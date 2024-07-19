import landybee
from landybee import types
from typing import Dict

landb = landybee.LanDB(username="", password='')

domain: types.DeviceSearch = {'Domain': "CMS"}

CMSdevices = landb.searchDevice(domain)  #generate list of all dvices in CMS domain

CMSDevicesstring = list(map(str, CMSdevices))   #turn list into array of strings for later use

print(CMSDevicesstring.index('D3VSW-ETH-C2E33-28-01--CMS'))

def split_list(list, stepsize=50):
    return [list[i:i + stepsize] for i in range(0, len(list), stepsize)]  #split list into sets of 50

splitlist = split_list(CMSDevicesstring)

for i, sublist in enumerate(splitlist): 
    '''
    Split all sublists into their own variables.
    '''
    var_name = f'sublist_{i + 1}'
    globals()[var_name] = sublist

def getdeviceinfoCMS():
    '''
    Get device info from landybee and save a file with info of each list
    of 50 devices.
    '''
    for i in range(len(splitlist)):
        var_name = f'sublist_{i + 1}'
        sublist = globals().get(var_name)
        if sublist is not None:
            device_info = landb.getDeviceInfoArray(sublist)

            filename = f'device_info_{i + 1}.txt'
            with open(filename, 'w') as file:
                for info in device_info:
                    file.write(f"{info}\n")
            
            print(f'Device info for sublist {i + 1} saved to {filename}')
        else:
            print(f"Variable {var_name} not found.")

# getdeviceinfoCMS()