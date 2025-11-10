import json
import os



class Reader():
    def __init__(self, file):
        self.file = file
        
    @property
    def file(self):
        return self._file
    
    @file.setter
    def file(self, f):
        self._file = f
        
        
    def load_client_info(self):
        with open(self.file, 'r') as file:
            client_info = json.load(file)
        
        if os.path.basename(self.file) == "credentials.json":
            client_id = client_info['installed']['client_id']
            client_secret = client_info['installed']['client_secret']
        else:
            client_id = client_info['client_id']
            client_secret = client_info['client_secret']
        return client_id, client_secret