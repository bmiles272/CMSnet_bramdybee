from typing import Any
from CSVExtracttoDict import CSVtypes
import bramdybee
from ConvSUDStoDict import SUDS2Dict
extract_dict = CSVtypes()
bramdb = bramdybee.bramDB()
conv = SUDS2Dict()

yippiee = conv.sobject_to_json(bramdb.landb.getDeviceInfo('KVM-S3562-1-IP157-64--CMS'))

print(yippiee)

'''
plan for creating the check function:
- check if the device exists using getinfo function, if it does not exist then advise going to add function
- start to compare entries:
-- cards
-- interfaces
-- basic device info
-- 'compound' parameters
'''

