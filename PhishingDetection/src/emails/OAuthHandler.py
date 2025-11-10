import ssl
import tkinter as tk
from tkinter import messagebox
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import webview
#import logging
import json
from PhishingDetection.src.manager.ownerManager import OwnerManager
from requests_oauthlib import OAuth2Session
from PhishingDetection.src.models.account import Account
from PhishingDetection.src.manager.accountManager import AccountManager
from PhishingDetection.src.manager.tokenManager import TokenManager
from PhishingDetection.src.service.gmailService import GmailService
from PhishingDetection.src.service.yahooService import YahooService
from google_auth_oauthlib.flow import Flow
from PhishingDetection.src.service.outlookService import OutlookService
from PhishingDetection.src.emails.credentials import Credentials


# Setup logging
#logging.basicConfig(level=logging.DEBUG)

SERVICE = None
OWNER = None

class OAuthHandler:
    def __init__(self, controller):
        self.controller = controller
        self.local_server = None
        self.current_service = None
        self.webview_window = None
    def start_local_server(self, service, auth_url, user_id):
        global SERVICE
        global OWNER
        SERVICE = service
        OWNER = user_id
        #logging.debug(f"Starting local server for {SERVICE} with auth_url: {auth_url}")

        class RequestHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.tk_root = kwargs.pop('tk_root', None)
                self.local_server = kwargs.pop('local_server', None)
                self.oauth_handler = kwargs.pop('oauth_handler', None)
                super().__init__(*args, **kwargs)

            def do_GET(self):
                parsed_path = urllib.parse.urlparse(self.path)
                query_params = urllib.parse.parse_qs(parsed_path.query)
                if 'code' in query_params and 'state' in query_params:
                    self.server.auth_code = query_params['code'][0]
                    self.server.state = query_params['state'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    # Close the webview window
                    if self.oauth_handler.webview_window is not None:
                        self.oauth_handler.webview_window.destroy()

                    # Create the countdown window in Tkinter
                    self.create_countdown_window()

            def create_countdown_window(self):
                self.countdown_window = tk.Toplevel(self.tk_root)
                self.countdown_window.title("Authentication Successful")
                self.countdown_window.geometry("300x100")

                label = tk.Label(self.countdown_window, text="Authentication successful.\nThis window will close in 6 seconds.")
                label.pack(expand=True)

                self.seconds = 6
                self.countdown_label = tk.Label(self.countdown_window, text=f"{self.seconds} seconds remaining")
                self.countdown_label.pack()

                self.update_countdown()

            def update_countdown(self):
                if self.seconds > 0:
                    self.seconds -= 1
                    self.countdown_label.config(text=f"{self.seconds} seconds remaining")
                    self.countdown_window.after(1000, self.update_countdown)
                else:
                    self.countdown_window.destroy()
                    self.local_server.shutdown()
                    self.oauth_handler.handle_redirect()

        class CustomHTTPServer(HTTPServer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.auth_code = None
                self.state = None

        def run_server():
            self.local_server = CustomHTTPServer(('localhost', 8000), RequestHandler)
            if SERVICE in ["Yahoo", "Outlook", "AOL"]:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certfile=r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\cert.pem', keyfile=r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\key.pem')
                self.local_server.socket = context.wrap_socket(self.local_server.socket, server_side=True)

            self.local_server.RequestHandlerClass = lambda *args, **kwargs: RequestHandler(
                *args,
                tk_root=self.controller,
                local_server=self.local_server,
                oauth_handler=self,
                **kwargs
            )
            self.local_server.serve_forever()

        threading.Thread(target=run_server).start()

        self.webview_window = webview.create_window(f"{SERVICE} Authentication", auth_url)
        
        # Start the webview
        webview.start(gui='tkinter')

    def handle_redirect(self):
        global SERVICE, OWNER
        auth_code = self.local_server.auth_code
        credentials = None
        if SERVICE == "Gmail":  
            try:
            # Fetch credentials using the authorization code
                flow = Flow.from_client_secrets_file(r'PhishingDetection/config/credentials.json',
                    scopes=[
                        'https://www.googleapis.com/auth/userinfo.email',
                        'https://www.googleapis.com/auth/gmail.readonly',
                        'openid'
                    ],
                    redirect_uri='http://localhost:8000/'
                )
                flow.fetch_token(code=auth_code)
                credentials = flow.credentials
                if credentials:
                    self.current_service = GmailService(credentials=credentials)
                else:
                    raise ValueError("Failed to obtain credentials.")
            except Exception as e:
                #logging.error(f"An error occurred: {e}")
                messagebox.showerror("Error", f"An error occurred: {e}")
            
        elif SERVICE in ["Yahoo", "AOL"]:
            try:
                self.current_service = YahooService(service_name = SERVICE)
                authorization_response = f'https://localhost:8000/?code={auth_code}'
                token = self.current_service.fetch_token(authorization_response)
                credentials = self.current_service.creds
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        elif SERVICE == "Outlook":
            try:
                code_verifier = self.controller.code_verifier  # Retrieve the stored code_verifier
                self.current_service = OutlookService(code_verifier=code_verifier)
                authorization_response = f'https://localhost:8000/?code={auth_code}'
                #logging.debug(f"Authorization response: {authorization_response}")

                token = self.current_service.fetch_token(authorization_response)
                credentials = self.current_service.creds
              

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        
        # Use the authorization code to get the email address
        user_info = self.current_service.get_user_info()
        access, refresh = self.current_service.get_tokens()
        email = user_info['email']
        
           
        print(email)
        #UPDATE THIS SO THAT IT ACTUALLY CREATES AN INSTANCE OF THE SERVICE              
        service = SERVICE.lower()
        # Create the account object
        account = Account(service, email)
        account.access_token = access
        account.refresh_token = refresh
        
        account.expiry = credentials.expiry
        account.token_uri = credentials.token_uri
        
        print(f"{account.access_token}, {account.refresh_token}, {account.expiry}, {account.token_uri}")
        
        token_manager = TokenManager(account)
        account_manager = AccountManager()
        
        id = account_manager.get_manager_id(OWNER)
        
        
        token_manager.store_tokens_in_db(account, id)
        
        
        account_id=token_manager.get_id_by_account(id)
        existing_accounts = account_manager.get_accounts_by_id(id, owner_id=OWNER)
        account_manager.add_account(account=account, user_id=OWNER, existing_accounts=existing_accounts)
        
        
        #Redirect to ScaSn Screen
        self.controller.show_frame("Scan_Screen", account = account, service = self.current_service, user_id = OWNER)

    
