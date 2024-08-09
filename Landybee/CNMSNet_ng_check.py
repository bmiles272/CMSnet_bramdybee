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

    def get_all_keys(self, iterable, returned = "value"):

        result = {}

        def extract(current_iterable: dict, parent_key = ''):
            if isinstance(current_iterable, dict):
                for key, value in current_iterable.items():
                    full_key = f"{parent_key}/{key}" if parent_key else key

                    if returned == "key":
                        result[full_key] = None  # assign automatiuc value, for cmsnet use most liekly wont be used.
                    elif returned == "value":
                        if full_key not in result:
                            result[full_key] = []

                        elif (isinstance(value, dict) or isinstance(value, list)):
                            new_values = extract(value, parent_key = full_key)
                            if new_values:
                                result[full_key] = new_values

                        else:
                            result[full_key].append(value)
                        
                    else:
                        raise ValueError("'returned' keyword only accepts 'key' or 'value'.")
                    

                    extract(value, parent_key=full_key)

            if isinstance(current_iterable, list):
                for index, el in enumerate(current_iterable):
                    extract(el, parent_key= f'{parent_key}[{index}]')

            else:
                if returned == "value":
                    if parent_key not in result:
                        result[parent_key] = []
                    result[parent_key].append(current_iterable)
            
        extract(iterable)
        return result
        
    def describe_changes(self, changes):
        for path, change in changes.items():
            old_value = change['old_value']
            new_value = change['new_value']
            
            message = f"For: {path}, the value given in cmsnet csv is {old_value}, the lanDB database has it recorded as {new_value}."
            print(message)
    

    def compare_all(self):
        cmsnet = self.get_all_keys(self.combined_csmnet)
        landb = self.get_all_keys(self.device_landb)
        # print(self.device_landb)
        print(landb)

    # def compare_location(self):
    #     location = self.device_input.get('Location')
    #     locationdict = {key: str(value).lower() for key, value in location.items()}
    #     landb_lower = {key: str(value).lower() for key, value in self.device_landb.get("UserPerson").items()}
    #     diff_location = DeepDiff(locationdict, landb_lower, ignore_order = True)
    #     changes = diff_location.get('values_changed')

    #     if not changes:
    #         print(f"No differences in location for device {self.device_name}.")
    #     else:
    #         print(self.describe_changes(changes))

    # def compare_personinput(self):
    #     personinput = self.device_input.get('UserPerson')
    #     personinput_dict = {key: str(value).lower() for key, value in personinput.items()}
    #     landb_lower = {key: str(value).lower() for key, value in self.device_landb.get("UserPerson").items()}
    #     diff_location = DeepDiff(personinput_dict, landb_lower, ignore_order = True)
    #     changes = diff_location.get('values_changed')

    #     if not changes:
    #         print(f"No differences in User Person, Responsible Person and lanDB Manager Person for device {self.device_name}.")
    #     else:
    #         print(self.describe_changes(changes))

    # def compare_operatingsystem(self):
    #     os = self.device_input.get('OperatingSystem')
    #     os_dict = {key: str(value).lower() for key, value in os.items()}
    #     landb_lower = {key: str(value).lower() for key, value in self.device_landb.get("OperatingSystem").items()}
    #     diff_location = DeepDiff(os_dict, landb_lower, ignore_order = True)
    #     changes = diff_location.get('values_changed')

    #     if not changes:
    #         print(f"No differences in Operating System for device {self.device_name}.")
    #     else:
    #         print(self.describe_changes(changes))


    # def compare_deviceinput(self):
    #     diff_devinp = DeepDiff(self.device_input, self.device_landb, ignore_order= True, ignore_string_case= True)
    #     changes = diff_devinp.get('values_changed')
    #     # print(diff_devinp)
    #     if not changes:
    #         print(f"No differences in device parameters for device {self.device_name}.")
    #     else:
    #         print(self.describe_changes(changes))
    #     # differences = {
    #     #     key.lower(): {'old_value': str(self.device_landb[key]).lower(),
    #     #           'new_value': str(self.device_input[key]).lower()}
    #     #     for key in self.device_landb
    #     #     if key in self.device_input and str(self.device_landb[key]).lower() != str(self.device_input[key]).lower()
    #     # }
    #     # print(differences)

    # def compare_interfacecards(self):
    #     diff_devcards = DeepDiff(self.interface_card, self.device_landb, ignore_order= True, ignore_string_case= True)
    #     changes = diff_devcards.get('values_changed')
    #     if not changes:
    #         print(f"No differences in interface cards for device {self.device_name}.")
    #     else:
    #         print(self.describe_changes(changes))

    # def compare_bulkinterface(self):
    #     diff_bulkinterface = DeepDiff(self.interface_card, self.device_landb, ignore_order= True, ignore_string_case= True)
    #     changes = diff_bulkinterface.get('values_changed')
    #     # print(diff_bulkinterface)
    #     if not changes:
    #         print(f"No differences in bulk interface for device {self.device_name}.")
    #     else:
    #         print(self.describe_changes(changes))

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.compare_location()
        self.compare_personinput()
        self.compare_operatingsystem()