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
from bramdybee import bramDB
from ConvSUDStoDict import SUDS2Dict
bramdb = bramDB()
conv = SUDS2Dict()


class cmsnet_extract:

    def __init__(self, domain: str) -> None:
        
        ip_ranges_cms = ("10.176.", "10.184.32.")
        ip_ranges_904 = ("10.192.")
        self.domain = domain.upper()
        self.cmsIF_domain = ".CERN.CH"

        domains = ("cms", "cms904")

        self.dhcp = []

        #check whether domain given is valid, if not give valid one.
        if domain not in domains:
            print(f"The domain specified {domain} is not a valid domain. Valid domains are: {domains}")
            exit()

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
                    dhcp_fh.write(entry + "\n")
                print(f"File {i} created.")
    
    def split_list(self, lst, section_length):
        return [lst[i:i + section_length] for i in range(0, len(lst), section_length)]

    def process_normal_cases(self):
        self.devices_by_group = {
        'dcs': [],
        'cc8': [],
        'juniper': [],
        'misc': []
    }
        self.dhcp = {
        'dcs': [],
        'cc8': [],
        'juniper': [],
        'misc': []
    }

        #cc8 versions condition list
        cc8_versions = ['CC8', 'RHEL8', 'ALMA9', 'RHEL9', 'ALMA9']

        #first we find all devices in domain
        devices = self.domain_devices(self.domain)

        #next we get info arrays for all devices in steps of 50
        split_devices = self.split_list(devices, 200)

        for sub_devices in split_devices:
            try:
                device_info = bramdb.landb.getDeviceInfoArray(sub_devices)
                for single_devinfo in device_info:
                    #turn each suds object into usable dictionary
                    deviceinfo_str = conv.sobject_to_json(single_devinfo)
                    devinfo_dict = json.loads(deviceinfo_str)

                    #start defining all things needed to populate DHCP files
                    dev_name = devinfo_dict.get("DeviceName")
                    IF_name = dev_name + self.cmsIF_domain
                    IFs = devinfo_dict.get("Interfaces")
                    correct_IF = self.find_dict_by_entry(IFs, 'Name', IF_name)
                    os = devinfo_dict.get("OperatingSystem")
                    # print(correct_IF)

                    if correct_IF:
                        IPaddress = correct_IF.get("IPAddress")
                        boundinterface = correct_IF.get("BoundInterfaceCard")
                        if boundinterface is None:
                            print(f"Device {dev_name} ignored, no hardware address present.")
                            continue
                        else:
                            mac = boundinterface.get("HardwareAddress")
                            netmask = correct_IF.get("SubnetMask")
                            # print(netmask)
                            defaultgateway = correct_IF.get("DefaultGateway")
                            # print(defaultgateway)

                            #append the device names to each respective file
                            if os.get("Name") == "WINDOWS":
                                self.devices_by_group['dcs'].append(dev_name)
                                group = 'dcs'
                            elif os.get("Version") in cc8_versions:
                                self.devices_by_group['cc8'].append(dev_name)
                                group = 'cc8'
                            elif devinfo_dict.get("Manufacturer") == "JUNIPER":
                                self.devices_by_group['juniper'].append(dev_name)
                                group = 'juniper'
                            else:
                                self.devices_by_group['misc'].append(dev_name)
                                group = 'misc'
                    # else:
                    #     print(dev_name)
                    #     IPaddress = mac = netmask = defaultgateway = None
                    try:
                        self.add_dhcp(dev_name, IPaddress, mac,  netmask, defaultgateway, group) 
                    except Exception as e:
                        print(f"ERROR creating dhcp format: {e}")                   
                    
            except Exception as e:
                print(f"ERROR getting device info: {e}")

        print("self.devices_by_group created")

        self.create_files(self.dhcp)


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

    def add_dhcp(self, device_name, ip, mac, subnetmask, def_gateway, group):
        if not all([device_name, ip, mac, subnetmask, def_gateway]):
            print(f"Skipping DHCP entry for {device_name} due to missing information.")
            return

        mac = mac.replace('.', ':').replace('-', ':')
        broadcast = self.broadcast_address(subnetmask, ip)

        dhcp_entry = (
            f"host {device_name} {{ hardware ethernet {mac}; fixed-address {ip}; "
            f"option host-name {device_name}; option subnet-mask {subnetmask}; "
            f"option broadcast-address {broadcast}; option routers {def_gateway}; }}\n"
        )

        if group in self.dhcp:
            self.dhcp[group].append(dhcp_entry)
        else:
            self.dhcp[group] = [dhcp_entry]