import pandas as pd
from typing import List
from os import listdir
from os.path import isfile
import os
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
        file_devicescsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/cms', 'devices.csv'))
        file_aliasescsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/cms', 'aliases.csv'))
        file_interfacescsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/cms', 'interfaces.csv'))
        file_networkscsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/cms', 'networks.csv'))
        file_networks_routescsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/cms', 'networks_routes.csv'))
        file_switches_special_portscsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/cms', 'switches_special_ports.csv'))


        self.devicescsvfile = pd.read_csv(file_devicescsv, comment='#')
        self.aliasescsvfile = pd.read_csv(file_aliasescsv, comment='#')
        self.interfacescsvfile = pd.read_csv(file_interfacescsv, comment='#')
        self.networkscsvfile = pd.read_csv(file_networkscsv, comment='#')
        self.networks_routescsvfile = pd.read_csv(file_networks_routescsv, comment='#')
        self.switches_special_portscsvfile = pd.read_csv(file_switches_special_portscsv, comment='#')

        if file_list is None:
            self.file_list = [file_devicescsv, file_aliasescsv, file_interfacescsv, file_networkscsv, file_networks_routescsv, file_switches_special_portscsv]  # Default file list
        else:
            self.file_list = file_list

        #import serial files and combine them since they have equal columns
        serialpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/serial'))

        serial = [f for f in listdir(serialpath) if isfile(os.path.join(serialpath, f))]

        serialfiles = [os.path.join(serialpath, file) for file in serial]

        readserial = [pd.read_csv(file, comment= '#') for file in serialfiles]

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
        self.cmsdomain = 'cms'
        self.cerndomain = '.cern.ch'
        self.subdomain_delimiter = '-'
        self.domain_delimiter = '--'

    #Extract keys and input true values from medium and speed tables.
    def get_medium_description(self, key):
        cleaned_key = str(key).strip()
        return self.mediums.get(cleaned_key, "Unknown medium")

    def get_speed_value(self, key):
        cleaned_key = str(key).strip()
        return self.speeds.get(cleaned_key, "Unknown speed")

    #location dictionary, pointing to location of device in building, floor, room format
    def location(self, device_name):
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

        return location

    #person input dictionary points to owner of device and their information
    def PersonInput(self, device_name):

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
                        
        return PersonInputs

    def OperatingSystem(self, device_name):
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
        
        return OpSys
    
    #IP alias list, as a device can have more than 1 interface each interface can have its own alias
    def IPAliasList(self, device_name = None, interface_name = None):
        IPAList = []
        device_rows = self.aliasescsvfile[self.aliasescsvfile['<Device>'] == device_name]

        if interface_name == None:
            for index, row in device_rows.iterrows():
                alias = row['<Alias>'] if '<Alias>' in row else None
                if alias is not None:
                    split = alias.split('.')
                    newalias = split[0] + self.domain_delimiter + self.cmsdomain + self.cerndomain
                    IPAList.append(newalias)
        else:
            aliases_rows = device_rows[device_rows['<IFName>'] == interface_name]
            for index, row in aliases_rows.iterrows():
                alias = row['<Alias>'] if '<Alias>' in row else None
                if alias is not None:
                    split = alias.split('.')
                    newalias = split[0] + self.domain_delimiter + self.cmsdomain + self.cerndomain
                    IPAList.append(newalias)
            
        return IPAList

    #NIC, Network Interface Card type
    def InterfaceCard(self, device_name):
        IFcard = []

        device_rows = self.devicescsvfile[self.devicescsvfile['<Device>'] == device_name]

        for index, row in device_rows.iterrows():
            try:
                mac_info = self.MACaddress(device_name)
                if mac_info is not None:
                    hw_address1 = mac_info.get('OnboardMAC1') or mac_info.get('OnboardMAC2')
                    hw_address = hw_address1.replace(":", "-")
                else:
                    hw_address = None
            except Exception as e:
                print(f"MAC address for device {device_name} could not be found in the CMS csv files. Exception: {e}")
                hw_address = None

            IFCards = {
                    'HardwareAddress': hw_address,     
                    'CardType': row['<CardType>'] if '<CardType>' in row else "Ethernet"
                    }

            IFcard.append(IFCards)
        return IFcard
    
    def IPMIinterfacecard(self, device_name):
        # Initialize IFCard outside the try-except block
        IFCard = {
            'HardwareAddress': None,
            'CardType': "Ethernet"
        }
        
        try:
            mac_info = self.MACaddress(device_name)
            ipmimac = mac_info.get('IPMIMAC')
            
            if ipmimac is not None:
                IFCard['HardwareAddress'] = ipmimac
            else:
                IFCard['HardwareAddress'] = None
                
        except Exception as e:
            print(f"MAC address for device {device_name} could not be found in the CMS csv files. Exception: {e}")

        return IFCard
    
    #generate a list of interface cards, device NIC and ipmi NIC
    def CombinedInterfaceCards(self, device_name):
        # Initialize the list to store the two dictionaries
        interface_cards = []

        # Process for InterfaceCard
        ifcard_list = []
        device_rows = self.devicescsvfile[self.devicescsvfile['<Device>'] == device_name]
        mac_info = self.MACaddress(device_name)  #obtains mac addresses from device name using serial

        for index, row in device_rows.iterrows():
            try:
                if mac_info is not None:
                    hw_address1 = mac_info.get('OnboardMAC1') or mac_info.get('OnboardMAC2')
                    hw_address = hw_address1.replace(":", "-") if hw_address1 else None
            except Exception as e:
                print(f"MAC address for device {device_name} could not be found in the CMS csv files. Exception: {e}")
                hw_address = None

            ifcard_list.append({
                'HardwareAddress': hw_address,
                'CardType': row['<CardType>'] if '<CardType>' in row else "Ethernet"
            })

        # Process for IPMIinterfacecard
        try:
            ipmimac = mac_info.get('IPMIMAC')
            if ipmimac is not None:
                ipmimac_format = ipmimac.replace(":", "-") if ipmimac else None

                ipmi_card = {
                    'HardwareAddress': ipmimac_format,
                    'CardType': "Ethernet"
                }
            else:
                ipmi_card = {
                    'HardwareAddress': None,
                    'CardType': "Ethernet"
                }
        except Exception as e:
            print(f"MAC address for device {device_name} could not be found in the CMS csv files. Exception: {e}")

        # Append both dictionaries to the list
        interface_cards.extend(ifcard_list)
        interface_cards.append(ipmi_card)

        return interface_cards
        
    # to generate a list of interfaces for a specific device
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

    #Device input type for inputting device information into lanDB
    #If device name is not defined thne it gives a list of all device information from all devices in 'devices.csv'
    def DeviceInput(self, device_name=None):
        required_columns = {'<Device>', '<Manufacturer>', '<model>'}
        devinp = None
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
                                'UserPerson': self.PersonInput(device) if '<MainUser>' in row and not 'Main User' else None,
                                'HCPResponse': True if '<ITDHCP>' in row else False, #if something present then true
                                'IPv6Ready': True if '<IPv6Ready>' in row else False,
                                'ManagerLocked': True if '<ManagerLocked>' in row else False, #same here for boolean
                            }
                else:
                    device_rows = csvfile[csvfile['<Device>'] == device_name]
                    if device_rows.empty:
                        raise Exception("Device not found in devices.csv and so cannot be uploaded")
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
                            'UserPerson': None,
                            'HCPResponse': True if '<ITDHCP>' in row else False,
                            'IPv6Ready': True if '<IPv6Ready>' in row else False,
                            'ManagerLocked': True if '<ManagerLocked>' in row else False,
                        }

            except Exception as e:
                print(f"An error occurred while processing file {file_path}: {e}")
        return devinp
        


    # generates interface names when uploading to lanDB
    def interfacenames(self, IFname, device_name):
        if IFname != None:
            split_IFname = IFname.split('.')
            if len(split_IFname) == 1:   #for gpn domain (.cern.ch)
                updatedname = device_name
            if len(split_IFname) == 2:     #for any subdomains within cms (-subdomain--cms)
                updatedname = device_name + self.subdomain_delimiter + split_IFname[1] + self.domain_delimiter + self.cmsdomain
        elif IFname == None:
            updatedname = device_name + self.domain_delimiter + self.cmsdomain #devices in cms domain with no subdomain (--cms)
        return updatedname + self.cerndomain
    
    def BulkInterface(self, device_name): 
        interfaces = []               
        device_rows = self.interfacescsvfile[self.interfacescsvfile['<Device>'] == device_name]
                
        for index, row in device_rows.iterrows():
                intname = row['<IFName>'] if '<IFName>' in row and not pd.isna(row['<IFName>']) else None
                interface_name = self.interfacenames(intname, device_name)
                BInterface = {
                            'InterfaceName': interface_name,
                            'IPAliases': self.IPAliasList(device_name= device_name, interface_name= interface_name) if self.IPAliasList(device_name= device_name, interface_name= interface_name) != '[]' else None,
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
                            'ServiceName': row['<ServiceName>'] if '<ServiceName>' in row and not pd.isna(row['<ServiceName>']) else None
                        }
                interfaces.append(BInterface)
        return interfaces
    
    #Retreives MAC addresses from device names through their serial number
    def MACaddress(self, device_name):
        deviceserial = self.devicescsvfile[self.devicescsvfile['<Device>'] == device_name]
        serialnumber = deviceserial['<Serial>'].values[0]
        try: 
            mac = self.serials[self.serials['<Serial>'] == serialnumber]  #all the serial files concatted into one
            if mac.empty:
                return None
            macaddresses = {
                'OnboardMAC1': mac['<OnboardMAC1>'].values[0] if '<OnboardMAC1>' in mac and not pd.isna(mac['<OnboardMAC1>'].values[0]) else None,
                'OnboardMAC2': mac['<OnboardMAC2>'].values[0] if '<OnboardMAC2>' in mac and not pd.isna(mac['<OnboardMAC2>'].values[0]) else None,
                'IPMIMAC': mac['<IPMIMAC>'].values[0] if '<IPMIMAC>' in mac and not pd.isna(mac['<IPMIMAC>'].values[0]) else None
                    }
            return macaddresses
        except Exception as e:
            print(f"Serial number {serialnumber} for device {device_name} is not found or does not have a MAC address: {e}")