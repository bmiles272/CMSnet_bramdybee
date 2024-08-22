'''
plan:
- call in dicts converted from CSV files (DeviceInput, InterfaceCard, BulkInterface)
-add device class wil contain 3 different functions
-- deviceInsert --> requires DeviceInput dict
-- deviceAddCard --> requires InterfaceCard
-- deviceAddBulkInterface --> requires BulkInterface
- the fucntions will be callable seperately and should gives errors at each point if it fails
'''

from typing import Any
from CSVExtracttoDict import CSVtypes
import bramdybee
import ConvSUDStoDict
import argparse

#initiate any clases required
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()
s2d = ConvSUDStoDict.SUDS2Dict()
'''
When instance of class is called all 3 functions automatically are used. As if we used the bulkInsert function. 
However each function is also callable individually.
'''
class cmsnet_add:

    def __init__(self, device_name) -> None:
        #Call in dicts from CSVExtracttoDict
        self.device_input = extract_dict.DeviceInput(device_name)
        self.interface_card = extract_dict.InterfaceCard(device_name)
        self.bulk_interface = extract_dict.BulkInterface(device_name)
        self.device_name = device_name

        interfaces = extract_dict.interface_list(self.device_name)
        self.ipmi_interface_found = any('ipmi' in iface.lower() for iface in interfaces)
        self.ipmi_fullname = extract_dict.interfacenames(self.device_name + '.ipmi', self.device_name)



    def deviceInsert(self):
        if self.device_input is None:
            print(f"No device information in devices.csv for device {self.device_name}, stopping add process.")
            exit()

        else:
            try:
                bramdb.landb.deviceInsert(self.device_input)
                print(f"Successfully inserted device info for device {self.device_name}.")
            except Exception as e:
                print(f"There was an ERROR inserting the device info for device {self.device_name}: {e}")
                exit()
    
    def deviceAddCard(self):
        hardware_address = extract_dict.MACaddress(self.device_name)
        ipmicard = extract_dict.IPMIinterfacecard(self.device_name)

        if not self.interface_card:
            print('ERROR attaching interface card to device as the list of interface cards is empty.')
            return
        
        for card in self.interface_card:
            if card.get('HardwareAddress') is None:
                print(f"ERROR attaching interface card with missing hardware address for device {self.device_name}.")
                continue

            try:
                for card in self.interface_card:
                    bramdb.landb.deviceAddCard(self.device_name, card)
                    print(f"Successfully added Network Interface Card (NIC) for device {self.device_name}.")
            except Exception as e:
                print(f"There was an ERROR adding Network Interface Card (NIC) for device {self.device_name}: {e}")
        
        ipmimac = hardware_address.get("IPMIMAC")
        if ipmimac is not None:
            try:
                bramdb.landb.deviceAddCard(self.device_name, ipmicard)
                print(f"Successfully added IPMI Network Interface Card (NIC) for device {self.device_name}.")
            except Exception as e:
                print(f"There was an ERROR adding IPMI Network Interface Card (NIC) for device {self.device_name}: {e}")
        

    def deviceAddBulkInterface(self):
        hardware_address = extract_dict.MACaddress(self.device_name)
        for index, interface in enumerate(self.bulk_interface):
            IFName = interface.get("InterfaceName")
            switch_name = interface.get("SwitchName")
            switchnumber = interface.get("PortNumber")
            port_name = interface.get("PortNumber")

            try:
                #check switch information, of port is already in use we use a fanout.
                switch_info_list = bramdb.landb.getSwitchInfo(switch_name)
                switch_info = None

                for info in switch_info_list:
                    if info.Name == switchnumber:
                        switch_info = info
                        break

                if switch_info:
                    if switch_info.InUse == True:
                        print(f"Switch in use, turning switchport {switch_name} into a fanout...")
                        try:
                            fanout = bramdb.landb.enableFanOutFromSwitchPort(switch_name, port_name)
                            if fanout == True:
                                print(f"Fanout for switchport {switch_name} created succesfully.")
                        except Exception as fanout_error:
                            print(f"Fanout failed. Trying to continue as it could already be a fanout: {fanout_error}")
                else:
                    print(f"No switch info found for device name {self.device_name}.")

            except Exception as e:
                print(f"ERROR getting info for switch {switch_name}, for interface {IFName}: {e}")

            try:
                bramdb.landb.deviceAddBulkInterface(self.device_name, interface)
                print(f"Successfully added Interface {IFName} for device {self.device_name}.")
            except Exception as e:
                print(f"ERROR adding Bulk Interface {IFName} for device {self.device_name}: {e}")
            
            if index == 0:
                device_interface = interface

        #binds NIC to interface of device rather than extra ones as device interface will always be first one
        if device_interface:
            IFName = device_interface.get("InterfaceName")
            if hardware_address is not None:
                try:
                    macaddress = hardware_address.get('OnboardMAC1') or hardware_address.get('OnboardMAC2')
                    if macaddress:
                        bind = bramdb.landb.bindUnbindInterface(IFName, macaddress)
                        if bind:
                            print(f"Interface {IFName} successfully bound to hardware address {macaddress}.")
                        else:
                            print(f"Failed to bind interface {IFName} to hardware address {macaddress}.")
                    else:
                        print(f"No valid MAC address found for interface {IFName}.")
                except Exception as e:
                    print(f"ERROR binding interface {IFName} to {macaddress}: {e}")
            else:
                print("Hardware address information is not available. Skipping binding.")
        
        #generate IPMI interfaces for a device that has non-zero IPMIMAC

        if not self.ipmi_interface_found:
            if hardware_address is not None:
                ipmimac = hardware_address.get("IPMIMAC")
                if ipmimac is not None:
                    device_interface['InterfaceName'] = self.ipmi_fullname
                    IPMI_IF = device_interface
                    try:
                        bramdb.landb.deviceAddBulkInterface(self.device_name, IPMI_IF)
                        print(f"Successfully added Interface {self.ipmi_fullname} for device {self.device_name}.")
                    except Exception as e:
                        print(f"There was an ERROR adding IPMI Interface {IPMI_IF} for device {self.device_name}: {e}")
                else:
                    print("IPMI Hardware address information is not available. Skipping creation of IPMI interface.")

        #bind IPMI MAC to ipmi interface
        ipmimac = hardware_address.get("IPMIMAC")
        try:
            bind = bramdb.landb.bindUnbindInterface(self.ipmi_fullname, ipmimac)
            if bind:
                print(f"Successfully bound IPMI MAC address to the IPMI interface {self.ipmi_fullname} for device {self.device_name}")
        except Exception as e:
            print(f"ERROR binding IPMI MAC address to IPMI interface {self.ipmi_fullname}: {e}")

    def printdevinfo(self):
        print("Device Input:", self.device_input)

    def printIFcard(self):
        print("Interface Card:", self.interface_card)

    def printbulkinterface(self):
        print("Bulk Interface:", self.bulk_interface)


