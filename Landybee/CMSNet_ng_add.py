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
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()
'''
When instance of class is called all 3 functions automatically are used. As if we used the bulkInsert function. 
However each function is also callable individually.
'''
class add_device:

    def __init__(self, device_name) -> None:
        #Call in dicts from CSVExtracttoDict
        self.device_input = extract_dict.DeviceInput(device_name)
        self.interface_card = extract_dict.InterfaceCard(device_name)
        self.bulk_interface = extract_dict.BulkInterface(device_name)
        self.device_name = device_name

    def deviceInsert(self):
        try:
            bramdb.landb.deviceInsert(self.device_input)
            print(f"Successfully inserted device info for device {self.device_name}.")
        except Exception as e:
            print(f"There was an ERROR inserting the device info for device {self.device_name}: {e}")
        return
    
    def deviceAddCard(self):
        try:
            for card in self.interface_card:
                bramdb.landb.deviceAddCard(self.device_name, card)
                print(f"Successfully added Network Interface Card (NIC) for device {self.device_name}.")
        except Exception as e:
            print(f"There was an ERROR adding Network Interface Card (NIC) for device {self.device_name}: {e}")
        return
    
    def deviceAddBulkInterface(self):
        for interface in self.bulk_interface:
            IFName = interface.get("InterfaceName")
            switch_name = interface.get("SwitchName")
            switchnumber = interface.get("PortNumber")
            hardware_address = extract_dict.MACaddress(self.device_name)
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
                            fanout = bramdb.landb.enableFanOutFromSwitchPort(switch_name)
                            if fanout == True:
                                print(f"Fanout for switchport {switch_name} created succesfully.")
                        except Exception as fanout_error:
                            print(f"Fanout failed,. Trying to continue as it could already be a fanout: {fanout_error}")
                else:
                    print(f"No switch info found for device name {self.device_name}.")

            except Exception as e:
                print(f"There was an ERROR getting info for switch {switch_name}, for interface {IFName}: {e}")

            try:
                bramdb.landb.deviceAddBulkInterface(self.device_name, interface)
                print(f"Successfully added Interface for device {self.device_name}.")
            except Exception as e:
                print(f"There was an ERROR adding Bulk Interface {IFName} for device {self.device_name}: {e}")
            
            try:
                bind = bramdb.landb.bindUnbindInterface(IFName, hardware_address)
                if bind == True:
                    return print(f"Interface succesfully binded to hardware address {hardware_address}")
            except Exception as e:
                print(f"ERROR binding interface {IFName} to {hardware_address}: {e}")
        
    #Call function is what allows all 3 functions to be used when instance of add_device is called in combination with a device name.
    def __call__(self) -> Any:
        self.deviceInsert()
        self.deviceAddCard()
        self.deviceAddBulkInterface()
        return print(f"full device {self.device_name} added. :)")

