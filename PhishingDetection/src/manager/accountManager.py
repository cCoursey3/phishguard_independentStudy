import mysql.connector
from PhishingDetection.src.models.account import Account
from PhishingDetection.src.service import *
import json

class AccountNotFound(Exception):
    pass

SERVICE_MAP = {
    "gmail",
    "aol",
    "outlook",
    "yahoo"
}

class AccountManager:
    def __init__(self, owner_id=None):  
        self._accounts = []   
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="manager",
            password="gl33bieWeedyK!tty",
            database="user_db"
        )
        self.cursor = self.db_connection.cursor()
        
        if owner_id is not None:
            self.owner_id = owner_id
            self.load_database()
        else:
            self.owner_id = None
    
    @property
    def owner_id(self):
        return self._owner_id
    
    @owner_id.setter
    def owner_id(self, owner_id):
        self._owner_id = owner_id
        
    def load_database(self):
        try:
            sql = "INSERT INTO account_manager (accounts, owner_id) VALUES (%s, %s)"
            self.cursor.execute(sql, (None, self.owner_id))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection.rollback()
    
    def add_account(self, account, user_id, existing_accounts):
        if account.checkService():
            existing_accounts.append(account)
            self.save_to_database(existing_accounts, user_id)

    def save_to_database(self, accounts, user_id):
        accounts_list = []
        try:
            sql = "UPDATE account_manager SET accounts = %s WHERE owner_id = %s" 
            for account in accounts:
                accounts_list.append(account.to_json())
            accounts_json = json.dumps(accounts_list)
            self.cursor.execute(sql, (accounts_json, user_id))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection.rollback()

    def remove_account(self, account):
        self._accounts.remove(account)
    
    @property
    def accounts(self):
        return self._accounts

    @accounts.setter
    def accounts(self, accounts):
        self._accounts = accounts
        
    def close_connection(self):
        self.cursor.close()
        self.db_connection.close()
    
    def get_manager_id(self, owner_id):
        self.cursor.execute("SELECT ID FROM account_manager WHERE owner_id=%s", (owner_id,))
        result = self.cursor.fetchone()
        return result[0]
    
    def get_accounts_by_id(self, id, owner_id):
        self.cursor.execute("SELECT accounts FROM account_manager WHERE ID = %s AND owner_id = %s", (id, owner_id))
        result = self.cursor.fetchone()
        
        print(f"\n\n\n\n\n\n\n\n\n\n\n\n\n{result}")
        if result:
            accounts_json = result[0]
            if accounts_json is None:
                return []
            else:
                accounts_list = json.loads(accounts_json)
                return [Account.from_json(account) for account in accounts_list]
        return []

