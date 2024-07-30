'''
plan:
- call in dicts converted from CSV files (DeviceInput, InterfaceCard, BulkInterface)
-add device class wil contain 3 different functions
-- deviceInsert --> requires DeviceInput dict
-- deviceAddCard --> requires InterfaceCard
-- deviceAddBulkInterface --> requires BulkInterface
- the fucntions will be callable seperately and should gives errors at each point if it fails
'''

from CSVExtracttoDict import CSVtypes
import bramdybee

bramdb = bramdybee.bramDB()
input = CSVtypes.DeviceInput()
print(input)