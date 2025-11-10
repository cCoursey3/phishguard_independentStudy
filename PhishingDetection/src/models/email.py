class Email:
    def __init__(self, sender, recipient, subject, body):
        #self.sender = self.Sender(sender)
        self.sender = self.Sender("", sender)
        self.subject = subject
        #self.recipient = self.Recipient(recipient)
        self.recipient = self.Recipient("", recipient)
        self.body = body
        self.links = self.Links()
        #self.Images = self.Images()
    
    
    def __str__(self):
        return f"{self.sender}\n{self.subject}\n{self.recipient}\n\n{self.body}"
    '''
        Create Inner Classes relevant to creating an email
    '''
    class Sender:
        def __init__(self, name, email):
            self.name = name
            self.email = email
            
        @property
        def name(self):
            return self._name
        
        @name.setter
        def name(self, name):
            self._name = name
            
        @property
        def email(self):
            return self._email
        
        @email.setter
        def email(self, email):
            self._email = email
            
            
        def __str__(self):
            if self.name == self.email:
                return f'From: {self.name}'
            else:
                return f'From: {self.name} <{self.email}>'
            
            
            
    class Recipient:
        def __init__(self, name, email):
            self.name = name
            self.email = email
            
        @property
        def name(self):
            return self._name
        
        @name.setter
        def name(self, name):
            self._name = name
            
        @property
        def email(self):
            return self._email
        
        @email.setter
        def email(self, email):
            self._email = email
            
            
        def __str__(self):
            if self.name == self.email:
                return f'To: {self.name}'
            else:
                return f'To: {self.name} <{self.email}>'
            
    
    
    class Links:
        def __init__(self):
            self.links = []
            
        def add_link(self, link):
            self.links.append(link)
        
        def __iter__(self):
            return iter(self.links)
            
        
        class Link:
            def __init__(self, link_address, description):
                self.link_address = link_address
                self.description = description
                
            @property
            def link_address(self):
                return self._link_address
            
            @link_address.setter
            def link_address(self, link_address):
                self._link_address = link_address
            
            @property
            def description(self):
                return self._description
            
            @description.setter
            def description(self, description):
                self._description = description
                
            def __str__(self):
                return f'Link for {self.description} via {self.link_address}'
    
    
    
'''    class Images:
        def __init__(self):
            self.images = []
            
        def add_image(self, i):
            self.image.append(i)
        
        def __iter__(self):
            return iter(self.images)
        '''