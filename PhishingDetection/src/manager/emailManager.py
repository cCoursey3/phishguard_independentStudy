import mysql.connector

class EmailManager:
    def __init__(self, service, email, message_id):
        print("first here")
        self.service = service
        self.email = email
        self.message_id = message_id
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="manager",
            password="gl33bieWeedyK!tty",
            database="user_db"
        )
        self.cursor = self.db_connection.cursor()
        
    @property
    def service(self):
        return self._service
    
    @service.setter
    def service(self, s):
        self._service = s
        
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, b):
        self._email = b
        
    @property
    def message_id(self):
        return self._message_id
    
    @message_id.setter
    def message_id(self, m):
        self._message_id = m
        
        
        
    def add_to_database(self, header, body):
        sender = header[0]
        subject = header[1]
        recipient = header[2]
        full_header = ', '.join(header)
        try: 
            sql = "INSERT INTO email_messages (sender, recipient, subject, full_header, body, message_id) VALUES (%s, %s, %s, %s,%s,%s)"
            values = (sender, recipient, subject, full_header, body, self.message_id)
            self.cursor.execute(sql, values)
            self.db_connection.commit()
        except mysql.connector.Error as err:
                print(f"Error adding owner to database: {err}")
                self.db_connection.rollback() 
        
    

    
    