from datetime import datetime, timedelta
import json
import os

class Credentials():
    def __init__(self, service, credentials = None, 
                 client_id = None, secret = None, 
                 redirect_uri = None, authorization_base_url = None, token_uri = None, 
                 expiry = None, access = None, refresh = None):
        #The service we are making a credential for 
        self.service = service
        
        #the file the credentials can be found in 
        self.credentials_file = None
        self.token_file = None
        
        if credentials is not None:
            self.__dict__.update(credentials.__dict__)
        elif all(var is not None for var in [client_id, secret, redirect_uri, authorization_base_url, token_uri, expiry, access, refresh]):
            # Initialize individual attributes if credentials are not provided
            self.client_id = client_id
            self.client_secret = secret
            self.redirect_uri = redirect_uri
            self.authorization_base_url = authorization_base_url
            self.token_uri = token_uri
            self.expiry = expiry
            
        else: #otherwise, we need to create the new credential       
            self.credentials = None
            if self.service in ["Yahoo", "AOL"]:
                self.credentials_file =r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\yahoo_credentials.json'
                self.scope = ['openid', 'email']
                
                if self.service == "Yahoo":
                    self.token_file = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\yahoo_token.json'
                else:
                    self.token_file = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\aol_token.json'
                
            elif self.service == "Outlook":
                self.credentials_file = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\outlook_credentials.json'
                self.scope = ['https://graph.microsoft.com/Organization.Read.All','openid', 'https://graph.microsoft.com/Directory.Read.All', 
                              'https://graph.microsoft.com/User.ManageIdentities.All', 'https://graph.microsoft.com/Family.Read',
                              'https://graph.microsoft.com/Directory.AccessAsUser.All', 'https://graph.microsoft.com/User.ReadBasic.All',
                              'https://graph.microsoft.com/User.Read.All', 'https://graph.microsoft.com/User.Read', 'email', 'profile', 
                              'https://graph.microsoft.com/User.Export.All', 'https://graph.microsoft.com/Mail.Read', 
                              'https://graph.microsoft.com/User.EnableDisableAccount.All', 'offline_access']
                self.token_file = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\token_outlook.json'
            self.read_credentials()  
        
    def read_credentials(self):
        with open(self.credentials_file, 'r') as file:
            creds = json.load(file)
        self.client_id = creds['client_id']
        self.client_secret = creds['client_secret']
        self.redirect_uri = creds['redirect_uri']
        self.authorization_base_url = creds['authorization_base_url']
        self.token_uri = creds['token_url']
        
           
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])

    
    @property
    def client_id(self):
        return self.__client_id
    
    @client_id.setter
    def client_id(self, value):
        self.__client_id = value
        
    @property
    def client_secret(self):
        return self.__client_secret
    
    @client_secret.setter
    def client_secret(self, value):
        self.__client_secret = value
        
    @property
    def redirect_uri(self):
        return self.__redirect_uri
    
    @redirect_uri.setter
    def redirect_uri(self, value):
        self.__redirect_uri = value
        
    @property
    def authorization_base_url(self):
        return self.__authorization_base_url
    
    @authorization_base_url.setter
    def authorization_base_url(self, value):
        self.__authorization_base_url = value
        
    @property
    def token_uri(self):
        return self.__token_uri
    
    @token_uri.setter
    def token_uri(self, value):
        self.__token_uri = value
        
    @property
    def expiry(self):
        return self.__expiry
    
    @expiry.setter
    def expiry(self, value):
        self.__expiry = value
        
    @property
    def scopes(self):
        return self.__scopes
    
    
    def __str__(self):
        return f"Client ID: {self.client_id}\nRedirect URI: {self.redirect_uri}\nToken URL: {self.token_url}"