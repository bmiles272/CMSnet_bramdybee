import os
import pandas as pd


def location(*files):
    if not files:
        raise ValueError("Undefined file name")

    locations = []

    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Failed to open locations file {file}")

        csvfile = pd.read_csv(file, comment='#')

        required_columns = {'<Device>', '<building>', '<floor>', '<room>'}
        if not required_columns.issubset(csvfile.columns):
            raise ValueError(f"One or more required columns are missing in file {file}")

        for index, row in csvfile.iterrows():
            location = {
                'DeviceName': row['<Device>'],
                'Building': row['<building>'],
                'Floor': row['<floor>'],
                'Room': row['<room>']
            }

            locations.append(location)

    return locations

def PersonInput(*files):
    if not files:
        raise ValueError("Undefined file name")

    PersonInput = []

    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Failed to open locations file {file}")

        csvfile = pd.read_csv(file, comment='#')

        for index, row in csvfile.iterrows():
            PersonInputs = {
                'Name': row['<Name>'] if '<Name>' in row else None,
                'FirstName': row['<FirstName>'] if '<FirstName>' in row else None,
                'Department': row['<Department>'] if '<Department>' in row else None,
                'Group': row['<Group>'] if '<Group>' in row else None,
                'PersonID': row['<PersonID>'] if '<PersonID>' in row else None
            }

            PersonInput.append(PersonInputs)
    return PersonInput

def OperatingSystem(*files):
    if not files:
        raise ValueError("Undefined file name")

    OS = []

    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Failed to open locations file {file}")

        csvfile = pd.read_csv(file, comment='#')

        required_columns = {'<OS>', '<OSversion>'}
        if not required_columns.issubset(csvfile.columns):
            raise ValueError(f"One or more required columns are missing in file {file}")

        for index, row in csvfile.iterrows():
            OpSys = {
                'Name': row['<OS>'],
                'Version': row['<OSversion>']
            }

            OS.append(OpSys)
    return OS

def InterfaceCard(*files):
    if not files:
        raise ValueError("Undefined file name")

    IFcard = []

    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Failed to open locations file {file}")

        csvfile = pd.read_csv(file, comment='#')

        required_columns = {'<>', '<>'}
        if not required_columns.issubset(csvfile.columns):
            raise ValueError(f"One or more required columns are missing in file {file}")

        for index, row in csvfile.iterrows():
            IFCards = {
                'HardwareAddress': row['<>'],
                'CardType': row['<>']
            }

            IFcard.append(IFCards)
    return IFcard

def DeviceInput(*files):
    if not files:
        raise ValueError("Undefined file name")

    deviceinput = []

    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Failed to open locations file {file}")

        csvfile = pd.read_csv(file, comment='#')

        required_columns = {'<Device>', '<Manufacturer>', '<model>'}
        if not required_columns.issubset(csvfile.columns):
            raise ValueError(f"One or more required columns are missing in file {file}")

        for index, row in csvfile.iterrows():
            devinp = {
                'DeviceName': row['<Device>'],
                'Location': location('data/cms/devices.csv')[0],
                'Zone': row['<Zone>'] if '<Zone>' in row else None,
                'Manufacturer': row['<Manufacturer>'],
                'Model': row['<model>'],
                'Description': row['<Description>'] if '<Description>' in row else None,
                'Tag': row['<Tag>'] if '<Tag>' in row else None,
                'SerialNumber': row['<>'] if '<>' in row else None,
                'OperatingSystem': OperatingSystem('data/cms/devices.csv')[0],
                'InventoryNumber': row['<>'] if '<>' in row else None,
                'LandbManagerPerson': PersonInput('data/cms/devices.csv')[0] if PersonInput != None else None,
                'ResponsiblePerson': PersonInput('data/cms/devices.csv')[0],
                'UserPerson': PersonInput('data/cms/devices.csv')[0] if PersonInput != None else None,
                'HCPResponse': row['<>'] if '<>' in row else None,
                'IPv6Ready': row['<>'] if '<>' in row else None,
                'ManagerLocked': row['<>'] if '<>' in row else None,
            }

            deviceinput.append(devinp)
    return deviceinput

file_paths = ['data/cms/devices.csv']

# Load the locations from the specified CSV files
locations = location(*file_paths)
person = PersonInput(*file_paths)
opsys = OperatingSystem(*file_paths)
devicein = DeviceInput(*file_paths)
# print(locations, person, opsys)
print(devicein[0])