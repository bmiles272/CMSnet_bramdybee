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
import json
from CSVExtracttoDict import CSVtypes
import bramdybee
import ConvSUDStoDict
import os
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
                            print(f"Interface successfully bound to hardware address {macaddress}.")
                        else:
                            print(f"Failed to bind interface {IFName} to hardware address {macaddress}.")
                    else:
                        print(f"No valid MAC address found for interface {IFName}.")
                except Exception as e:
                    print(f"ERROR binding interface {IFName} to {macaddress}: {e}")
            else:
                print("Hardware address information is not available. Skipping binding.")
        
        #generate IPMI interfaces for a device that has non-zero IPMIMAC
        interfaces = extract_dict.interface_list(self.device_name)
        ipmi_interface_found = any('ipmi' in iface.lower() for iface in interfaces)

        if not ipmi_interface_found:
            if hardware_address is not None:
                if hardware_address.get("IPMIMAC") is not None:
                    ipmi_name =  self.device_name + '.ipmi'
                    device_interface['InterfaceName'] = extract_dict.interfacenames(ipmi_name, self.device_name)
                    IPMI_IF = device_interface

                    try:
                        bramdb.landb.deviceAddBulkInterface(self.device_name, IPMI_IF)
                        print(f"Successfully added Interface {IPMI_IF.get('InterfaceName')} for device {self.device_name}.")
                    except Exception as e:
                        print(f"There was an ERROR adding IPMI Interface {IPMI_IF} for device {self.device_name}: {e}")
            else:
                print("IPMI Hardware address information is not available. Skipping creation of IPMI interface.")
        
    #Call function is what allows all 3 functions to be used when instance of add_device is called in combination with a device name.
    def __call__(self) -> Any:
        self.deviceInsert()
        self.deviceAddCard()
        self.deviceAddBulkInterface()
