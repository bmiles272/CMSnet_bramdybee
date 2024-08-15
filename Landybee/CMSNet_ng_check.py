from typing import Any
from CSVExtracttoDict import CSVtypes
import bramdybee
from ConvSUDStoDict import SUDS2Dict
import json
import argparse
import copy
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
        try:
            self.ifnames = []
            interfaces_landb = self.device_landb.get("Interfaces")
            #retreive number and names of interfaces from 
            for interface in interfaces_landb:
                IFName = interface.get("Name")
                self.ifnames.append(IFName)

            intf_list =[]
            for name in self.ifnames:
                interface =  bramdb.landb.getBulkInterfaceInfo(name)
                interface_str = conv.sobject_to_json(interface)
                interface_landb = json.loads(interface_str)
                intf_list.append(interface_landb)
        except Exception as e:
            print(f"ERROR: {e}")

        self.interfaces_landb = intf_list
        self.device_name = device_name

        #combine the dicts
        self.combined_csmnet = {
            **self.device_input,
            'NetworkInterfaceCards': self.interface_cards,
            'Interfaces': self.bulk_interface
        }

        self.flat_landb = self.iterate_nested_dicts(self.device_landb)
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

        #if value in cms is none then ignore as lanDB automatcally assigns values
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

            #Convert strings found in cms .csv files into strings so they can be easily compared
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
    
    #Compare device input parameters
    def compare_device_input(self):
        flat_cms_devicesinput = self.iterate_nested_dicts(self.device_input)
        flat_landb_deviceinput = self.iterate_nested_dicts(self.device_landb)
        matchingkeys = set(flat_cms_devicesinput.keys()).intersection(set(flat_landb_deviceinput))

        try:
            compare_devinp = self.compare_dicts(flatcms_data= flat_cms_devicesinput, flatlandb_data= flat_landb_deviceinput, matching_keys= matchingkeys)
            print(f"DEVICE INPUT: Differences found between lanDB database and CMS database for device {self.device_name}:")
            if compare_devinp == self.empty:
                print(f"NO DIFFERENCES")
            else:
                print(compare_devinp)
            print(f"Device Input paramater comparison COMPLETE.")
        except Exception as e:
            print(f"ERROR comparing device input paramaters to lanDB data for device {self.device_name}: {e}")

    def compare_interface_cards(self):
        #load in lanDB and cms interface cards and flatten so that there are no nested values
        network_interface_cards = self.device_landb.get("NetworkInterfaceCards", [])

        for card in self.interface_cards:
            mac = card.get("HardwareAddress")

            try:
                #Select the dict by the value of the hardware address in landb, once multiple NICs are added this become vital
                find_correct_dict = self.find_dict_by_entry(network_interface_cards, "HardwareAddress", mac)
                flat_landb_IFcards = self.iterate_nested_dicts(find_correct_dict)
                flatcard = self.iterate_nested_dicts(card)
                matchingkeys = [key for key in flatcard.keys() if key in flat_landb_IFcards]


                try:
                    #compare values from both dictioanries using matching keys
                    compare_card = self.compare_dicts(
                        flatcms_data= flatcard, 
                        flatlandb_data= flat_landb_IFcards, 
                        matching_keys= matchingkeys
                        )
                    
                    print(f"NICs: Differences found between lanDB database and CMS database for device {self.device_name}:")
                    if compare_card == self.empty:
                        print(f"NO DIFFERENCES")
                    else:
                        print(compare_card)
                    
                except Exception as e:
                    print(f"ERROR comparing device input paramaters to lanDB data for device {self.device_name}: {e}")
            except Exception as e:
                print(f"ERROR: {e}")
    
        print(f"Device Interface card comparison COMPLETE.")

    #find a dictionary based on one of the entries in that dictionaries
    def find_dict_by_entry(self, dict_list, key, value):
        for d in dict_list:
            if d.get(key, '').upper() == value.upper():
                return d
        return None

    def compare_interfaces(self):
        #append ipmi interface to cms interface info, it does not exist in interfaces.csv but is created when added to lanDB so it exists there.
        for name in self.ifnames:
            if 'IPMI' in name:
                ipminame = name.lower()
                break
            else:
                None

        devint_name = extract_dict.interfacenames(None, self.device_name)

        if ipminame is not None:
            ipmiIF = self.find_dict_by_entry(self.bulk_interface, "InterfaceName", devint_name)
            if ipmiIF:
                new_impiIF = copy.deepcopy(ipmiIF)
                new_impiIF["InterfaceName"] = ipminame
                
                #check if ipmi interface already exists in bulk_interface
                ipmi_exists = any(
                        item.get("InterfaceName") == ipminame and "ipmi" in item.get("InterfaceName", "")
                        for item in self.bulk_interface
                        )
                
                if not ipmi_exists:
                    self.bulk_interface.append(new_impiIF)

        #location extracted empty from getbulkinterfaceinfo, replace with device info whihc has it filled in.
        for interface in self.interfaces_landb:
            if "Location" in interface:
                interface["Location"] = self.device_input["Location"]

        #first select interface with matching names in cms and landb database.
        for interface in self.bulk_interface:
            IFName = interface.get("InterfaceName")
            find_correct_interface = self.find_dict_by_entry(self.interfaces_landb, "InterfaceName", IFName)
            flat_cms_interfaces = self.iterate_nested_dicts(interface)
            flat_landb_interfaces = self.iterate_nested_dicts(find_correct_interface)
            matchingkeys = [key for key in flat_cms_interfaces.keys() if key in flat_landb_interfaces]

            try:
                compare_IF = self.compare_dicts(
                    flatcms_data= flat_cms_interfaces, 
                    flatlandb_data= flat_landb_interfaces, 
                    matching_keys= matchingkeys
                    )
                
                print(f"INTERFACE: Differences found between lanDB database and CMS database for interface {IFName}:")
                if compare_IF == self.empty:
                    print(f"NO DIFFERENCES")
                else:
                    print(compare_IF)

            except Exception as e:
                print(f"ERROR comparing device input paramaters to lanDB data for device {self.device_name}: {e}")

        print(f"Interface comparison complete.")

def commandline():
    parser = argparse.ArgumentParser(description= "Compare information from CMS csv files to lanDB database for given device. Format: python3.11 CMSNet_ng_check.py device_name --function")
    parser.add_argument('device_name', type=str, help='The name of the device to manage.')
    parser.add_argument('--check', action='store_true', help='Check for differences in device information.')

    args = parser.parse_args()
    cmsnet = cmsnet_check(args.device_name)

    if args.check:
        cmsnet()  # Calls the __call__ method to execute all three functions
    else:
        if args.check:
            cmsnet.compare_dicts()

if __name__ == "__main__":
    commandline()