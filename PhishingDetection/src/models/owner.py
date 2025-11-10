import re
from PhishingDetection.src.manager.accountManager import AccountManager
class InvalidName(Exception):
    pass

class InvalidPIN(Exception):
    pass

class Owner:
    """
    A class to represent the owner of all email accounts
    
    Attributes
    ----------
    firstName: str
        the first name of the owner
    lastName: str
        the last name of the owner
    pin: long
        the "pin" a user sets in order to access their accounts
    """
    def __init__(self, firstName, lastName, pin, bypass_pin_validation=False):
        """
        Args:
            firstName (str): the first name of the owner
            lastName (str): the last name of the owner
            pin (long): a pin or password as defined by the owner
        """
        self.firstName = firstName
        self.lastName = lastName
        if bypass_pin_validation:
            self._pin = pin
        else:
            self.pin = pin  # This will call the setter and perform validation

    @property
    def firstName(self):
        return self._firstName
    
    @firstName.setter
    def firstName(self, value):
        if value is None:
            raise ValueError("First name cannot be None")
        pattern = r"^[A-Za-z]+(['-][A-Za-z]+)*$"
        if re.match(pattern, value) is None:
            raise InvalidName("Invalid name")
        self._firstName = value
    
    @property
    def lastName(self):
        return self._lastName
    
    @lastName.setter
    def lastName(self, value):
        if value is None:
            raise ValueError("Last name cannot be None")
        pattern = r"^[A-Za-z]+(['-][A-Za-z]+)*$"
        if re.match(pattern, value) is None:
            raise InvalidName("Invalid name")
        self._lastName = value
    
    @property
    def pin(self):
        return self._pin
    
    @pin.setter
    def pin(self, value):
        if value is None:
            raise ValueError("PIN cannot be None")
        if len(str(value)) < 4 or len(str(value)) > 6:
            print(len(str(value)))
            raise InvalidPIN("PIN needs to be 4 to 6 characters")
        self._pin = value
    
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id (self, id):
        self._id = id
        
        
    def __str__(self):
        return f"{self.firstName} {self.lastName}"
    
    
