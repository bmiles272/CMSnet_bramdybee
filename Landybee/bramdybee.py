'''external authorisation of passkey provided by landybee, writing into .env file for purpose of CMSNet update to python 16/07/2024'''
'''use in CMSNet to not require username and password for every command called'''
'''each passkey is valid for 10 hours, we use 30 minute buffer to make sure'''

from dotenv import load_dotenv, find_dotenv, dotenv_values
import getpass
import os
import time
import os.path as path
import client_bramdybee as landybee

class bramDB():

    def __init__(self, username: str | None = None, password: str | None = None) -> None:
        self.landb = landybee.LanDB(username, password)
        self.authenticate()

    def write_env(self, token) -> str:
        with open('.env', 'w') as file:
            file.write('AUTH_TOKEN=' + token)
        return 'file .env created and token inputted'

    def file_older_than_9half(self, file): 
        '''
        Check whether .env file generated to store the authentication token is older than 9.5 hours.
        '''
        file_time = path.getmtime(file) 
        if ((time.time() - file_time) / 3600 > 9.5):
            return PermissionError('Authentication key is invalid, enter password and username')
        return ((time.time() - file_time) / 3600 < 9.5)
    
    def authenticate(self, file = '.env', username: str | None = None, password: str | None = None):
        '''
        checking authentication token
        '''
        if os.path.exists(file) and self.file_older_than_9half(file):
            load_dotenv(find_dotenv(filename= file))
            token = os.getenv('AUTH_TOKEN')
            self.landb.filltoken(token)
        else:
            print('no valid token present')
            username = input("Enter your username: ")
            password = getpass.getpass("Enter your password: ")
            token = self.landb.getAuthToken(username, password, 'CERN')
            self.write_env(token)
            self.landb.filltoken(token)
            



        
        
    
    



