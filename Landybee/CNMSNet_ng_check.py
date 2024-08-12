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


    def iterate_nested_dicts(self, json_obj, root_key=None):
        results = {}
        
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if root_key is not None:
                    current_key = f"{root_key}.{key}" if root_key else key
                else:
                    current_key = key

                if isinstance(value, dict) or isinstance(value, list):
                    results.update(self.iterate_nested_dicts(value, current_key))
                else:
                    if isinstance(value, str):
                        value = value.lower()
                    results[current_key] = value
        elif isinstance(json_obj, list):
            for index, item in enumerate(json_obj):
                list_key = f"{root_key}[{index}]"
                if isinstance(item, dict) or isinstance(item, list):
                    results.update(self.iterate_nested_dicts(item, list_key))
                else:
                    if isinstance(item, str):
                        item = item.lower()
                    results[list_key] = item

        return results
    

    def compare_dicts(self):
        #using iterated_nested_dicts we flatten both dictionaries to compare all the value
        flat_cmsnet = self.iterate_nested_dicts(self.combined_csmnet)
        flat_landb = self.iterate_nested_dicts(self.device_landb)

        matching_keys = set(flat_cmsnet.keys()).intersection(set(flat_landb.keys()))

        differences = {}

        for key in matching_keys:
            value_cmsnet = flat_cmsnet.get(key)
            value_landb = flat_landb.get(key)

            #Convert strings found in cms .csv files into strings so they can be easily compared
            if isinstance(value_cmsnet, int):
                value_cmsnet = str(value_cmsnet)
            
            #LanDB returns some room values as 0001 instead of 1, to compare we remove any zeros before integer and ocnvert ints to strings
            if isinstance(value_landb, str) and value_landb.isdigit():
                value_landb = str(int(value_landb))

            #Convert any bools to strings as cms .csv returns them as strings while lanDB returns them as bools
            if isinstance(value_cmsnet, bool):
                value_cmsnet = str(value_cmsnet)

            if isinstance(value_landb, bool):
                value_landb = str(value_landb)

            if value_cmsnet != value_landb:
                differences[key] = {
                    "CMS database": value_cmsnet,
                    "lanDB database": value_landb
                }

        print(f"Differences found between lanDB database and CMS database for device {self.device_name}:")
        return print(differences)

    def __call__(self) -> Any:
        self.compare_dicts()