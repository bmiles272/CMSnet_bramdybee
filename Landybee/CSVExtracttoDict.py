import pandas as pd
from typing import List
'''
Object which transforms the data from CMS CSV device files into python dictionaries for the types.py file used by landybee in order to
alter LanDB entries. Some types require dictionaries within dictionaries, for example the DeviceInput requires a location 'dictionary' within it.
Difference between BulkInterface and Interfaces is that BulkInterface is in the format required by types.py, the interfaces fucntion simply lists
the interfaces, info and their associated aliases (bulkinterface requires a list of aliases).
'''


class CSVtypes:

    def __init__(self, file_list = None) -> None:
        
        '''
        Call all .csv files whihc are used throughout the functions, a list is also generated as some functions require data from more than one file.
        '''
        self.devicescsvfile = pd.read_csv('data/cms/devices.csv', comment='#')
        self.aliasescsvfile = pd.read_csv('data/cms/aliases.csv', comment='#')
        self.interfacescsvfile = pd.read_csv('data/cms/interfaces.csv', comment='#')
        self.networkscsvfile = pd.read_csv('data/cms/networks.csv', comment='#')
        self.networks_routescsvfile = pd.read_csv('data/cms/networks_routes.csv', comment='#')
        self.switches_special_portscsvfile = pd.read_csv('data/cms/switches_special_ports.csv', comment='#')

        if file_list is None:
            self.file_list = ['data/cms/devices.csv', 'data/cms/aliases.csv', 'data/cms/interfaces.csv', 'data/cms/networks.csv', 'data/cms/networks_routes.csv', 'data/cms/switches_special_ports.csv']  # Default file list
        else:
            self.file_list = file_list

        #import serial files and combine them since they have equal columns
        file_paths = [
            'data/serial/Dell_serial_number_blades.csv',
            'data/serial/Dell_serial_number_Rx30.csv',
            'data/serial/Dell_serial_number_Rx40.csv',
            'data/serial/maguay_serial_number.csv'
        ]

        readserial = [pd.read_csv(file, comment= '#') for file in file_paths]
        self.serials = pd.concat(readserial, ignore_index = True)

        # Define the mediums key readable table
        self.mediums = {
            "1": "GIGABITETHERNET",
            "10": "TENGIGAETHERNET",
            "25": "25GIGABITETHERNET",
            "40": "40GIGABITETHERNET",
            "50": "50GIGABITETHERNET",
            "100": "100GIGABITETHERNET",
            "56": "56GIGABITIB",
            "IB": "INFINIBAND",
            "IB-EDR": "INFINIBAND-EDR"
        }

        # Define the speeds key readable table
        self.speeds = {
            "1": "1000",
            "10": "10000",
            "25": "25000",
            "40": "40000",
            "50": "50000",
            "100": "100000",
            "56": "56000",
            "IB": "56000",
            "IB-EDR": "100000"
}
        #define global cms domain
        self.domain = '--cms.cern.ch'

    #Extract keys and input true values from medium and speed tables.
    def get_medium_description(self, key):
        cleaned_key = str(key).strip()
        return self.mediums.get(cleaned_key, "Unknown medium")

    def get_speed_value(self, key):
        cleaned_key = str(key).strip()
        return self.speeds.get(cleaned_key, "Unknown speed")

    #location dictionary, pointing to location of device in building, floor, room format
    def location(self, device_name):
        locations = []
        csvfile = self.devicescsvfile

        required_columns = {'<Device>', '<building>', '<floor>', '<room>'}
        if not required_columns.issubset(csvfile):
            raise ValueError("One or more required columns are missing in file")

        for index, row in csvfile.iterrows():
            if row['<Device>'] == device_name:
                location = {
                        'Building': row['<building>'],
                        'Floor': row['<floor>'],
                        'Room': row['<room>']
                    }

                locations.append(location)
        return locations

    #person input dictionary points to owner of device and their information
    def PersonInput(self, device_name):
        PersonInput = []

        csvfile = self.devicescsvfile

        for index, row in csvfile.iterrows():
            if row['<Device>'] == device_name:
                PersonInputs = {
                        'Name': "CMS-NET-ADMINS" if '<OS>' != 'Windows' else "CMS-NET-DCS",
                        # 'Name': row['<MainUser>'] if '<MainUser>'in row else "CMS-NET-ADMINS",
                        'FirstName': row['<FirstName>'] if '<FirstName>' in row else "E-GROUP",
                        'Department': row['<Department>'] if '<Department>' in row else None,
                        'Group': row['<Group>'] if '<Group>' in row else None,
                        'PersonID': row['<PersonID>'] if '<PersonID>' in row else None
                    }
                        
                PersonInput.append(PersonInputs)
        return PersonInput

    def OperatingSystem(self, device_name):
        OS = []
        csvfile = self.devicescsvfile

        required_columns = {'<OS>', '<OSversion>'}
        if not required_columns.issubset(csvfile):
            raise ValueError("One or more required columns are missing in file")

        for index, row in csvfile.iterrows():
            if row['<Device>'] == device_name:
                OpSys = {
                        'Name': row['<OS>'],
                        'Version': row['<OSversion>']
                    }
        
                OS.append(OpSys)
        return OS
    
    #IP alias list, as a device can have more than 1 interface each interface can have its own alias
    def IPAliasList(self, device_name = None, interface_name = None):
        IPAList = []
        device_rows = self.aliasescsvfile[self.aliasescsvfile['<Device>'] == device_name]

        if interface_name == None:
            for index, row in device_rows.iterrows():
                alias = row['<Alias>'] if '<Alias>' in row else None
                if alias is not None:
                    split = alias.split('.')
                    newalias = split[0] + self.domain
                    IPAList.append(newalias)
        else:
            aliases_rows = device_rows[device_rows['<IFName>'] == interface_name]
            for index, row in aliases_rows.iterrows():
                alias = row['<Alias>'] if '<Alias>' in row else None
                if alias is not None:
                    split = alias.split('.')
                    newalias = split[0] + self.domain
                    IPAList.append(newalias)
            
        return IPAList

    #NIC, Network Interface Card type
    def InterfaceCard(self, device_name):
        IFcard = []

        device_rows = self.devicescsvfile[self.devicescsvfile['<Device>'] == device_name]

        for index, row in device_rows.iterrows():
            IFCards = {
                    'HardwareAddress': self.MACaddress(device_name)['OnboardMAC1'] if self.MACaddress(device_name)['OnboardMAC1'] != None else self.MACaddress['OnboardMAC2'],
                    'CardType': row['<CardType>'] if '<CardType>' in row else "Ethernet"
                    }

            IFcard.append(IFCards)
        return IFcard
    
    #to generate a list of interfaces for a specific device
    # def interface_list(self, device_name):
    #     interfaceslist = []
    #     device_rows = self.interfacescsvfile[self.interfacescsvfile['<Device>'] == device_name]

    #     for index, row in device_rows.iterrows():
    #         interface_name = row['<IFName>'] if '<IFName>' in row else None
    #         if pd.isna(interface_name):
    #             interface_name = f"{device_name}.cms"
    #             interfaceslist.append(interface_name)
    #         else:
    #             interfaceslist.append(interface_name)
    #     return interfaceslist

    #Device input type for inputting device information into lanDB
    #If device name is not defined thne it gives a list of all device information from all devices in 'devices.csv'
    def DeviceInput(self, device_name=None):
        required_columns = {'<Device>', '<Manufacturer>', '<model>'}

        for file_path in self.file_list:
            try:
                csvfile = pd.read_csv(file_path, comment='#')
                if not required_columns.issubset(csvfile.columns):
                    continue

                if device_name is None:
                    device_names = csvfile['<Device>'].unique()
                    for device in device_names:
                        device_rows = csvfile[csvfile['<Device>'] == device]
                        for index, row in device_rows.iterrows():
                            devinp = {
                                'DeviceName': device,
                                'Location': self.location(device),
                                'Zone': row['<Zone>'] if '<Zone>' in row else None,
                                'Manufacturer': row['<Manufacturer>'],
                                'Model': row['<model>'],
                                'Description': row['<Description>'] if '<Description>' in row else None,
                                'Tag': row['<Tag>'] if '<Tag>' in row else None,
                                'SerialNumber': row['<SerialNumber>'] if '<SerialNumber>' in row else None,
                                'OperatingSystem': self.OperatingSystem(device),
                                'InventoryNumber': row['<InventoryNumber>'] if '<InventoryNumber>' in row else None,
                                'LandbManagerPerson': self.PersonInput(device) if self.PersonInput != None else None,
                                'ResponsiblePerson': self.PersonInput(device),
                                'UserPerson': self.PersonInput(device) if self.PersonInput != None else None,
                                'HCPResponse': row['<HCPResponse>'] if '<HCPResponse>' in row else None,
                                'IPv6Ready': row['<IPv6Ready>'] if '<IPv6Ready>' in row else None,
                                'ManagerLocked': row['<ManagerLocked>'] if '<ManagerLocked>' in row else None,
                            }
                else:
                    device_rows = csvfile[csvfile['<Device>'] == device_name]
                    for index, row in device_rows.iterrows():
                        devinp = {
                            'DeviceName': device_name,
                            'Location': self.location(device_name),
                            'Zone': row['<Zone>'] if '<Zone>' in row else None,
                            'Manufacturer': row['<Manufacturer>'],
                            'Model': row['<model>'],
                            'Description': row['<Description>'] if '<Description>' in row else None,
                            'Tag': row['<Tag>'] if '<Tag>' in row else None,
                            'SerialNumber': row['<SerialNumber>'] if '<SerialNumber>' in row else None,
                            'OperatingSystem': self.OperatingSystem(device_name),
                            'InventoryNumber': row['<InventoryNumber>'] if '<InventoryNumber>' in row else None,
                            'LandbManagerPerson': self.PersonInput(device_name) if self.PersonInput != None else None,
                            'ResponsiblePerson': self.PersonInput(device_name),
                            'UserPerson': self.PersonInput(device_name) if self.PersonInput != None else None,
                            'HCPResponse': row['<HCPResponse>'] if '<HCPResponse>' in row else None,
                            'IPv6Ready': row['<IPv6Ready>'] if '<IPv6Ready>' in row else None,
                            'ManagerLocked': row['<ManagerLocked>'] if '<ManagerLocked>' in row else None,
                        }

            except Exception as e:
                print(f"An error occurred while processing file {file_path}: {e}")
    
        return devinp

    #    
    # def Interfaces(self, device_name):
    #     IF = []
    #     # interface_list = self.interface_list(device_name)
    #     # IF.append(f"Interfaces: {interface_list}")
                
    #     device_rows = self.interfacescsvfile[self.interfacescsvfile['<Device>'] == device_name]
                
    #     for index, row in device_rows.iterrows():
    #             interface_name = row['<IFName>'] if '<IFName>' in row and not pd.isna(row['<IFName>']) else device_name + self.domain
    #             Interface = {
    #                         'InterfaceName': interface_name,
    #                         'IPAlais': self.IPAliasList(device_name= device_name, interface_name= interface_name) if self.IPAliasList(device_name= device_name, interface_name= interface_name) != '[]' else None,
    #                         'Location': self.location(device_name), 
    #                         'OutletLabel': row['<OutletLabel>'] if '<OutletLabel>' in row else "AUTO",
    #                         'SecurityClass': row['<SecurityClass>'] if '<SecurityClass>' in row else "USER",
    #                         'InternetConnectivity': row['<InternetConnectivity>'] if '<InternetConnectivity>' in row else None,
    #                         'Medium': self.get_medium_description(row['<Medium>']) if '<Medium>' in row else "GIGABITETHERNET",
    #                         'SwitchName': row['<Switch>'],
    #                         'PortNumber': row['<Port>'],
    #                         'CableNumber': row['<Cable>'],
    #                         'IP': row['<IP>'] if '<IP>' in row else None,
    #                         'IPv6': row['<IPv6>'] if '<IPv6>' in row else None,
    #                         'ServiceName': row['<ServiceName>'] if '<Servicename>' in row else None
    #                     }
    #             IF.append(Interface)
    #     return IF

    def interfacenames(self, IFname, device_name):
        if IFname == device_name:
            updatedname = device_name + self.domain
        else:
            splitIF = IFname.split('.')
            if len(splitIF) == 3:
                updatedname = f"{splitIF[0]}-{splitIF[1]}--{splitIF[2]}.cern.ch"
            else:
                updatedname = device_name + self.domain
        return updatedname
    
    def BulkInterface(self, device_name): 
        interfaces = []               
        device_rows = self.interfacescsvfile[self.interfacescsvfile['<Device>'] == device_name]
                
        for index, row in device_rows.iterrows():
                intname = row['<IFName>'] if '<IFName>' in row and not pd.isna(row['<IFName>']) else device_name
                interface_name = self.interfacenames(intname, device_name)
                BInterface = {
                            'InterfaceName': interface_name,
                            'IPAliases': self.IPAliasList(device_name= device_name) if self.IPAliasList(device_name= device_name) != '[]' else None,
                            'Location': self.location(device_name), 
                            'OutletLabel': row['<OutletLabel>'] if '<OutletLabel>' in row else "AUTO",
                            'SecurityClass': row['<SecurityClass>'] if '<SecurityClass>' in row else "USER",
                            'InternetConnectivity': row['<InternetConnectivity>'] if '<InternetConnectivity>' in row else False,
                            'Medium': self.get_medium_description(row['<Speed>']) if '<Speed>' in row else "GIGABITETHERNET",
                            'SwitchName': row['<Switch>'],
                            'PortNumber': row['<Port>'],
                            'CableNumber': row['<Cable>'],
                            'IP': row['<IP>'] if '<IP>' in row else None,
                            'IPv6': row['<IPv6>'] if '<IPv6>' in row else None,
                            'ServiceName': row['<ServiceName>'] if '<Servicename>' in row else None
                        }
                interfaces.append(BInterface)
        return interfaces

    #Returns all device info, deviceinput, bulkinterfaces, NICs
    def search_device_info(self, device_name = None):

        alldevice_info = []

        if device_name == None:
            device_names = self.devicescsvfile['<Device>'].unique()
            
            for device_name in device_names:

                device_info = {
                    'DeviceInput': self.DeviceInput(device_name),
                    'BulkInterface': self.BulkInterface(device_name),
                    'Interfaces': self.Interfaces(device_name),
                    'NetworkInterfaceCards': self.InterfaceCard(device_name)

                }
                alldevice_info.append(device_info)
        
        else:
            device_info = {
                    'DeviceInput': self.DeviceInput(device_name),
                    'BulkInterface': self.BulkInterface(device_name),
                    'Interfaces': self.Interfaces(device_name),
                    'InterfaceCards': self.InterfaceCard(device_name)

                }
        
            alldevice_info.append(device_info)

        return alldevice_info
    
    #Retreives MAC addresses from device names through their serial number
    def MACaddress(self, device_name):
        deviceserial = self.devicescsvfile[self.devicescsvfile['<Device>'] == device_name]
        serialnumber = deviceserial['<Serial>'].values[0]
        try: 
            mac = self.serials[self.serials['<Serial>'] == serialnumber]
            if mac.empty:
                print(f"serial number not found in serials CSV file")
                return None
            macaddresses = {
                'OnboardMAC1': mac['<OnboardMAC1>'].values[0] if '<OnboardMAC1>' in mac and not pd.isna(mac['<OnboardMAC1>'].values[0]) else None,
                'OnboardMAC2': mac['<OnboardMAC2>'].values[0] if '<OnboardMAC2>' in mac and not pd.isna(mac['<OnboardMAC2>'].values[0]) else None,
                'IPMIMAC': mac['<IPMIMAC>'].values[0] if '<IPMIMAC>' in mac and not pd.isna(mac['<IPMIMAC>'].values[0]) else None
                    }
            return macaddresses
        except Exception as e:
            print(f"Serial number {serialnumber} for device {device_name} is not found or does not have a MAC address: {e}")
            
         

''' for example '''
# bramtype = CSVtypes()
# device = 'spare-c2d11-39-01'
# print(bramtype.Interfaces('spare-c2d11-40-01'))
# print(bramtype.DeviceInput())
# print('')
# print(bramtype.BulkInterface(device))
# print('')
# print(bramtype.Interfaces(device))
# print('')
# print(bramtype.InterfaceCard(device))

# print(bramtype.InterfaceCard(device))