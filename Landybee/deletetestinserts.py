'''
Quick script to delete any test devices inserted into the lanDB database.
'''

import bramdybee
bramdb = bramdybee.bramDB()
test = 'spare-c2d11-40-01'

bramdb.landb.deviceRemoveBulkInterface(test, 'spare-c2d11-40-01--cms.cern.ch')
bramdb.landb.deviceRemoveBulkInterface(test, 'SPARE-C2D11-40-01.CERN.CH')

bramdb.landb.deviceRemove(test)
