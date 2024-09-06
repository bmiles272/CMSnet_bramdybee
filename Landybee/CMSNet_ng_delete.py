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
import argparse

# Initialise any classes that need to be used
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()

class cmsnet_delete:

    def __init__(self, device_name) -> None:
        self.bulk_interface = extract_dict.BulkInterface(device_name)
        self.device_name = device_name
        # Check if the device exists
        try:
            bramdb.landb.getDeviceInfo(device_name)
        except Exception as e:
            print(f"Device {device_name} not found in lanDB database: {e}")
            exit()

    # Function to just delete interfaces, will prompt user with a list of possible interfaces to delete from a device.
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

    # Function to delete all interfaces before deleting the device.
    def delete_all_interfaces(self):
        for IF in self.bulk_interface:
            interface_name = IF.get("InterfaceName")
            print(f"Deleting interface {interface_name} from device {self.device_name}")
            try:
                bramdb.landb.deviceRemoveBulkInterface(self.device_name, interface_name)
                print(f"Interface {interface_name} deleted.")
            except Exception as e:
                print(f"Failed to delete interface {interface_name}: {e}")
                return False  # If we fail to delete an interface, abort the process
        return True  # Return True if all interfaces were successfully deleted

    # Modified delete_device function to first delete all interfaces and then the device.
    def delete_device(self, auto_confirm=False):
        if auto_confirm:
            print(f"Automatically deleting device {self.device_name} and its interfaces.")
        else:
            deldev = input(f"Confirm you want to delete device {self.device_name} and all the attached interfaces: (yes)/(no): ")
            if deldev.lower() != 'yes':
                print("Device deletion aborted.")
                return

        # First, delete all interfaces
        if self.delete_all_interfaces():
            print(f"All interfaces for device {self.device_name} have been deleted.")
            # Now delete the device itself
            try:
                bramdb.landb.deviceRemove(self.device_name)
                print(f"Device {self.device_name} deleted from the lanDB database.")
            except Exception as e:
                print(f"ERROR deleting device {self.device_name}: {e}")
        else:
            print(f"Failed to delete all interfaces for device {self.device_name}. Aborting device deletion.")

def commandline():
    parser = argparse.ArgumentParser(description="Delete devices from the CMS csv databases to the lanDB CERN database. Format: python3.11 CMSNet_ng_delete.py device_name --function.")
    parser.add_argument('device_names', nargs='+', type=str, help='The name(s) of the device(s) to manage.')
    parser.add_argument('--delete-interface', action='store_true', help='Delete an interface from a device')
    parser.add_argument('--delete', action='store_true', help='Remove a device from lanDB database.')
    parser.add_argument('-y', '--yes', action='store_true', help='Auto confirm device deletion without prompting user input.')

    args = parser.parse_args()

    for device_name in args.device_names:
        cmsnet = cmsnet_delete(device_name)

        if args.delete:
            cmsnet.delete_device(auto_confirm=args.yes)  # Pass the 'yes' argument to skip user confirmation
        elif args.delete_interface:
            cmsnet.delete_interface()

if __name__ == "__main__":
    commandline()