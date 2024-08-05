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

class add_device:

    def __init__(self, device_name) -> None:
        #call in dicts from CSVExtracttoDict
        self.device_input = extract_dict.DeviceInput(device_name)
        self.interface_card = extract_dict.InterfaceCard(device_name)
        self.bulk_interface = extract_dict.BulkInterface(device_name)
        self.device_name = device_name

    def deviceInsert(self):
        try:
            bramdb.landb.deviceInsert(self.device_input)
        except Exception as e:
            print(f"There was an ERROR inserting the device info for device {self.device_name}: {e}")
        return
    
    def deviceAddCard(self):
        try:
            bramdb.landb.deviceAddCard(self.device_name, self.interface_card)
        except Exception as e:
            print(f"There was an error adding Network Interface Card (NIC) for device {self.device_name}: {e}")
        return
    
    def deviceAddBulkInterface(self):
        try:
            bramdb.landb.deviceAddBulkInterface(self.device_name, self.bulk_interface)
        except Exception as e:
            print(f"There was an error adding Bulk Interface for device {self.device_name}: {e}")
        return
    
    def __call__(self) -> Any:
        self.deviceInsert()
        self.deviceAddCard()
        self.deviceAddBulkInterface()
