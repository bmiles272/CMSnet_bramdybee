from typing import Any
from CSVExtracttoDict import CSVtypes
import bramdybee
from ConvSUDStoDict import SUDS2Dict
import json
import argparse
import copy
#initialise any classes used in script
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()
conv = SUDS2Dict()


'''
Plan for update function:

- use check function or copy check function and chnage output given so its easy to update the function
- write an update which uses output from chnaged check function to update parameters

- check whether device exists in database and whether only 1 exists
- check and update device info (deviceUpdate function)
- check and updated 
'''

class cmsnet_update:

    def __init__(self, device_name) -> None:
        #check for the existance of device
        try:
            device_info = bramdb.landb.getDeviceInfo(device_name)
            deviceinfo_str = conv.sobject_to_json(device_info)
            self.device_landb = json.loads(deviceinfo_str)
            if device_info:
                print(f"Device {device_name} found in lanDB database")
                print('Checking information...')
        
        except Exception as e:
            print(f"Device {device_name} not found in lanDB database: {e}")
            exit()

        #read in all csv files containing the device information
        self.device_input = extract_dict.DeviceInput(device_name)
        self.bulk_interface = extract_dict.BulkInterface(device_name)
        self.interface_cards = extract_dict.CombinedInterfaceCards(device_name)
        # print(self.bulk_interface)

        #load in bulk interface information for each interface in a device.   
        #finds interface names from lanDB  
        try:
            self.ifnames = []
            interfaces_landb = self.device_landb.get("Interfaces")
            for interface in interfaces_landb:
                IFName = interface.get("Name")
                self.ifnames.append(IFName)

            intf_list =[]
        #obtains interface information from lanDB database using getBulkInterfaceInfo instead of deviceinfo as it matches what we input.
            for name in self.ifnames:
                interface =  bramdb.landb.getBulkInterfaceInfo(name)
                interface_str = conv.sobject_to_json(interface)
                interface_landb = json.loads(interface_str)
                intf_list.append(interface_landb)
        except Exception as e:
            print(f"ERROR: {e}")

        self.interfaces_landb = intf_list
        self.device_name = device_name
        self.empty = {}

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
    
    def compare_dicts(self, flatcms_data: dict, flatlandb_data: dict, matching_keys):
        #using iterated_nested_dicts we flatten both dictionaries to compare all the value
        #it also adjust values within dicts to be easily comparable
        differences = {}

        keys_none_cms = ['ServiceName', 'IP', 'IPv6']
        for key in keys_none_cms:
            if key in matching_keys and flatcms_data.get(key) is None:
                matching_keys.remove(key)

        if "OutletLabel" in matching_keys:
            if flatcms_data["OutletLabel"] == 'auto' and flatlandb_data['OutletLabel'].startswith('auto'):
                matching_keys.remove("OutletLabel")
            

        for key in matching_keys:
            value_cmsnet = flatcms_data.get(key)
            value_landb = flatlandb_data.get(key)

            #Convert ints found in cms .csv files into strings so they can be easily compared
            if isinstance(value_cmsnet, int):
                value_cmsnet = str(value_cmsnet)
            if isinstance(value_landb, int):
                value_landb = str(value_landb)
            
            #LanDB returns some room values as 0001 instead of 1, to compare we remove any zeros before integer and ocnvert ints to strings
            if isinstance(value_landb, str) and value_landb.isdigit():
                value_landb = str(int(value_landb))

            #Convert any bools to strings as cms .csv returns them as strings while lanDB returns them as bools
            if isinstance(value_cmsnet, bool):
                value_cmsnet = str(value_cmsnet)
            if isinstance(value_landb, bool):
                value_landb = str(value_landb)

            #reproduce differences as a dictionary with clear entries
            if value_cmsnet != value_landb:
                differences[key] = {
                    "CMS database": value_cmsnet,
                    "lanDB database": value_landb
                }

        return differences
    
    def find_dict_by_entry(self, dict_list, key, value):
        for d in dict_list:
            if d.get(key, '').upper() == value.upper():
                return d
        return None
    
    def update_device_info(self):
        # First, compare the device input
        flat_cms_devicesinput = self.iterate_nested_dicts(self.device_input)
        flat_landb_deviceinput = self.iterate_nested_dicts(self.device_landb)
        matchingkeys = set(flat_cms_devicesinput.keys()).intersection(set(flat_landb_deviceinput))

        try:
            differences = self.compare_dicts(flatcms_data=flat_cms_devicesinput, flatlandb_data=flat_landb_deviceinput, matching_keys=matchingkeys)
            if differences == self.empty:
                print(f'Data matches, update not required')
            else:
                self.apply_updates(self.device_name, differences)
            print(f"Device Input parameter update COMPLETE.")

        except Exception as e:
            print(f"ERROR updating device input parameters in lanDB for device {self.device_name}: {e}")

    def update_interface_cards(self):
        network_interface_cards = self.device_landb.get("NetworkInterfaceCards", [])

        for card in self.interface_cards:
            mac = card.get("HardwareAddress")
            try:
                find_correct_dict = self.find_dict_by_entry(network_interface_cards, "HardwareAddress", mac)
                flat_landb_IFcards = self.iterate_nested_dicts(find_correct_dict)
                flatcard = self.iterate_nested_dicts(card)
                matchingkeys = [key for key in flatcard.keys() if key in flat_landb_IFcards]

                differences = self.compare_dicts(flatcms_data=flatcard, flatlandb_data=flat_landb_IFcards, matching_keys=matchingkeys)
                if differences:
                    self.apply_updates(self.device_name, differences, type="NIC")
            except Exception as e:
                print(f"ERROR updating network interface cards in lanDB for device {self.device_name}: {e}")
        
        print(f"Device Interface card update COMPLETE.")

    def update_interfaces(self):
        # Append ipmi interface to cms interface info
        for name in self.ifnames:
            if 'IPMI' in name:
                ipminame = name.lower()
                break

        devint_name = extract_dict.interfacenames(None, self.device_name)

        if ipminame:
            ipmiIF = self.find_dict_by_entry(self.bulk_interface, "InterfaceName", devint_name)
            if ipmiIF:
                new_impiIF = copy.deepcopy(ipmiIF)
                new_impiIF["InterfaceName"] = ipminame
                ipmi_exists = any(item.get("InterfaceName") == ipminame and "ipmi" in item.get("InterfaceName", "") for item in self.bulk_interface)
                if not ipmi_exists:
                    self.bulk_interface.append(new_impiIF)

        for interface in self.interfaces_landb:
            if "Location" in interface:
                interface["Location"] = self.device_input["Location"]

        for interface in self.bulk_interface:
            IFName = interface.get("InterfaceName")
            find_correct_interface = self.find_dict_by_entry(self.interfaces_landb, "InterfaceName", IFName)
            flat_cms_interfaces = self.iterate_nested_dicts(interface)
            flat_landb_interfaces = self.iterate_nested_dicts(find_correct_interface)
            matchingkeys = [key for key in flat_cms_interfaces.keys() if key in flat_landb_interfaces]

            try:
                differences = self.compare_dicts(flatcms_data=flat_cms_interfaces, flatlandb_data=flat_landb_interfaces, matching_keys=matchingkeys)
                if differences:
                    self.apply_updates(IFName, differences, type="Interface")
            except Exception as e:
                print(f"ERROR updating interfaces in lanDB for device {self.device_name}: {e}")

        print(f"Interface update COMPLETE.")

    def apply_updates(self, name, updates, type="Device"):
        try:
            if type == "Device":
                # Apply updates to the device info in lanDB
                for key, value in updates.items():
                    # Assuming bramdb.landb.updateDeviceInfo is the method to update device info
                    bramdb.landb.updateDeviceInfo(name, key, value['CMS database'])
                print(f"Updated device {name} in lanDB.")
            
            elif type == "NIC":
                # Apply updates to the network interface cards in lanDB
                for key, value in updates.items():
                    # Assuming bramdb.landb.updateNIC is the method to update NIC info
                    bramdb.landb.updateNIC(name, key, value['CMS database'])
                print(f"Updated NIC for device {name} in lanDB.")
            
            elif type == "Interface":
                # Apply updates to the interfaces in lanDB
                for key, value in updates.items():
                    # Assuming bramdb.landb.updateInterface is the method to update Interface info
                    bramdb.landb.updateInterface(name, key, value['CMS database'])
                print(f"Updated interface {name} in lanDB.")
            
        except Exception as e:
            print(f"Failed to update {type} {name} in lanDB: {e}")
