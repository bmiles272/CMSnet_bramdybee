'''
cmsnet delete plan:
steps to be taken when creating:
- check the existance of the device within lanDB
- deletion
-- deletion of interface: deviceRemoveBulkInterface --> removes interface.
-- deletion of device: deviceRemove --> removes device and attached cards, only possible once all the interfaces are deleted.
'''
from typing import Any
from CSVExtracttoDict import CSVtypes
import bramdybee
import sys
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()

class cmsnet_delete:

    def __init__(self, device_name) -> None:
        self.bulk_interface = extract_dict.BulkInterface(device_name)
        self.device_name = device_name

        #check if device exists
        try:
            bramdb.landb.getDeviceInfo(device_name)
        except Exception as e:
            print(f"Device {device_name} not found in lanDB database: {e}")
            exit()

    #function to just delete intefaces, will prompt user with list of possible interfaces to delete from a device.
    def delete_interface(self):
        list_IF = []
        for IF in self.bulk_interface:
            name = IF.get("InterfaceName")
            list_IF.append(name)
        print(f"Interfaces for device {self.device_name}: {list_IF}")

        while True:
            chooseIF = input("Enter the interface you would like to delete (enter 'stop' to exit):")

            if chooseIF.lower() == 'stop':
                print("Exiting the deletion process.")
                break

            if chooseIF in list_IF:
                print(f"Deleting interface : {chooseIF}")
                try:
                    bramdb.landb.deviceRemoveBulkInterface(self.device_name, chooseIF)
                    print(f"Interface {chooseIF} deleted from device {self.device_name}")
                except Exception as e:
                    print(f"Failed to delete interface {chooseIF}: {e} ")
                break
            else:
                print("Invalid interface name, please try again.")

    #Bulk remove function will remove interfaces and devices, unable to remove just devices as all interfaces need to be removed before device can be removed.
    #Seemed easier to do bulk remove over having to prompt user to delete all interfaces before being able to delete the device.
    
    def delete_device(self):
        print(f"You have called the deletion of device {self.device_name}")
        deldev = input(f"Confirm you want to delete device {self.device_name} and all the attached interfaces: (yes)/(no)")
        if deldev == 'yes':
            try:
                bramdb.landb.bulkRemove(self.device_name)
                print(f"Device {self.device_name} deleted from the lanDB database.")
            except Exception as e:
                print(f"ERROR deleting device {self.device_name}: {e}")

    def __call__(self) -> Any:
        self.delete_device()