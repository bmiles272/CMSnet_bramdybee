from CMSNet_ng_add import add_device
from CSVExtracttoDict import CSVtypes
from bramdybee import bramDB
extract_dict = CSVtypes()
bramdb = bramDB()

device = 'spare-c2d11-35-01'
switch = 'D3562-1V-IP55-SHPYL-1414'
# print(extract_dict.DeviceInput(device))
# print(extract_dict.InterfaceCard(device))
# print(extract_dict.BulkInterface(device))
# print(bramdb.landb.getSwitchInfo(switch))

add = add_device(device)

# add.deviceInsert()
# add.deviceAddCard()
add.deviceAddBulkInterface()