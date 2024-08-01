import pandas as pd
from typing import List
'''
Object which transforms the data from CMS CSV device files into python dictionaries for the types.py file used by landybee in order to
alter LanDB entries. Some types require dictionaries within dictionaries, for example the DeviceInput requires a location 'dictionary' within it.
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
    #Extract keys and input true values from medium and speed tables.
    def get_medium_description(self, key):
        return self.mediums.get(key, "Unknown medium")

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
                        'Name': row['<MainUser>'] if '<MainUser>' in row else None,
                        'FirstName': row['<FirstName>'] if '<FirstName>' in row else None,
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
                    IPAList.append(alias)
        else:
            aliases_rows = device_rows[device_rows['<IFName>'] == interface_name]
            for index, row in aliases_rows.iterrows():
                alias = row['<Alias>'] if '<Alias>' in row else None
                if alias is not None:
                    IPAList.append(alias)
            
        return IPAList

    def InterfaceCard(self, device_name):
        IFcard = []

        for file_path in self.file_list:
            device_rows = self.devicescsvfile[self.devicescsvfile['<Device>'] == device_name]

            for index, row in device_rows.iterrows():
                IFCards = {
                        'HardwareAddress': row['<HardwareAddress>'] if '<HardwareAddress>' in row else None,
                        'CardType': row['<CardType>'] if '<CardType>' in row else "Ethernet"
                    }

                IFcard.append(IFCards)
        return IFcard
    
    def interface_list(self, device_name):
        interfaceslist = []
        device_rows = self.interfacescsvfile[self.interfacescsvfile['<Device>'] == device_name]

        for index, row in device_rows.iterrows():
            interface_name = row['<IFName>'] if '<IFName>' in row else None
            if pd.isna(interface_name):
                interface_name = f"{device_name}.cms"
                interfaceslist.append(interface_name)
            else:
                interfaceslist.append(interface_name)
        return interfaceslist


    def DeviceInput(self, device_name=None):
        deviceinput = []
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
                            deviceinput.append(devinp)
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
                        deviceinput.append(devinp)

            except Exception as e:
                print(f"An error occurred while processing file {file_path}: {e}")
    
        return deviceinput

    
    def Interfaces(self, device_name):
        IF = []
        # interface_list = self.interface_list(device_name)
        # IF.append(f"Interfaces: {interface_list}")
                
        device_rows = self.interfacescsvfile[self.interfacescsvfile['<Device>'] == device_name]
                
        for index, row in device_rows.iterrows():
                interface_name = row['<IFName>'] if '<IFName>' in row and not pd.isna(row['<IFName>']) else device_name + '.cms'
                Interface = {
                            'InterfaceName': interface_name,
                            'IPAlais': self.IPAliasList(device_name= device_name, interface_name= interface_name) if self.IPAliasList(device_name= device_name, interface_name= interface_name) != '[]' else None,
                            'Location': self.location(device_name), 
                            'OutletLabel': row['<OutletLabel>'] if '<OutletLabel>' in row else "AUTO",
                            'SecurityClass': row['<SecurityClass>'] if '<SecurityClass>' in row else "USER",
                            'InternetConnectivity': row['<InternetConnectivity>'] if '<InternetConnectivity>' in row else None,
                            'Medium': self.get_medium_description(row['<Medium>']) if '<Medium>' in row else "GIGABITETHERNET",
                            'SwitchName': row['<Switch>'],
                            'PortNumber': row['<Port>'],
                            'CableNumber': row['<Cable>'],
                            'IP': row['<IP>'] if '<IP>' in row else None,
                            'IPv6': row['<IPv6>'] if '<IPv6>' in row else None,
                            'ServiceName': row['<ServiceName>'] if '<Servicename>' in row else None
                        }
                IF.append(Interface)
        return IF
    
    def BulkInterface(self, device_name):
        BulkIF = []
                
        device_rows = self.interfacescsvfile[self.interfacescsvfile['<Device>'] == device_name]
                
        for index, row in device_rows.iterrows():
                interface_name = row['<IFName>'] if '<IFName>' in row and not pd.isna(row['<IFName>']) else device_name + '.cms'
                BInterface = {
                            'InterfaceName': interface_name,
                            'IPAlais': self.IPAliasList(device_name= device_name) if self.IPAliasList(device_name= device_name) != '[]' else None,
                            'Location': self.location(device_name), 
                            'OutletLabel': row['<OutletLabel>'] if '<OutletLabel>' in row else "AUTO",
                            'SecurityClass': row['<SecurityClass>'] if '<SecurityClass>' in row else "USER",
                            'InternetConnectivity': row['<InternetConnectivity>'] if '<InternetConnectivity>' in row else False,
                            'Medium': self.get_medium_description(row['<Medium>']) if '<Medium>' in row else "GIGABITETHERNET",
                            'SwitchName': row['<Switch>'],
                            'PortNumber': row['<Port>'],
                            'CableNumber': row['<Cable>'],
                            'IP': row['<IP>'] if '<IP>' in row else None,
                            'IPv6': row['<IPv6>'] if '<IPv6>' in row else None,
                            'ServiceName': row['<ServiceName>'] if '<Servicename>' in row else None
                        }
                BulkIF.append(BInterface)
        return BulkIF

    def search_device_info(self, device_name = None):

        alldevice_info = []

        if device_name == None:
            device_names = self.devicescsvfile['<Device>'].unique()
            
            for device_name in device_names:

                device_info = {
                    'DeviceInput': self.DeviceInput(device_name),
                    # 'BulkInterface': self.BulkInterface(device_name),
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

''' checks '''
bramtype = CSVtypes()
device = 'spare-c2d11-39-01'
# print(bramtype.Interfaces('spare-c2d11-40-01'))
# print(bramtype.DeviceInput())
# print('')
print(bramtype.BulkInterface(device))
# print('')
# print(bramtype.Interfaces(device))
# print('')
# print(bramtype.InterfaceCard(device))