from CMSNet_ng_add import cmsnet_add
from CSVExtracttoDict import CSVtypes
from bramdybee import bramDB
from CMSNet_ng_delete import cmsnet_delete
extract_dict = CSVtypes()
bramdb = bramDB()

device = 'spare-c2d11-40-01'
# switch = 'D3562-1V-IP55-SHPYL-1414'
# print(extract_dict.DeviceInput(device))
# print(extract_dict.InterfaceCard(device))
# print(extract_dict.BulkInterface(device))
# print(bramdb.landb.getSwitchInfo(switch))

# add = cmsnet_add(device)
# add()

delete = cmsnet_delete(device)
delete()
# print(bramdb.landb.getSwitchInfo('D3562-1V-IP56-SHPYL-1514'))