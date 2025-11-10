from PhishingDetection.src.emails.query import Query
import mysql.connector

class Query_Manager():
    def __init__(self, q):
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="manager",
            password="gl33bieWeedyK!tty",
            database="user_db"
        )
        if q is not None:
            self.query = q
        else:
            self.query = None
        self.cursor = self.db_connection.cursor()
    
    def save_to_db(self, account_id):
        print(self.query)
        message_ids_str = ','.join(self.query.message_ids)
        text = self.query.text
        try: # Insert new owner
            sql = "INSERT INTO query (query_text, message_ids, account_id) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (text, message_ids_str, account_id))
            self.db_connection.commit()
            print("Query details saved to database successfully.")
        except mysql.connector.Error as e:
            print(f"Error while connecting to MySQL: {e}")
        finally:
            if self.db_connection.is_connected():
                self.cursor.close()
                self.db_connection.close()
                print("MySQL connection is closed.")
