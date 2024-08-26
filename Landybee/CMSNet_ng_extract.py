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
import timeit
from bramdybee import bramDB
from ConvSUDStoDict import SUDS2Dict
bramdb = bramDB()
conv = SUDS2Dict()


class cmsnet_extract:

    def __init__(self, domain: str) -> None:
        self.start_time = timeit.default_timer()
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

    def create_files(self, dhcp):  #does not necesarily need to be a function just needs to be created
        #generate the files
        #make sure previosu directory exists
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
    
    def process_normal_cases(self):
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
                    #if networkinterface card exists use the first one in the list if it does not exist fill in None
                    mac = fallback_networkinterfaces[0].get("HardwareAddress") if fallback_networkinterfaces else None
            else:
                #if interface is None then set all values to None before checking next interfaces
                netmask = default_gateway = ip_address = mac = None
            return ip_address, mac, netmask, default_gateway

        def categorize_device(os_name, os_version, manufacturer):
            """Helper function to categorize devices."""
            if os_name == "WINDOWS" or "windows":
                group = 'dcs'
            elif os_version in cc8_versions:
                group = 'cc8'
            elif manufacturer == "JUNIPER" or "juniper":
                group = 'juniper'
            else:
                group = 'misc'
            self.devices_by_group[group].append(dev_name)
            return group

        self.devices_by_group = {group: [] for group in ['dcs', 'cc8', 'juniper', 'misc']}
        self.dhcp = {group: [] for group in ['dcs', 'cc8', 'juniper', 'misc']}
        cc8_versions = ['CC8', 'RHEL8', 'ALMA9', 'RHEL9', 'ALMA9']

        devices = self.domain_devices(self.domain)
        split_devices = self.split_list(devices, 200)

        for sub_devices in split_devices:
            device_info = bramdb.landb.getDeviceInfoArray(sub_devices)
            for single_devinfo in device_info:
                devinfo_dict = json.loads(conv.sobject_to_json(single_devinfo))
                dev_name = devinfo_dict.get("DeviceName")
                interfaces = devinfo_dict.get("Interfaces")

                # finding info for specific interfaces
                correct_IF = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.IF_domain)
                correct_cmsIF = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.cms_IF_domain)
                correct_ipmiIF = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.ipmi_IF_domain)

                ip_address, mac, netmask, default_gateway = get_interface_info(correct_IF, devinfo_dict.get("NetworkInterfaceCards"))

                # checks other interfaces if DEVICE_NAME + CERN.CH does not exist
                if not correct_IF:
                    if correct_cmsIF:
                        ip_address, mac, netmask, default_gateway = get_interface_info(correct_cmsIF, devinfo_dict.get("NetworkInterfaceCards"))
                    elif correct_ipmiIF:
                        ip_address, mac, netmask, default_gateway = get_interface_info(correct_ipmiIF, devinfo_dict.get("NetworkInterfaceCards"))
                    else:
                        hcpinfo = bramdb.landb.getHCPInfoArray([dev_name])
                        if len(hcpinfo) == 1:
                            hcp_dict = json.loads(conv.sobject_to_json(hcpinfo[0]))
                            ip_address = hcp_dict.get("IP")
                            mac = hcp_dict.get("HardwareAddress")
                            netmask = hcp_dict.get("Mask")
                            default_gateway = hcp_dict.get("GatewayAddress")
                        else:
                            print(f"WARNING device {dev_name} has hardware address that cannot be tracked down.")

                group = categorize_device(devinfo_dict.get("OperatingSystem").get("Name"), 
                                        devinfo_dict.get("OperatingSystem").get("Version"),
                                        devinfo_dict.get("Manufacturer"))

                self.add_dhcp(device_name=dev_name, ip=ip_address, mac=mac, subnetmask=netmask, def_gateway=default_gateway, group=group)

        self.create_files(self.dhcp)
        end_time = timeit.default_timer()
        runtime = end_time - self.start_time
        print(f"Process completed in {runtime:.2f} seconds")



    # def process_normal_cases(self):
    #     self.devices_by_group = {
    #     'dcs': [],
    #     'cc8': [],
    #     'juniper': [],
    #     'misc': []
    # }
    #     self.dhcp = {
    #     'dcs': [],
    #     'cc8': [],
    #     'juniper': [],
    #     'misc': []
    # }

    #     #cc8 versions condition list
    #     cc8_versions = ['CC8', 'RHEL8', 'ALMA9', 'RHEL9', 'ALMA9']

    #     #first we find all devices in domain
    #     devices = self.domain_devices(self.domain)

    #     #next we get info arrays for all devices in steps of 50
    #     split_devices = self.split_list(devices, 200)
    #     for sub_devices in split_devices:
    #         device_info = bramdb.landb.getDeviceInfoArray(sub_devices)
    #         for single_devinfo in device_info:
    #             #turn each suds object into usable dictionary
    #                 deviceinfo_str = conv.sobject_to_json(single_devinfo)
    #                 devinfo_dict = json.loads(deviceinfo_str)

    #                 #start defining all things needed to populate DHCP files
    #                 dev_name = devinfo_dict.get("DeviceName")
    #                 IF_name = dev_name + self.IF_domain
    #                 IFs = devinfo_dict.get("Interfaces")
    #                 correct_IF = self.find_dict_by_entry(IFs, 'Name', IF_name)
    #                 correct_cmsIF = self.find_dict_by_entry(IFs, 'Name', dev_name + self.cms_IF_domain)
    #                 correct_ipmiIF = self.find_dict_by_entry(IFs, 'Name', dev_name + self.ipmi_IF_domain)
    #                 os = devinfo_dict.get("OperatingSystem")
    #                 # print(correct_IF)

    #                 if correct_IF:
    #                     IPaddress = correct_IF.get("IPAddress")
    #                     boundinterface = correct_IF.get("BoundInterfaceCard")
    #                     if boundinterface is None:
    #                         interfacecards = devinfo_dict.get("NetworkInterfaceCards")
    #                         if interfacecards:
    #                             mac = interfacecards[0].get("HardwareAddress")
    #                             # if len(interfacecards) == 1:
    #                             #     mac = interfacecards[0].get("HardwareAddress")
    #                             # else:
    #                             #     print(f"WARNING device {dev_name} ignored, hardware address not able to specified.")
    #                             #     continue
    #                         else:
    #                             # print(f"NO HARDWARE ADDRESS present for device {dev_name}")
    #                             mac = None
    #                             # continue
    #                     else:
    #                         mac = boundinterface.get("HardwareAddress")

    #                     netmask = correct_IF.get("SubnetMask")
    #                     defaultgateway = correct_IF.get("DefaultGateway")
    #                         # print(defaultgateway)

    #                             #append the device names to each respective file
    #                     if os.get("Name") == "WINDOWS":
    #                         self.devices_by_group['dcs'].append(dev_name)
    #                         group = 'dcs'
    #                     elif os.get("Version") in cc8_versions:
    #                         self.devices_by_group['cc8'].append(dev_name)
    #                         group = 'cc8'
    #                     elif devinfo_dict.get("Manufacturer") == "JUNIPER":
    #                         self.devices_by_group['juniper'].append(dev_name)
    #                         group = 'juniper'
    #                     else:
    #                         self.devices_by_group['misc'].append(dev_name)
    #                         group = 'misc'

    #                 self.add_dhcp(device_name= dev_name, ip=IPaddress, mac=mac, subnetmask= netmask, def_gateway=defaultgateway,group= group) 

    #                 #for those devices where finding correct interface is not as trivial as device_name.CERN.CH
    #                 if not correct_IF:
    #                     #quick check if only 1 interface card then we just take mac from there
    #                     # interfacecards = devinfo_dict.get("NetworkInterfaceCards")
    #                     # if interfacecards:
    #                     #     if len(interfacecards) == 1:
    #                     #         mac = interfacecards[0].get("HardwareAddress")
    #                         # else:
    #                             #no simple interface card solution, we check for more complex interface names, first device_name--CMS.CERN.CH   
    #                     if correct_cmsIF:
    #                         netmask = correct_cmsIF.get("SubnetMask")
    #                         defaultgateway = correct_cmsIF.get("DefaultGateway")
    #                         IPaddress = correct_cmsIF.get("IPAddress")

    #                         boundinterface = correct_cmsIF.get("BoundInterfaceCard")
    #                         if boundinterface:
    #                             mac = boundinterface.get("HardwareAddress")
                               
    #                         else:
    #                             interfacecards = devinfo_dict.get("NetworkInterfaceCards")
    #                             if interfacecards:
    #                                 mac = interfacecards[0].get("HardwareAddress")
    #                                 # if len(interfacecards) == 1:
    #                                 #     mac = interfacecards[0].get("HardwareAddress")
    #                                 # else:
    #                                 #     print(f"WARNING device {dev_name} ignored, hardware address not able to specified in extra check.")
    #                                 #     continue
    #                             else:
    #                                 print(f"NO HARDWARE ADDRESS present for device {dev_name}")
    #                                 mac = None
                                

                            
    #                     #next check for interface device_name-IPMI--CMS.CERN.CH
    #                     elif correct_ipmiIF:
    #                         netmask = correct_ipmiIF.get("SubnetMask")
    #                         defaultgateway = correct_ipmiIF.get("DefaultGateway")
    #                         IPaddress = correct_ipmiIF.get("IPAddress")

    #                         boundinterface = correct_ipmiIF.get("BoundInterfaceCard")
    #                         if boundinterface:
    #                             mac = boundinterface.get("HardwareAddress")

    #                         else:
    #                             interfacecards = devinfo_dict.get("NetworkInterfaceCards")
    #                             if interfacecards:
    #                                 mac = interfacecards[0].get("HardwareAddress")
    #                                 # if len(interfacecards) == 1:
    #                                 #     mac = interfacecards[0].get("HardwareAddress")
    #                                 # else:
    #                                 #     print(f"WARNING device {dev_name} ignored, hardware address not able to specified in extra check.")
    #                                 #     continue
    #                             else:
    #                                 mac = None

                                    
    #                     #last attempt if no matching interfaces found and only 1 interface card is present we can obtain          
    #                     else:
    #                         # check for single HCP info, if so all the info can be taken from there (might be scrapped might give much longer run time)
    #                         hcpinfo = bramdb.landb.getHCPInfoArray([dev_name])
    #                         hcp_str = conv.sobject_to_json(hcpinfo[0])
    #                         hcp_dict = json.loads(hcp_str)
    #                         if len(hcpinfo) == 1:
    #                             mac = hcp_dict.get("HardwareAddress")
    #                             IPaddress = hcp_dict.get("IP")
    #                             netmask = hcp_dict.get("Mask")
    #                             defaultgateway = hcp_dict.get("GatewayAddress")
    #                         else:
    #                             print(f"WARNING device {dev_name} has hardware address that cannot be tracked down.")
                                

    #                         #append the devicenames to each respective file
    #                         if os.get("Name") == "WINDOWS":
    #                             self.devices_by_group['dcs'].append(dev_name)
    #                             group = 'dcs'
    #                         elif os.get("Version") in cc8_versions:
    #                             self.devices_by_group['cc8'].append(dev_name)
    #                             group = 'cc8'
    #                         elif devinfo_dict.get("Manufacturer") == "JUNIPER":
    #                             self.devices_by_group['juniper'].append(dev_name)
    #                             group = 'juniper'
    #                         else:
    #                             self.devices_by_group['misc'].append(dev_name)
    #                             group = 'misc'

    #                     self.add_dhcp(device_name= dev_name, ip=IPaddress, mac=mac, subnetmask= netmask, def_gateway=defaultgateway,group= group) 

    #     self.create_files(self.dhcp)


    def broadcast_address(self, mask, ip):
        if mask is not None and ip is not None:
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