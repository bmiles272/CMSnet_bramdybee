'''external authorisation of passkey provided by landybee, writing into .env file for purpose of CMSNet update to python 16/07/2024'''
'''use in CMSNet to not require username and password for every command called'''
'''each passkey is valid for 10 hours, we use 30 minute buffer to make sure'''

from dotenv import load_dotenv, find_dotenv, dotenv_values
import getpass
import os
import time
import os.path as path
import suds.client
import suds.xsd.doctor
import client_internalmodsv4 as landybee


client = suds.client.Client(
            url="https://network.cern.ch/sc/soap/soap.fcgi?v=6&WSDL",
            doctor=suds.xsd.doctor.ImportDoctor(
                suds.xsd.doctor.Import("http://schemas.xmlsoap.org/soap/encoding/"),
            ),
            cache=None,
        )

class bramDB():
    
    def write_env(token) -> str:
        with open('.env', 'w') as file:
            file.write('AUTH_TOKEN=' + token)
        return 'file .env created and token inputted'

    def file_older_than_9half(file): 
        file_time = path.getmtime(file) 
        if ((time.time() - file_time) / 3600 > 9.5):
            return PermissionError('Authentication key is invalid, enter password and username')
        return ((time.time() - file_time) / 3600 < 9.5)
    
    def check_authentication(file = '.env', username: str | None = None, password: str | None = None):
        landb = landybee.LanDB()
        if os.path.exists(file) and bramDB.file_older_than_9half(file):
            load_dotenv(find_dotenv(filename= file))
            token = os.getenv('AUTH_TOKEN')
            # print(token)
            landb.filltoken(token)
        else:
            print('no valid token present')
            username = input("Enter your username: ")
            password = getpass.getpass("Enter your password: ")    
            token = landb.getAuthToken(username, password, 'CERN')
            bramDB.write_env(token)
            landb.filltoken(token)
            



        
        
    
    



