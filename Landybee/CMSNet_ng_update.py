from typing import Any
from CSVExtracttoDict import CSVtypes
import bramdybee
from ConvSUDStoDict import SUDS2Dict
import argparse
import json
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
- check and updated interface cards
-check an dupdate interface using deviceMoveBulkInterface
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

        #load in bulk interface information for each interface in a device.   
        #finds interface names from lanDB.
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

        #adding ipmi interface and locations for interfaces as they dont exist within cms database but are present in lanDB
        #where they are added in the cmsnet_add.py
        # Append ipmi interface to cms interface info
        for name in self.ifnames:
            if 'IPMI' in name:
                ipminame = name.lower()
                break
            else:
                ipminame = None

        devint_name = extract_dict.interfacenames(None, self.device_name)

        if ipminame is not None:
            ipmiIF = self.find_dict_by_entry(self.bulk_interface, "InterfaceName", devint_name)
            if ipmiIF:
                new_impiIF = copy.deepcopy(ipmiIF)
                new_impiIF["InterfaceName"] = ipminame

                #check ipmi interface already exists
                ipmi_exists = any(item.get("InterfaceName") == ipminame and "ipmi" in item.get("InterfaceName", "") for item in self.bulk_interface)

                if not ipmi_exists:
                    self.bulk_interface.append(new_impiIF)

        #use device information location to append to interface so that we can compare it to lanDB information.
        for interface in self.interfaces_landb:
            if "Location" in interface:
                interface["Location"] = self.device_input["Location"]


        

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
        
        keys_none_cms = ['IP', 'IPv6', 'ServiceName']
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
        # Ensure that d is not None and the key exists in the dictionary
            if d is not None:
                dict_value = d.get(key)
                if value is None and dict_value is None:
                    return None
                elif isinstance(dict_value, str) and isinstance(value, str) and dict_value.upper() == value.upper():
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
                print(f'Device information for device {self.device_name} data matches, update not required')
            else:
                self.apply_updates(self.device_name, differences, type = 'Device')
                print(f"Device Information update COMPLETE.")

        except Exception as e:
            print(f"ERROR updating device input parameters in lanDB for device {self.device_name}: {e}")

    def update_interface_cards(self):
        network_interface_cards = self.device_landb.get("NetworkInterfaceCards", [])
        everything_matched = True
        #check for cms NICs in lanDB database, if not present we want to add them
        for card in self.interface_cards:
            mac = card.get("HardwareAddress")
            if mac is not None:
                try:
                    find_correct_nic = self.find_dict_by_entry(network_interface_cards, "HardwareAddress", mac)
                    if find_correct_nic is None:
                        everything_matched = False
                        print(f"NIC {card} is not found in the lanDB database, adding it to lanDB database.")
                        try:
                            bramdb.landb.deviceAddCard(self.device_name, card)
                            print(f"NIC {card} added to lanDB database")
                        except Exception as e:
                            print(f'ERROR adding NIC to the lanDB database: {e}')
                    # else:
                    #     print(f"NIC {card} exists in IT and in CMS")

                except Exception as e:
                    print(f"ERROR comparing CMS data to lanDB database for NIC {card}: {e}")

        #check for lanDB NICs in compared to cms, if they are present there then remove.
        hardware_address = extract_dict.CombinedInterfaceCards(self.device_name)
        for card in network_interface_cards:
            mac = card.get("HardwareAddress")
            
            try:
                find_nic_cms = self.find_dict_by_entry(hardware_address, "HardwareAddress", mac)
                if find_nic_cms is None:
                    everything_matched = False
                    print(f"NIC {card} is not found in the CMS database, removing it from lanDB database.")
                    try:
                        bramdb.landb.deviceRemoveCard(self.device_name, mac)
                        print("NIC removed.")
                    except Exception as e:
                        print(f"ERROR removing NIC from the lanDB database: {e}")
                # else:
                #     print(f"NIC {card} exists in IT and in CMS")
            except Exception as e:
                print(f"ERROR comparing lanDB database to CMS data for NIC {card}: {e}")

        if everything_matched:
            print(f"ALL NICs matched, no updates needed.")

    def update_interfaces(self):
        #structure:
        #check port states, if port already in use will attempt a fanout
        #for each interface present in cms data find interface with matching name and compare+update entries if differences
        for interface in self.bulk_interface:
            IFName = interface.get("InterfaceName")
            try:
                find_correct_interface = self.find_dict_by_entry(self.interfaces_landb, "InterfaceName", IFName)
                #check that the interface name exists in lanDB database otherwise we have no way to identify it and compare for updates
                if find_correct_interface is None:
                    print(f"INTERFACE {IFName} is not found in the lanDB database, please check you have the correct interface name.")
                    exit()
                else:

                    #check port for the interface we are currently on
                    # try:
                    #     swinfo = bramdb.landb.getSwitchInfo(interface.get("SwitchName"))
                    # except Exception as e:
                    #     print(f"ERROR getting switch information for interface {IFName}: {e}")


                    #check bound interface cards
                    device_info_interfaces = self.device_landb['Interfaces']
                    interface_bound = self.find_dict_by_entry(device_info_interfaces, "Name", IFName)
                    boundinterface = interface_bound.get("BoundInterfaceCard")
                    if boundinterface is None:
                        print(f"No bound NIC on interface {IFName}, continuing...")
                    else:
                        macbound = boundinterface.get("HardwareAddress") 
                        cms_cards = extract_dict.CombinedInterfaceCards(self.device_name)
                        checkbound = self.find_dict_by_entry(cms_cards, "HardwareAddress", macbound)
                        if checkbound is None:
                            print(f"Bound interface does not match CMS database, binding correct NIC")
                            hardware_address = extract_dict.MACaddress(self.device_name)
                            if hardware_address is not None:
                                try:
                                    bramdb.landb.bindUnbindInterface(InterfaceName= IFName, HardwareAddress= None) #unbind/clean interface
                                    bramdb.landb.bindUnbindInterface(InterfaceName= IFName, HardwareAddress= hardware_address.get('OnboardMAC1' or 'OnboardMAC2')) #bind correct interface
                                except Exception as e:
                                    print(f"ERROR binding correct hardware address to interface {IFName}")
                        else:
                            print(f"Hardware address bound to interface {IFName} correct.")
                    
                    #check basic parameters obtained by bulkinterface
                    flat_cms_interfaces = self.iterate_nested_dicts(interface)
                    flat_landb_interfaces = self.iterate_nested_dicts(find_correct_interface)
                    matchingkeys = [key for key in flat_cms_interfaces.keys() if key in flat_landb_interfaces]

                    differences = self.compare_dicts(flatcms_data=flat_cms_interfaces, flatlandb_data=flat_landb_interfaces, matching_keys=matchingkeys)
                    if differences == self.empty:
                        print(f'Data matches for interface {IFName}, update not required')
                    else:
                        self.apply_updates(IFName, differences, type="Interface")
            except Exception as e:
                print(f"ERROR updating interface {IFName} in lanDB for device {self.device_name}: {e}")

    def apply_updates(self, name: str, updates: dict, type="Device"):
        deviceinfo = self.device_input        
        while True:
            try:
                if type == "Device":
                    yesno = input(f"Allow changes to be made to lanDB DEVICE {name} information? (y/n): {updates}")
                    if yesno.lower() == 'y':
                    # Apply updates to the device info in lanDB
                        for key, value in updates.items():
                            try:
                                updates_key = updates[key]
                                deviceinfo[key] = updates_key['CMS database']
                                updated_deviceinfo = deviceinfo
                                bramdb.landb.deviceUpdate(name, updated_deviceinfo)
                                print(f"Updated device {name} in lanDB.")
                                
                            except Exception as e:
                                print(f"There was an error updating device {name}: {e}")
                            break
                    
                    elif yesno.lower() == 'n':
                        print(f"Continue without updating {key}...")
                    else:
                        print(f"Please input either y or n.")
                        continue
                
                elif type == "Interface":
                    yesno = input(f"Allow changes to be made to lanDB INTERFACE {name}? ('y'/'n', to end enter 'exit'): {updates}")
                    # Apply updates to the interfaces in lanDB
                    if yesno.lower() == 'y':
                        updated_IF = self.find_dict_by_entry(self.bulk_interface, "InterfaceName", name)
                        for key, value in updates.items():
                            try:
                                updates_key = updates[key]
                                deviceinfo[key] = updates_key['CMS database']
                                updated_deviceinfo = deviceinfo
                                bramdb.landb.deviceMoveBulkInterface(
                                    DeviceName= self.device_name, 
                                    InterfaceName= name,  
                                    BulkInterface=updated_IF, 
                                    BulkMoveOptions= {False}
                                    )
                                print(f"Interface {name} updated.")
                            except Exception as e:
                                print(f"There was an error updating device {name}: {e}")
                        break

                    if yesno.lower() == 'n':
                        print(f"No update for done for interface {name}")
                        break

                    elif yesno.lower() == 'exit':
                        exit()

                    else:
                        print("Please input either 'y', 'n', or 'exit'")
                        continue
            
            except Exception as e:
                print(f"Failed to update {type} {name} in lanDB: {e}")

def commandline():
    parser = argparse.ArgumentParser(description= "Compare information from CMS csv files to lanDB database for given device. Format: python3.11 CMSNet_ng_update.py device_name --function")
    parser.add_argument('device_names', nargs='+', type=str, help= 'Name(s) of the device to manage.')
    parser.add_argument('--update', action='store_true', help='Check and update device information for given device.')

    args = parser.parse_args()
    for device_name in args.device_names:
        cmsnet = cmsnet_update(device_name)

        if args.update:
            cmsnet.update_device_info()
            cmsnet.update_interface_cards()
            cmsnet.update_interfaces()

if __name__ == "__main__":
    commandline()