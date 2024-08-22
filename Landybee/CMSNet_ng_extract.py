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



class cmsnet_extract:

    def __init__(self, domain) -> None:
        
        ip_ranges_cms = ("10.176.", "10.184.32.")
        ip_ranges_904 = ("10.192.")
        self.domain = domain

        domains = ("cms", "cms904")

        #check whether domain given is valid, if not give valid one.
        if domain not in domains:
            print(f"The domain specified {domain} is not a valid domain. Valid domains are: {domains}")
            exit()


    def create_files(self, dhcp):  #does not necesarily need to be a function just needs to be created
        #generate the files
        #make sure previosu directory exists
        shutil.rmtree("build", ignore_errors=True)

        #write dhcp file
        os.makedirs("build/var/dhcp/", exist_ok=True)

        for i in sorted(dhcp.keys()):
            with open(f"build.var/dhcp/{self.domain}.{i}.dhcp", "w") as dhcp_fh:
                dhcp_fh.write(dhcp[i])



    def broadcast_address(self, mask, def_gateway, ip):
        if mask is not None and def_gateway is not None and ip is not None:
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

    def add_dhcp(self, device_name, IP, MAC, group, netmask, broadcast, def_gateway, dhcp):
        entries = [device_name, IP, MAC, group, netmask, broadcast, def_gateway]
        if any(arg is None for arg in entries):
            print("Missing arguments in: 'add_dhcp'")
            return

        mac = mac.replace('.', ':').replace('-', ':')
        broadcast = self.broadcast_address(mask=netmask, 
                                           def_gateway=def_gateway,
                                           ip= IP)

        if group in dhcp and f"host {device_name}" in dhcp[group]:
            print(f"Cannot add DHCP for {device_name}: entry already exists.")
        else:
            print(f"Add DHCP: {device_name}: {IP}: {mac} (group: {group})")

            dhcp_entry = (f"host {device_name} {{ hardware ethernet {mac}; fixed-address {IP}; "
                      f"option host-name {device_name}; option subnet-mask {netmask}; "
                      f"option broadcast-address {broadcast}; option routers {def_gateway}; }}\n")
            if group in dhcp:
                dhcp[group] += dhcp_entry
            else:
                dhcp[group] = dhcp_entry