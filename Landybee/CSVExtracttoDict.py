import os
import pandas as pd
from typing import Self

class bramtypes:

    def __init__(self, files) -> None:
        if not files:
            raise ValueError("Undefined file name")

        for file in files:
            if not os.path.isfile(file):
                raise FileNotFoundError(f"Failed to open locations file {file}")
        
        self.csvfile = pd.read_csv(file, comment='#')
        

    def location(self):
        locations = []

        required_columns = {'<Device>', '<building>', '<floor>', '<room>'}
        if not required_columns.issubset(self.csvfile.columns):
            raise ValueError("One or more required columns are missing in file")

        for index, row in self.csvfile.iterrows():
            location = {
                    'DeviceName': row['<Device>'],
                    'Building': row['<building>'],
                    'Floor': row['<floor>'],
                    'Room': row['<room>']
                }

            locations.append(location)

        return locations

    def PersonInput(self):
        PersonInput = []

        for index, row in self.csvfile.iterrows():
            PersonInputs = {
                    'Name': row['<Name>'] if '<Name>' in row else None,
                    'FirstName': row['<FirstName>'] if '<FirstName>' in row else None,
                    'Department': row['<Department>'] if '<Department>' in row else None,
                    'Group': row['<Group>'] if '<Group>' in row else None,
                    'PersonID': row['<PersonID>'] if '<PersonID>' in row else None
                }

            PersonInput.append(PersonInputs)
        return PersonInput

    def OperatingSystem(self):
        OS = []

        required_columns = {'<OS>', '<OSversion>'}
        if not required_columns.issubset(self.csvfile.columns):
            raise ValueError("One or more required columns are missing in file")

        for index, row in self.csvfile.iterrows():
            OpSys = {
                    'Name': row['<OS>'],
                    'Version': row['<OSversion>']
                }

            OS.append(OpSys)
        return OS

    def InterfaceCard(self):
        IFcard = []

        required_columns = {'<>', '<>'}
        if not required_columns.issubset(self.csvfile.columns):
            raise ValueError("One or more required columns are missing in file")

        for index, row in self.csvfile.iterrows():
            IFCards = {
                    'HardwareAddress': row['<>'],
                    'CardType': row['<>']
                }

            IFcard.append(IFCards)
        return IFcard

    def DeviceInput(self):
        deviceinput = []

        required_columns = {'<Device>', '<Manufacturer>', '<model>'}
        if not required_columns.issubset(self.csvfile.columns):
            raise ValueError("One or more required columns are missing in file")

        for index, row in self.csvfile.iterrows():
            devinp = {
                    'DeviceName': row['<Device>'],
                    'Location': self.location()[0],
                    'Zone': row['<Zone>'] if '<Zone>' in row else None,
                    'Manufacturer': row['<Manufacturer>'],
                    'Model': row['<model>'],
                    'Description': row['<Description>'] if '<Description>' in row else None,
                    'Tag': row['<Tag>'] if '<Tag>' in row else None,
                    'SerialNumber': row['<>'] if '<>' in row else None,
                    'OperatingSystem': self.OperatingSystem()[0],
                    'InventoryNumber': row['<>'] if '<>' in row else None,
                    'LandbManagerPerson': self.PersonInput()[0] if self.PersonInput != None else None,
                    'ResponsiblePerson': self.PersonInput()[0],
                    'UserPerson': self.PersonInput()[0] if self.PersonInput != None else None,
                    'HCPResponse': row['<>'] if '<>' in row else None,
                    'IPv6Ready': row['<>'] if '<>' in row else None,
                    'ManagerLocked': row['<>'] if '<>' in row else None,
                }

            deviceinput.append(devinp)
        return deviceinput
    
    def BulkInterface(self):
        BulkIF = []

        required_columns = {'<OutletLabel>', '<SecurityClass>', '<InternetConnectivity>', '<Medium>', '<SwicthName>', '<PortNumber>', '<PortName>', '<CableNumber>'}
        if not required_columns.issubset(self.csvfile.columns):
            raise ValueError("One or more required columns are missing in file")

        for index, row in self.csvfile.iterrows():
            BInterface = {
                    'InterfaceName': row['<>'] if '<>' in row else None,
                    'IPAlaises': list(row['<>']) if '<>' in row else None,
                    'Location': self.location(), 
                    'OutletLabel': row['<>'],
                    'SecurityClass': row['<>'],
                    'InternetConnectivity': row['<Description>'],
                    'Medium': row['<>'],
                    'SwitchName': row['<>'],
                    'PortNumber': row['<>'],
                    'CableNumber': row['<>'],
                    'IP': row['<>'] if '<>' in row else None,
                    'IPv6': row['<>'] if '<>' in row else None,
                    'ServiceName': row['<>'] if '<>' in row else None
                }

            BulkIF.append(BInterface)
        return BulkIF


#to create dict in the format needed by landybee functions do the following
#list files
# file_paths = ['data/cms/devices.csv']

#create instance of bramtypes class
# bram = bramtypes(file_paths)

#call functions
# locations = bram.location()