def commandline():
    parser = argparse.ArgumentParser(description= "Add devices from the CMS csv databases to the lanDB CERN database. Format: python3.11 CMSNet_ng_add.py device_name --function.")
    parser.add_argument('device_names', nargs='+', type=str, help='The names of the devices to manage.')
    parser.add_argument('--insert', action='store_true', help='Insert device information into lanDB.')
    parser.add_argument('--add-card', action='store_true', help='Add interface cards to the device.')
    parser.add_argument('--add-bulk-interface', action='store_true', help='Add bulk interfaces to the device.')
    parser.add_argument('--add', action='store_true', help='Call all functions: adds a device to the lanDB database with information from the CMS .csv files.')
    parser.add_argument('--print-info', action='store_true', help= 'Prints device info at each stage of the addition process')

    global args
    args = parser.parse_args()
    for device_name in args.device_names:
        cmsnet = cmsnet_add(device_name)

        if args.add:
            cmsnet.deviceInsert()
            if args.print_info:
                cmsnet.printdevinfo()
            cmsnet.deviceAddCard()
            if args.print_info:
                cmsnet.printIFcard()
            cmsnet.deviceAddBulkInterface()
            if args.print_info:
                cmsnet.printbulkinterface()
    
        else:
            if args.insert:
                cmsnet.deviceInsert()
                if args.print_info:
                    cmsnet.printdevinfo()
            
            if args.add_card:
                cmsnet.deviceAddCard()
                if args.print_info:
                    cmsnet.printIFcard()
            
            if args.add_bulk_interface:
                cmsnet.deviceAddBulkInterface()
                if args.print_info:
                    cmsnet.printbulkinterface()


if __name__ == "__main__":
    commandline()