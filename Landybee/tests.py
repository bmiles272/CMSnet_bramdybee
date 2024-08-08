from CMSNet_ng_add import cmsnet_add
from CNMSNet_ng_check import cmsnet_check
from CSVExtracttoDict import CSVtypes
import bramdybee
from CMSNet_ng_delete import cmsnet_delete
import os
from ConvSUDStoDict import SUDS2Dict
import json
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()


s2d = SUDS2Dict()

device = 'spare-c2d11-40-01'
# switch = 'D3562-1V-IP55-SHPYL-1414'
# print(extract_dict.DeviceInput(device))
# print(extract_dict.InterfaceCard(device))
# print(extract_dict.BulkInterface(device))
# print(bramdb.landb.getSwitchInfo(switch))

checker = cmsnet_check(device)
checker()

# delete = cmsnet_delete(device)
# delete()

# add = cmsnet_add(device)
# add()







