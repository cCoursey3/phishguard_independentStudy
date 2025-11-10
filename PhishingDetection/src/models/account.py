class NotSupportedService(Exception):
    pass
class EmptyEmailException(Exception):
    pass


SERVICE_MAP = {
    "gmail": "gmail.com",
    "outlook": "outlook.com",
    "yahoo": "yahoo.com",
    "aol": "aol.com"
}

class Account:
    def __init__(self, service, emailAddress, id=None, access_token = None, refresh_token = None, expiry = None, uri = None):
        self.service = service
        
        if emailAddress is None:
            raise EmptyEmailException("You provided no email address.")
        else:
            self.emailAddress = emailAddress
            
            
        self.active_account = False
        
        if access_token is not None:
            self.access_token = access_token
        else:
            self.access_token = None
        
        if refresh_token is not None:
            self.refresh_token = refresh_token
        else:
            self.refresh_token = None
        
        if expiry is not None:
            self.expiry = expiry
        else:
            self.expiry = None
        
        if uri is not None:
            self.token_uri = uri
        else:
            self.token_uri = None
            
        if id is not None:
            self.id = id
        else:
            self.id = None

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id (self, id):
        self._id = id
    
    @property
    def token_uri(self):
        return self._token_uri
    
    @token_uri.setter
    def token_uri (self, uri):
        self._token_uri = uri
        
    @property
    def expiry(self):
        return self._expiry
    
    @expiry.setter
    def expiry (self, ex):
        self._expiry = ex
        
        
        
    @property
    def refresh_token(self):
        return self._refresh_token
    
    @refresh_token.setter
    def refresh_token (self, token):
        self._refresh_token = token
    
    @property
    def access_token(self):
        return self._access_token
    
    @access_token.setter
    def access_token (self, token):
        self._access_token = token
         
    @property
    def emailAddress(self):
        return self._emailAddress

    @property
    def service(self):
        return self._service
    
    @service.setter
    def service(self, s):
        if s.lower() not in SERVICE_MAP:
            raise NotSupportedService
        self._service = s

    @emailAddress.setter
    def emailAddress(self, address):
        self._emailAddress = address
    
    @property
    def active_account(self):
        return self._active
    
    @active_account.setter
    def active_account(self, status):
        self._active = status
    
    def checkService(cls):
        if cls.service not in SERVICE_MAP:
            return False
        else:
            return True


    def to_json(self):
         return {
            'service': self.service,
            'emailAddress': self.emailAddress,
        }
         

        
    @classmethod
    def from_json(cls, data):
        return cls(
            service=data.get('service'),
            emailAddress=data.get('emailAddress'),
        )
    
    def __str__(self):
        return f"The email service is {self.service}\n The email address is {self.emailAddress}"