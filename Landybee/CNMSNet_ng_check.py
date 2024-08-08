from typing import Any
from CSVExtracttoDict import CSVtypes
import bramdybee
from ConvSUDStoDict import SUDS2Dict
import pandas as pd
from deepdiff import DeepDiff
import json
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()
conv = SUDS2Dict()

'''
plan for creating the check function:
- check if the device exists using getinfo function, if it does not exist then advise going to add function
- start to compare entries:
-- cards
-- interfaces
-- basic device info
-- 'compound' parameters
'''

class cmsnet_check:

    def __init__(self, device_name) -> None:
        
        #check for the existance of device
        try:
            device_info = bramdb.landb.getDeviceInfo(device_name)
            print(f"Device {device_name} found in lanDB database")
            print('Checking information...')
        except Exception as e:
            print(f"Device {device_name} not found in lanDB database: {e}")
            exit()
    
        device_str = conv.sobject_to_json(device_info)
        self.device_landb = json.loads(device_str)

        #read in all csv files containing the device information
        self.device_input = extract_dict.DeviceInput(device_name)
        self.interface_card = extract_dict.InterfaceCard(device_name)
        self.bulk_interface = extract_dict.BulkInterface(device_name)
        self.device_name = device_name

        #combine the dicts
        self.combined_csmnet = {
            **self.device_input,
            'NetworkInterfaceCards': self.interface_card,
            'Interfaces': self.bulk_interface
        }
        # print(type(self.combined_dicts))
        # print(type(self.device_params))
        # print(self.device_params)
        # print(self.combined_dicts.get("Location"))
        # print(self.device_input)
        # print(self.combined_dict)
        
    def describe_changes(self, changes):
        for path, change in changes.items():
            old_value = change['old_value']
            new_value = change['new_value']
            
            message = f"For: {path}, the value given in cmsnet csv is {old_value}, the lanDB database has it recorded as {new_value}."
            print(message)
    

    def compare_location(self):
        location = self.device_input.get('Location')
        locationdict = {key: str(value) for key, value in location.items()}
        diff_location = DeepDiff(locationdict, self.device_landb.get('Location'), ignore_order = True)
        changes = diff_location.get('values_changed')
        if not changes:
            print(f"No differences in location for device {self.device_name}.")
        else:
            print(self.describe_changes(changes))

    def compare_personinput(self):
        location = self.device_input.get('UserPerson')
        locationdict = {key: str(value) for key, value in location.items()}
        diff_location = DeepDiff(locationdict, self.device_landb.get('UserPerson'), ignore_order = True)
        changes = diff_location.get('values_changed')
        if not changes:
            print(f"No differences in User Person, Responsible Person and lanDB Manager Person for device {self.device_name}.")
        else:
            print(self.describe_changes(changes))

    def compare_operatingsystem(self):
        location = self.device_input.get('OperatingSystem')
        locationdict = {key: str(value) for key, value in location.items()}
        diff_location = DeepDiff(locationdict, self.device_landb.get('OperatingSystem').lower(), ignore_order = True)
        changes = diff_location.get('values_changed')
        if not changes:
            print(f"No differences in Operating System for device {self.device_name}.")
        else:
            print(self.describe_changes(changes))


    # def compare_deviceinput(self):
        # diff_devinp = DeepDiff(self.device_input, self.device_landb, ignore_order= True, ignore_string_case= True)
        # changes = diff_devinp.get('values_changed')
        # # print(diff_devinp)
        # if not changes:
        #     print(f"No differences in device parameters for device {self.device_name}.")
        # else:
        #     print(self.describe_changes(changes))
        # differences = {
        #     key.lower(): {'old_value': str(self.device_landb[key]).lower(),
        #           'new_value': str(self.device_input[key]).lower()}
        #     for key in self.device_landb
        #     if key in self.device_input and str(self.device_landb[key]).lower() != str(self.device_input[key]).lower()
        # }
        # print(differences)

    def compare_interfacecards(self):
        diff_devcards = DeepDiff(self.interface_card, self.device_landb, ignore_order= True, ignore_string_case= True)
        changes = diff_devcards.get('values_changed')
        if not changes:
            print(f"No differences in interface cards for device {self.device_name}.")
        else:
            print(self.describe_changes(changes))

    def compare_bulkinterface(self):
        diff_bulkinterface = DeepDiff(self.interface_card, self.device_landb, ignore_order= True, ignore_string_case= True)
        changes = diff_bulkinterface.get('values_changed')
        # print(diff_bulkinterface)
        if not changes:
            print(f"No differences in bulk interface for device {self.device_name}.")
        else:
            print(self.describe_changes(changes))

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.compare_location()
        self.compare_personinput()
        self.compare_operatingsystem()