import mysql.connector
from PhishingDetection.src.models.owner import Owner
import hashlib

class OwnerManager:
    def __init__(self):
        self.owners = []
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="manager",
            password="gl33bieWeedyK!tty",
            database="user_db"
        )
        self.cursor = self.db_connection.cursor()

    def get_active_owner(self):
        self.cursor.execute("SELECT * FROM owners WHERE is_active = 1")
        active_owner = self.cursor.fetchone()
        if active_owner:
            owner = Owner(
                firstName=active_owner[1],
                lastName=active_owner[2],
                pin=active_owner[3],  # Adjust column index as per your table structure
                bypass_pin_validation=True# Add other attributes as needed
            )
            return owner
        else:
            return None  # No active owner found
    
    def get_manager_id(self):
        self.cursor.execute("SELECT * FROM owners WHERE is_active = 1")
        active_owner = self.cursor.fetchone()
        if active_owner:
            manager_id = active_owner[5]
        return manager_id
    
    def find_owner(self, ACTIVE_USER, pin):
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        try:
            self.cursor.execute('SELECT * FROM owners WHERE firstName = %s AND lastName = %s AND pin = %s', (ACTIVE_USER.firstName, ACTIVE_USER.lastName, hashed_pin))
            user = self.cursor.fetchone()
            if user:
                return "Success"
            else:
                return "Invalid User Names or PIN"
        except mysql.connector.Error as err:
            print(f"Error finding owner: {err}")
            return err
        
        
        
        
    def checkOwner(self, owner):
        try:
            self.cursor.execute("SELECT ID FROM owners WHERE firstName = %s AND lastName = %s", (owner.firstName, owner.lastName))
            if self.cursor.fetchone() is not None:
                return False
            else:
                return True
        except mysql.connector.Error as err:
            print(f"Error finding owner: {err}")
            return err
        

    def add_owner(self, owner):
        if self.checkOwner(owner):
            self.owners.append(owner)
            self.save_to_database(owner)
            return True
        else:
            return False
            
    def save_to_database(self, owner):
            try: # Insert new owner
                sql = "INSERT INTO owners (firstName, lastName, PIN, is_active) VALUES (%s, %s, %s, %s)"
                values = (owner.firstName, owner.lastName, owner.pin, True)
                self.cursor.execute(sql, values)
                self.db_connection.commit()
                print(f"Owner '{owner.firstName} {owner.lastName}' added to the database.")
            except mysql.connector.Error as err:
                print(f"Error adding owner to database: {err}")
                self.db_connection.rollback()   

        
        
    def remove_owner(self, owner_id):
        # Remove owner from local list
        for owner in self.owners:
            if owner.id == owner_id:
                self.owners.remove(owner)
                break
        
        # Remove owner from database
        try:
            sql = "DELETE FROM owners WHERE ID = %s"
            self.cursor.execute(sql, (owner_id,))
            self.db_connection.commit()
            print(f"Owner with ID {owner_id} removed from database.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection.rollback()

    def set_owner_inactive(self, owner_id):
        try:
            sql = "UPDATE owners SET is_active = %s WHERE ID = %s"
            self.cursor.execute(sql, (False, owner_id))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection.rollback()
            
    def set_owner_active(self, owner_id):
        try:
            sql = "UPDATE owners SET is_active = %s WHERE ID = %s"
            self.cursor.execute(sql, (True, owner_id))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection.rollback()
            
    def get_owner_by_id(self, owner_id):
         # Execute the query to fetch the owner's information
        self.cursor.execute("SELECT * FROM owners WHERE ID = %s", (owner_id,))
        owner_data = self.cursor.fetchone()  # Assuming ID is unique, fetch one row
        if owner_data:
            # Assuming you have an Owner class or similar structure to store owner information
            owner = Owner(firstName=owner_data[1], lastName=owner_data[2], pin=owner_data[3])
            return owner
        else:
            return None
        
        
    def close_connection(self):
        self.cursor.close()
        self.db_connection.close()
        
    def get_owner_id(self, owner):
        self.cursor.execute("SELECT ID FROM owners WHERE firstName = %s AND lastName = %s", (owner.firstName, owner.lastName))
        result =self.cursor.fetchone()
        return result[0]

    def add_manager_id(self, owner_id, manager_id):
        try:
            sql = "UPDATE owners SET account_manager_id = %s WHERE id = %s"
            self.cursor.execute(sql, (manager_id, owner_id))
            self.db_connection.commit()
            self.manager_id = manager_id
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection.rollback()
    