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
import pandas as pd
import time
from bramdybee import bramDB
from ConvSUDStoDict import SUDS2Dict
bramdb = bramDB()
conv = SUDS2Dict()


class cmsnet_extract:

    def __init__(self, domain: str) -> None:

        #read alias csv file for CNAME DNS entries
        file_aliasescsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/cms', 'aliases2.csv'))
        self.aliasescsvfile = pd.read_csv(file_aliasescsv, comment='#')


        #IP ranges that select the correct zones for the reverse IP lookup
        ip_ranges_cms = ("10.176.", "10.184.32.")
        ip_ranges_904 = ("10.192.")

        #some formatting
        self.domain = domain.upper()
        self.domainlow = domain.lower()

        #domains, in future --cms to be changed
        self.IF_domain = ".CERN.CH"
        self.cms_IF_domain = "--CMS" + self.IF_domain
        self.ipmi_IF_domain = '-IPMI' + self.cms_IF_domain
        self.ninezerofour_domain = '--904'

        domains = ("cms", "cms904")

        self.allowed_subdomains = ["cdrs0v0", "cdrs1v0", "cms", "d3vcdrs0", "d3vfbs1v0", "d3vfus0", "d3vfus1", "d3vfus3", "d3vrbs1v0", "d3vsms1v0",
                                   "daq2dqms0v0", "daq2fus10v0", "daq2fus11v0", "daq2fus12v0", "daq2fus13v0", "daq2fus14v0", "daq2fus15v0", "daq2fus16v0",
                                    "daq2fus17v0", "daq2fus18v0", "daq2fus19v0", "daq2fus20v0", "daq2fus21v0", "daq2fus22v0", "daq2fus35v0", "daq2fus36v0",
                                    "daq2fus37v0", "daq2fus38v0", "daq2fus39v0", "daq2fus40v0", "daq2fus41v0", "daq2fus42v0", "daq2fus43v0", "daq2fus44v0",
                                    "daq2fus4v0", "daq2fus8v0", "daq2fus9v0", "daq2sms1v0", "dvfbs2v0", "dvsms2v0", "ebs0", "ebs0v0", "ebs1", "fbs0v0",
                                    "fus0", "fus23", "fus24", "fus25", "fus26", "fus27", "fus28", "gemec1", "gemec2", "ipmi", "lcgp5", "utca01", "utca02",
                                    "utca03", "utca04", "utca05", "utca10", "utca11"]
        self.dhcp = []

        domainlength = len(self.domain_devices(domain= self.domain))

        #check whether domain given is valid, if not give valid one.
        if domain not in domains:
            print(f"The domain specified {domain} is not a valid domain. Valid domains are: {domains}")
            exit()
        else:
            print(f"Domain {domain} is valid and contains {domainlength} devices.")

    #obtain a list of all devices within cms or cms904 (depending on what selected)
    def domain_devices(self, domain):
        dmn_dict = {"Domain": domain}
        try:
            domain_list = bramdb.landb.searchDevice(dmn_dict)
        except Exception as e:
            print(f"ERROR obtaining list of device names from domain {domain}: {e}")
        return domain_list
    
    #tool to find a dictionary within a list based on one of its entries
    def find_dict_by_entry(self, dict_list, key, value):
        for d in dict_list:
            if d is not None:
                dict_value = d.get(key)
                if value is None and dict_value is None:
                    return None
                elif isinstance(dict_value, str) and isinstance(value, str) and dict_value.upper() == value.upper():
                    return d
        return None


    #creating the dhcp, dns files.
    def create_files(self, subdomain_dict, zone_dict, alias_dict):
        #remove build diretory so we can start with a new one
        shutil.rmtree("build", ignore_errors=True)

        #generate directories
        os.makedirs("build/var/dhcp/", exist_ok=True)
        os.makedirs("build/var/named/master/", exist_ok=True)

        for i, dhcp_entries in self.dhcp.items():
            filepath = f"build/var/dhcp/{self.domainlow}.{i}.dhcp"
            with open(filepath, "w") as dhcp_fh:
                for entry in dhcp_entries:
                    dhcp_fh.write(entry)
                print(f"File {filepath} created.")


        #write dns files, currently include 
        for subdomain in subdomain_dict.keys():
            sub_domain_file = f"build/var/named/master/{subdomain}.{self.domainlow}"
            
            # For CMS file we don't want cms.cms
            if subdomain == self.domainlow:
                sub_domain_file = f"build/var/named/master/{subdomain}"
            
            # Begin to write info into file
            try:
                with open(sub_domain_file, 'w') as file:
                    # Write zone header and static info
                    file.write(self.read_zone_header())
                    
                    if subdomain == self.domainlow:
                        file.write(self.read_static_info())
                        file.write("\n")
                        file.write(self.read_rr_alias())
                        file.write("\n")
                    
                    # Write devices from the device to ip dictionary
                    
                    
                    for name, ip in subdomain_dict[subdomain]:
                        file.write(f"{name}\t\tIN\tA\t{ip}\n")
                    
                    # Write devices from the alias dictionary
                    for name, alias in alias_dict[subdomain]:
                        file.write(f"{alias}\t\t\tCNAME\t{name}\n")

                    print(f"File {sub_domain_file} created.")

            except IOError as e:
                print(f"Can't open main zone file: {str(e)}")


        #write reverseip files
        for zone, elements in zone_dict.items():
            zone_reverseip_file = f"build/var/named/master/{zone}.in-addr.arpa"
            
            #begin to write info into file
            try:
                with open(zone_reverseip_file, 'w') as file:

                    #write zone header and static info
                    file.write(self.read_zone_header())
                    
                    #input reverse IP to device
                    for revIP, interface in elements:
                        file.write(f"{revIP}\t\t\t\t\tPTR\t{interface}\n")
                    print(f"File {zone_reverseip_file} created.")

            except IOError as e:
                print(f"Can't open zone file: {str(e)}")

    #tool to split list of devices in domain into smaller parts
    def split_list(self, lst, section_length):
        return [lst[i:i + section_length] for i in range(0, len(lst), section_length)]
    

    #dns zone header read from dns_header.txt
    def read_zone_header(self):
        zone_header = ""
        date  = int(time.time())    
        zone_header_path = "data/cms/dns_header.txt"
        
        try:
            with open(zone_header_path, 'r') as file:
                for line in file:
                    if "; Serial" in line:
                        # Replace the line containing "; Serial" with the desired format
                        zone_header += f"\t\t\t\t\t{date}\t; Serial\n"
                    else:
                        # Append the original line
                        zone_header += line
            zone_header += "\n"
        
        except IOError as e:
            print(f"Could not open zone header file {zone_header_path} for domain {self.domain}: {str(e)}")
        
        return zone_header
    
    #dns static info read from dns_main_zone_static.txt
    def read_static_info(self):
        static_info = ""
        static_info_path = "data/cms/dns_main_zone_static.txt"
        try:
            with open(static_info_path, 'r') as staticfile:
                for line in staticfile:
                    static_info += line
            

        except Exception as e:
            print(f"ERROR opening file {static_info_path}")
        return static_info
    
    #read dns_rr_alias.txt added only to cms dns zone file
    def read_rr_alias(self):
        rr_alias = ""
        alias_path = "data/cms/dns_rr_alias.txt"
        try:
            with open(alias_path, 'r') as aliasfile:
                for line in aliasfile:
                    rr_alias += line
            

        except Exception as e:
            print(f"ERROR opening file {alias_path}")
        return rr_alias

    
    #long fucntion to generate all the data for the dhcp, dns files
    #In essence what the function does:
    #- For DHCP:
    #-- Search each device for a 'trivial' device interface names,
    #   if the interface has a bound network interface card it obtains mac address,
    #-- it does the same for ipmi interfaces, 
    #-- optional(if there is no trivial interface then it checks for the number of interface cards,
    #           if there is only 1 NIC it uses the mac address from that)
    #
    #- For DNS:
    #-- create dictionary for each, device to ip, reverse ip lookup and cname
    #-- the key for every dictionary is the zone/subdomain and the elements of the key are pairs (tuples)
    #   for example: device to ip: {subdomain_1:[(device1, ip1),(device2, ip2),(device3, ip3)], subdomain_2: [(device4, ip4), ...]...}
    #   using the dictionaries the data is written into the files
    def populate(self):
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
                            mac = fallback_networkinterfaces[0].get("HardwareAddress")
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


        #categorize devices based on conditions below, easily able to be changed 
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
        
        def reverse_ip(ip_address):
            #split IP into 4 at the dot
            quarters = ip_address.split(".")

            reversed_ip = f"{quarters[3]}.{quarters[2]}"

            zone = f"{quarters[1]}.{quarters[0]}"

            return zone, reversed_ip

        
        start_time = time.time()

        self.devices_by_group = {group: [] for group in ['dcs', 'cc8', 'juniper', 'misc', 'misc-ipmi']}
        self.dhcp = {group: [] for group in ['dcs', 'cc8', 'juniper', 'misc', 'misc-ipmi']}
        cc8_versions = {'CC8', 'RHEL8', 'ALMA9', 'RHEL9', 'ALMA9'}

        devices = self.domain_devices(self.domain)
        split_devices = self.split_list(devices, 200)
        subdomain_dict = {}
        zone_dict = {}
        subdomain_alias_dict = {}

        for sub_devices in split_devices:
            device_info = bramdb.landb.getDeviceInfoArray(sub_devices)
            for single_devinfo in device_info:
                devinfo_dict = json.loads(conv.sobject_to_json(single_devinfo))

                '''Whether or not routers are taken into account for dhcp config files, cms.juniper.dhcp contains then'''
                #we ignore routers or switch for DHCP config files
                if devinfo_dict.get("GenericType") not in ["VIRTUAL-GATEWAY"]:
                    os = devinfo_dict.get("OperatingSystem")
                    manufacturer = devinfo_dict.get("Manufacturer")
                    dev_name = devinfo_dict.get("DeviceName")
                    interfaces = devinfo_dict.get("Interfaces")
                    interfacecards = devinfo_dict.get("NetworkInterfaceCards")

                    #populate subdomain list for dns zone files
                    for interface in interfaces:
                        pattern = re.compile(r'([^-]+)(?:-([^-]+))?' + re.escape(self.cms_IF_domain), re.IGNORECASE)
                        interface_name = interface.get("Name")
                        IPadd = interface.get("IPAddress")


                        #get reverse IP address and zone in which it exists
                        zone, ipreverse = reverse_ip(IPadd)
                        #now for each interface we obtain alias form IPaliases section
                        

                        #initialise alias variable
                        alias = None

                        #once aliases transferred to lanDB this section can be commented out
                        if not alias:
                            alias_devices = self.aliasescsvfile['<FQN of target>'].str.strip().str.lower()
                            dev_name_lower = dev_name.strip().lower()
                            if dev_name_lower in alias_devices.values:
                                alias_row = self.aliasescsvfile[self.aliasescsvfile['<FQN of target>'].str.strip().str.lower() == dev_name_lower]
                                alias = alias_row['<name>'].values[0]

                        if not alias:    
                            alias = interface.get("IPAliases")
                            
                        if zone not in zone_dict:
                            zone_dict[zone] = []
                        zone_dict[zone].append((ipreverse, interface_name))
                    

                        devlower = str(interface_name).lower()
                        #remove --cms from end of each entry
                        if devlower.endswith(self.cms_IF_domain):
                            devlower = devlower[:-13]
                        if devlower.endswith(self.ninezerofour_domain + self.IF_domain):
                            devlower = devlower[:-13]
                        if devlower.endswith(self.IF_domain):
                            devlower = devlower[:-8]
                        
                        match = pattern.search(interface_name)
                        if match:
                            subdomain = str(match.group(2)).lower() if match.group(2) else None
                            if subdomain:
                                if len(str(subdomain)) < 4:
                                    subdomain = None

                            if subdomain is None:
                                subdomain = "cms"

                            if subdomain not in self.allowed_subdomains:
                               subdomain == 'cms' 

                            if subdomain not in subdomain_dict:
                                subdomain_dict[subdomain] = []

                            subdomain_dict[subdomain].append((devlower, IPadd))

                            if subdomain not in subdomain_alias_dict:
                                subdomain_alias_dict[subdomain] = []

                            if alias:
                                subdomain_alias_dict[subdomain].append((devlower, alias))
                        else:
                            try:
                                pattern2 = re.compile(r'([^.]+)' + re.escape(self.IF_domain), re.IGNORECASE)
                                match = pattern2.search(interface_name)
                                if match:
                                    # print(f"Pattern2 matched: {match.group(1)}")
                                    subdomain = str("cms")

                                    if subdomain not in subdomain_dict:
                                        subdomain_dict[subdomain] = []
                                    
                                    subdomain_dict[subdomain].append((devlower, IPadd))

                                    if subdomain not in subdomain_alias_dict:
                                        subdomain_alias_dict[subdomain] = []

                                    if alias:
                                        subdomain_alias_dict[subdomain].append((devlower, alias))
                                
                                else:
                                    print(f"Interface {interface_name} has no match.")

                            except Exception as e:
                                print(f"Interface {interface_name} does not match the criteria: {e}")
                        
                
                    #ipmi interfaces checked first and pushed into misc-ipmi.dhcp file
                    ipmi_interface = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.ipmi_IF_domain)
                    if ipmi_interface:
                        ip_address, mac, netmask, default_gateway = get_interface_info(ipmi_interface, interfacecards)
                        if ip_address and mac and netmask and default_gateway:
                            self.add_dhcp(device_name=dev_name +'-ipmi', ip=ip_address, mac=mac, subnetmask=netmask, def_gateway=default_gateway, group='misc-ipmi')
                        else:
                            print(f"Ipmi interface {dev_name + self.ipmi_IF_domain} not added to DHCP as it has missing entries (probably no bound interface).")

                    # search for main interface --CMS.CERN.CH
                    primary_interface = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.cms_IF_domain)
                    ip_address, mac, netmask, default_gateway = get_interface_info(primary_interface, interfacecards)

                    # if no main trivial interface fallback onto .CERN.CH
                    if not ip_address and not mac:
                        cms_interface = self.find_dict_by_entry(interfaces, 'Name', dev_name + self.IF_domain)
                        ip_address, mac, netmask, default_gateway = get_interface_info(cms_interface, interfacecards)
                    

                    # Fallback to HCP info if all interface checks fail
                    # if not ip_address and not mac:
                    #     type = devinfo_dict.get("GenericType")
                    #     print(f"ignored {dev_name}, type {type}")

                    '''Used as a final attempt, if the device has a single DHCP netry we use that, otherwise we cant determine what it is, requires extra call to lanDB though'''
                    # hcpinfo = bramdb.landb.getHCPInfoArray([dev_name])
                    # if hcpinfo:
                    #     if len(hcpinfo) == 1:
                    #         hcp_dict = json.loads(conv.sobject_to_json(hcpinfo[0]))  #again to be changed
                    #         ip_address = hcp_dict.get("IP")
                    #         mac = hcp_dict.get("HardwareAddress")
                    #         netmask = hcp_dict.get("Mask")
                    #         default_gateway = hcp_dict.get("GatewayAddress")
                    #     else:
                    #         print(f"Not able to specify interface or hardware address for device {dev_name}")
                    #         netmask = default_gateway = ip_address = mac = None
                    #         continue
                    # else:
                    #     netmask = default_gateway = ip_address = mac = None
                    #     continue

                    # Check if all required information is present
                    # Categorize the device and add DHCP information
                    if ip_address and mac and netmask and default_gateway:
                     
                        
                        # Categorize the device
                        group = categorize_device(os, manufacturer, devinfo_dict)
                        
                        # Add the device to the DHCP configuration
                        self.add_dhcp(device_name=dev_name, ip=ip_address, mac=mac, subnetmask=netmask, def_gateway=default_gateway, group=group)
                    else:
                        print(f"WARNING: Device {dev_name} not added to DHCP as it has missing entries.")
                        continue
                
        
        self.create_files(subdomain_dict, zone_dict, subdomain_alias_dict)

        end_time = time.time()
        runtime = end_time - start_time
        print(f"Succesfully generated DHCP files.")
        print(f"Process completed in {runtime:.2f} seconds")


    #generate broadcast address
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

        # Check if the device name ends with '--cms'
        dev_name_lower = str(device_name).lower()
        if dev_name_lower.endswith(self.cms_IF_domain.lower()):
            dev_nocms = dev_name_lower[:-5]  # Strip off '--cms'
        elif dev_name_lower.endswith(self.ninezerofour_domain):
            dev_nocms = dev_name_lower[:-5]  # Strip off '--904'
        else:
            dev_nocms = dev_name_lower  # If not, use the original device name

        #generate broadcast address
        broadcast = self.broadcast_address(subnetmask, ip)

        dhcp_entry = (
            f"host {dev_nocms} {{ hardware ethernet {mac}; fixed-address {ip}; "
            f"option host-name {dev_nocms}; option subnet-mask {subnetmask}; "
            f"option broadcast-address {broadcast}; option routers {def_gateway}; }}\n"
        )

        if group in self.dhcp:
            self.dhcp[group].append(dhcp_entry)
        else:
            self.dhcp[group] = [dhcp_entry]


def commandline():
    parser = argparse.ArgumentParser(description= "Extract DNS and DHCP files from devices in a given domain. Format: python3.11 CMSNet_ng_extract.py domain --function")
    parser.add_argument('domain', type=str, help= 'Name of the domain to retreive DHCP and DNS configurations from.')
    parser.add_argument('--extract', action='store_true', help='Extract dhcp and dns configuratiopns from devices in domain.')

    args = parser.parse_args()
    cmsnet = cmsnet_extract(args.domain)

    if args.extract:
        cmsnet.populate()


if __name__ == "__main__":
    commandline()