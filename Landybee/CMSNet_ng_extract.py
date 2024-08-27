'''
Plan for extract funtion:
-it needs to populate the DNS and DHCP files

for dchp:
-generate fucntion add_dhcp which populates a dhcp point
-- must contain, name, hardware ethernet, fixed address IP, host-name, subnet mask, broadcaist address, routers (defualt gateway)
'''
import os
import shutil
import re
import json
import argparse
import time
from bramdybee import bramDB
from ConvSUDStoDict import SUDS2Dict
bramdb = bramDB()
conv = SUDS2Dict()


class cmsnet_extract:

    def __init__(self, domain: str) -> None:

        ip_ranges_cms = ("10.176.", "10.184.32.")
        ip_ranges_904 = ("10.192.")
        self.domain = domain.upper()
        self.IF_domain = ".CERN.CH"
        self.cms_IF_domain = "--CMS.CERN.CH"
        self.ipmi_IF_domain = '-IPMI' + self.cms_IF_domain

        domains = ("cms", "cms904")

        self.dhcp = []

        domainlength = len(self.domain_devices(domain))

        #check whether domain given is valid, if not give valid one.
        if domain not in domains:
            print(f"The domain specified {domain} is not a valid domain. Valid domains are: {domains}")
            exit()
        else:
            print(f"Domain {domain} is valid and contains {domainlength} devices.")

    def domain_devices(self, domain):
        dmn_dict = {"Domain": domain}
        try:
            domain_list = bramdb.landb.searchDevice(dmn_dict)
        except Exception as e:
            print(f"ERROR obtaining list of device names from domain {domain}")
        return domain_list
    
    def find_dict_by_entry(self, dict_list, key, value):
        for d in dict_list:
        # Ensure that d is not None and the key exists in the dictionary
            if d is not None:
                dict_value = d.get(key)
                if value is None and dict_value is None:
                    return None
                elif isinstance(dict_value, str) and isinstance(value, str) and dict_value.upper() == value.upper():
                    return d
        return None

    def create_files(self, dhcp):
        #generate the files

        shutil.rmtree("build", ignore_errors=True)

        #write dhcp file
        os.makedirs("build/var/dhcp/", exist_ok=True)

        for i, dhcp_entries in dhcp.items():
            filepath = f"build/var/dhcp/{self.domain}.{i}.dhcp"
            with open(filepath, "w") as dhcp_fh:
                for entry in dhcp_entries:
                    dhcp_fh.write(entry)
                print(f"File {filepath} created.")


    def split_list(self, lst, section_length):
        return [lst[i:i + section_length] for i in range(0, len(lst), section_length)]
    
    def populate_DHCP(self):
        def get_interface_info(interface, fallback_networkinterfaces):
            """Helper function to extract IP, MAC, netmask, and gateway info."""
            if interface:
                netmask = interface.get("SubnetMask")
                default_gateway = interface.get("DefaultGateway")
                ip_address = interface.get("IPAddress")
                bound_interface = interface.get("BoundInterfaceCard")
                if bound_interface:
                    mac = bound_interface.get("HardwareAddress")
                else:
                    if fallback_networkinterfaces:
                        #if networkinterface card exists use the first one in the list if it does not exist fill in None
                        if len(fallback_networkinterfaces) == 1:
                            mac = fallback_networkinterfaces[0].get("HardwareAddress") #to be chnaged
                        else:
                            # mac = fallback_networkinterfaces[0].get("HardwareAddress") if fallback_networkinterfaces else None   #to be changed
                            print(f"No specific hardware address able to be found for device {dev_name}")
                            mac=None
                    else:
                        print(f"No hardware address present for device {dev_name}")
                        mac = None
            else:
                #if interface is None then set all values to None before checking next interfaces
                netmask = default_gateway = ip_address = mac = None
            return ip_address, mac, netmask, default_gateway

        def categorize_device(os, manufacturer, devinfo_dict):
            """Helper function to categorize devices."""
            os_name = os.get("Name")
            os_version = os.get("Version")
            device_name = devinfo_dict.get("DeviceName")

            if "WINDOWS" in os_name:
                group = 'dcs'
            elif os_version in cc8_versions:
                group = 'cc8'
            elif "JUNIPER" in manufacturer:
                group = 'juniper'
            else:
                group = 'misc'
            self.devices_by_group[group].append(device_name)
            return group
        
        start_time = time.time()

        self.devices_by_group = {group: [] for group in ['dcs', 'cc8', 'juniper', 'misc', 'misc-ipmi']}
        self.dhcp = {group: [] for group in ['dcs', 'cc8', 'juniper', 'misc', 'misc-ipmi']}
        cc8_versions = {'CC8', 'RHEL8', 'ALMA9', 'RHEL9', 'ALMA9'}

        devices = self.domain_devices(self.domain)
        split_devices = self.split_list(devices, 200)

        for sub_devices in split_devices:
            device_info = bramdb.landb.getDeviceInfoArray(sub_devices)
            for single_devinfo in device_info:
                devinfo_dict = json.loads(conv.sobject_to_json(single_devinfo))
                os = devinfo_dict.get("OperatingSystem")
                manufacturer = devinfo_dict.get("Manufacturer")
                dev_name = devinfo_dict.get("DeviceName")
                interfaces = devinfo_dict.get("Interfaces")
                interfacecards = devinfo_dict.get("NetworkInterfaceCards")

                ipmi_interface = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.ipmi_IF_domain)
                if ipmi_interface:
                    ip_address, mac, netmask, default_gateway = get_interface_info(ipmi_interface, interfacecards)
                    if ip_address and mac and netmask and default_gateway:
                        self.add_dhcp(device_name=dev_name +'-ipmi', ip=ip_address, mac=mac, subnetmask=netmask, def_gateway=default_gateway, group='misc-ipmi')
                    else:
                        print(f"Ipmi interface {dev_name + self.ipmi_IF_domain} not added to DHCP as it has missing entries.")

                # search for main interface
                primary_interface = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.IF_domain)
                ip_address, mac, netmask, default_gateway = get_interface_info(primary_interface, interfacecards)

                # if no main trivial interface obtain potential --CMS.CERN.CH
                if not ip_address and not mac:
                    cms_interface = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.cms_IF_domain)
                    ip_address, mac, netmask, default_gateway = get_interface_info(cms_interface, interfacecards)

                # Fallback to HCP info if all interface checks fail
                if not ip_address and not mac:
                    hcpinfo = bramdb.landb.getHCPInfoArray([dev_name])
                    if hcpinfo:
                        if len(hcpinfo) == 1:
                            hcp_dict = json.loads(conv.sobject_to_json(hcpinfo[0]))  #again to be changed
                            ip_address = hcp_dict.get("IP")
                            mac = hcp_dict.get("HardwareAddress")
                            netmask = hcp_dict.get("Mask")
                            default_gateway = hcp_dict.get("GatewayAddress")
                        else:
                            print(f"Not able to specify interface or hardware address for device {dev_name}")
                            netmask = default_gateway = ip_address = mac = None
                    else:
                        print(f"WARNING: Device {dev_name} has a hardware address that cannot be tracked down.")
                        netmask = default_gateway = ip_address = mac = None


                # Categorize the device and add DHCP information
                if ip_address and mac and netmask and default_gateway:
                    group = categorize_device(os, manufacturer, devinfo_dict)
                    self.add_dhcp(device_name=dev_name, ip=ip_address, mac=mac, subnetmask=netmask, def_gateway=default_gateway, group=group)
                else:
                    print(f"WARNING device {dev_name} not added to DHCP as it has missing entries")

        self.create_files(self.dhcp)

        end_time = time.time()  # End timing
        runtime = end_time - start_time
        print(f"Succesfully generated DHCP files.")
        print(f"Process completed in {runtime:.2f} seconds")



    def broadcast_address(self, mask, ip):
        if mask and ip:
                  # Splitting up netMask and IP address using regex
            match = re.match(r"(\d+)\.(\d+)\.(\d+)\.(\d+)\|(\d+)\.(\d+)\.(\d+)\.(\d+)", f"{mask}|{ip}")
            
            if match:
                ma, mb, mc, md = map(int, match.groups()[:4])
                aa, ab, ac, ad = map(int, match.groups()[4:])
                
                # Generation of broadcast address
                ba = ((aa & ma) | (~ma & 255)) & 255
                bb = ((ab & mb) | (~mb & 255)) & 255
                bc = ((ac & mc) | (~mc & 255)) & 255
                bd = ((ad & md) | (~md & 255)) & 255
                
                # Construct the broadcast address as a string
                broadcast = f"{ba}.{bb}.{bc}.{bd}"
                return broadcast
    
        return None  

    #might need to initialise dhcp outside the function populated by device names within groups within the domain

    def add_dhcp(self, device_name: str, ip, mac, subnetmask, def_gateway, group):
        if not all([device_name, ip, subnetmask, def_gateway]):
            print(f"Skipping DHCP entry for {device_name} due to missing information.")
            return

        #chnage hardware address formatting
        if mac:
            mac = mac.replace('.', ':').replace('-', ':')

        #generate broadcast address
        broadcast = self.broadcast_address(subnetmask, ip)

        dhcp_entry = (
            f"host {device_name.lower()} {{ hardware ethernet {mac}; fixed-address {ip}; "
            f"option host-name {device_name.lower()}; option subnet-mask {subnetmask}; "
            f"option broadcast-address {broadcast}; option routers {def_gateway}; }}\n"
        )

        if group in self.dhcp:
            self.dhcp[group].append(dhcp_entry)
        else:
            self.dhcp[group] = [dhcp_entry]