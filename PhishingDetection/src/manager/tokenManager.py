from PhishingDetection.src.models.account import Account
import mysql.connector
from mysql.connector import errorcode
from PhishingDetection.src.reader.cred_reader import Reader
from google.oauth2.credentials import Credentials
from datetime import datetime
import os
from PhishingDetection.src.emails.credentials import Credentials as crd
import logging

class TokenManager:
    def __init__(self, account = None):
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="manager",
            password="gl33bieWeedyK!tty",
            database="user_db"
        )
        self.cursor = self.db_connection.cursor()
        if account is not None:
            self.account = account
        else:
            self.account = None
        
    def get_account_by_id(self, id):
        try:
            sql = "SELECT * FROM accounts WHERE id = %s"
            self.cursor.execute(sql, (id,))
            account_data = self.cursor.fetchone()
            if account_data:
                return Account(*account_data)
            return None
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
    
    def get_id_by_account(self, manager_id):
        try:
            sql = "SELECT ID FROM accounts WHERE Service = %s AND Email = %s AND ManagerID = %s"
            self.cursor.execute(sql, (self.account.service, self.account.emailAddress, manager_id))
            id = self.cursor.fetchone()
            return id[0] if id else None
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        
        
    def get_token_id_from_db(self, manager_id, account):
        try:
            # Retrieve all accounts with the same manager_id
            query = "SELECT id, Service, Email FROM accounts WHERE ManagerID = %s"
            print(manager_id)
            self.cursor.execute(query, (manager_id,))
            results = self.cursor.fetchall()

            if len(results) == 1:
                return results[0][0]  # Only one account found, return its ID
            
            # Filter by service
            filtered_by_service = [row for row in results if row[1] == account.service]
            if len(filtered_by_service) == 1:
                return filtered_by_service[0][0]  # Only one service match, return its ID
            
            # Filter by email
            filtered_by_email = [row for row in filtered_by_service if row[2] == account.emailAddress]
            if len(filtered_by_email) == 1:
                return filtered_by_email[0][0]  # Only one email match, return its ID
            
            raise Exception("Unable to uniquely identify the account.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None

    def get_refresh_by_id(self, id):
        try:
            query = "SELECT RefreshToken FROM accounts WHERE id = %s"
            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                raise Exception("No refresh token found for the given ID.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None

    def get_access_by_id(self, id):
        try:
            query = "SELECT AccessToken FROM accounts WHERE id = %s"
            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                raise Exception("No access token found for the given ID.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None
   

    def get_row_by_id(self, id):
        try:
            query = "SELECT AccessToken, RefreshToken, expiry, token_uri, redirect_uri FROM accounts WHERE id = %s"
            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            print(result)
            if result:
                data = {
                    "access_token": result[0],
                    "refresh_token": result[1],
                    "expiry": result[2],
                    "token_uri": result[3],
                    "redirect_uri": result[4]
                }
                return data
            else:
                raise Exception("No access token found for the given ID.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None
       
    def get_creds_from_db(self, id, file):
        row = self.get_row_by_id(id)
        reader = Reader(file)
        file_basename = os.path.basename(file)
        #if we are getting credentials from the db for a gmail account
        if file_basename == "credentials.json":
            return Credentials(
                token=row['access_token'],
                refresh_token=row['refresh_token'],
                token_uri=row['token_uri'],
                client_id=reader.load_client_info()[0],
                client_secret=reader.load_client_info()[1],
                scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/gmail.readonly", "openid"]
            )
        elif file_basename  == "yahoo_credentials.json":
            return crd (
                token=row['access_token'],
                refresh_token=row['refresh_token'],
                redirect_uri = row['redirect_uri'],
                token_uri=row['token_uri'],
                client_id=reader.load_client_info()[0],
                client_secret=reader.load_client_info()[1],
                scopes=['openid', 'email']
            )
        elif file_basename == "outlook_credentials.json":
            return crd (
                token=row['access_token'],
                refresh_token=row['refresh_token'],
                redirect_uri = row['redirect_uri'],
                token_uri=row['token_uri'],
                client_id=reader.load_client_info()[0],
                client_secret=reader.load_client_info()[1],
                scopes=['https://graph.microsoft.com/Organization.Read.All','openid', 'https://graph.microsoft.com/Directory.Read.All', 
                              'https://graph.microsoft.com/User.ManageIdentities.All', 'https://graph.microsoft.com/Family.Read',
                              'https://graph.microsoft.com/Directory.AccessAsUser.All', 'https://graph.microsoft.com/User.ReadBasic.All',
                              'https://graph.microsoft.com/User.Read.All', 'https://graph.microsoft.com/User.Read', 'email', 'profile', 
                              'https://graph.microsoft.com/User.Export.All', 'https://graph.microsoft.com/Mail.Read', 
                              'https://graph.microsoft.com/User.EnableDisableAccount.All', 'offline_access']
            )
            
        
        
            
    def update_tokens_in_db(self, manager_id, account, access_token, refresh_token, expiry, token_uri):
        try:
            query = """
                UPDATE accounts
                SET AccessToken = %s, RefreshToken = %s, expiry = %s, token_uri = %s
                WHERE ManagerID = %s AND Service = %s AND Email = %s
            """
            self.cursor.execute(query, (access_token, refresh_token, expiry, token_uri, manager_id, account.service, account.emailAddress))
            self.db_connection.commit()
            self.cursor.close()
            self.db_connection.close()
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def close_connection(self):
        self.cursor.close()
        self.db_connection.close()
    
    def is_expired(self, id):
        try:
            query = "SELECT expiry FROM accounts WHERE id = %s"
            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            if result:
                expiry = result[0]
                if isinstance(expiry, datetime):
                    expiry_datetime = expiry
                else:
                    expiry_datetime = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
                return datetime.now() >= expiry_datetime
            
        except ValueError as e:
            # Handle the error if the expiry string is not in the correct format
            logging.error(f"Error parsing expiry date: {e}")
            return True
        
    def store_tokens_in_db(self, account, manager_id):
        redirect_uri = None
        if account.service.lower() == "outlook":
            redirect_uri = "https://localhost:8000/PhishingDetect"
        elif account.service.lower() == "gmail":
            redirect_uri = "http://localhost"
        else:
            redirect_uri = "https://localhost:8000/PhishingDetection/Yahoo"
        try:
            # Check if an entry already exists
            check_sql = """
                SELECT COUNT(*) FROM accounts 
                WHERE Service = %s AND Email = %s AND ManagerID = %s
            """
            self.cursor.execute(check_sql, (account.service, account.emailAddress, manager_id))
            result = self.cursor.fetchone()

            if result[0] > 0:
                print("Account with the same Service, Email, and ManagerID already exists. Skipping insertion.")
                return

            # If no matching entry, insert the new account
            insert_sql = """
                INSERT INTO accounts (Service, Email, RefreshToken, AccessToken, ManagerID, expiry, token_uri, redirect_uri)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            account_data = (
                account.service,
                account.emailAddress,
                account.refresh_token,
                account.access_token,
                manager_id,
                account.expiry,
                account.token_uri,
                redirect_uri
            )
            self.cursor.execute(insert_sql, account_data)
            
            self.db_connection.commit()
            print("Account inserted successfully into Token Tables.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")