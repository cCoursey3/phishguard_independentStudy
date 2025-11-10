import requests
from requests_oauthlib import OAuth2Session
from PhishingDetection.src.emails.credentials import Credentials
import json
import os
from datetime import datetime, timedelta
import pkce
import urllib.parse
import logging
from PhishingDetection.src.manager.tokenManager import TokenManager
from google.auth.transport.requests import Request


class OutlookGraphService:
    def __init__(self, headers):
        self.headers = headers

    def get(self, url):
        return requests.get(url, headers=self.headers)

    def post(self, url, data):
        return requests.post(url, headers=self.headers, json=data)


class OutlookService:
    def __init__(self, oauth=None, credentials=None, code_verifier=None):
        self.oauth = None
        self.state = None
        self.service = None
        self.code_verifier = code_verifier  # Initialize code_verifier
        self.token_file = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\token_outlook.json'
        
        if credentials is not None:
            self.creds = credentials
            
        else:
            self.creds = Credentials(service = "Outlook")

        self.initialize_session()

    def initialize_session(self):
        token = self.load_token()
        ##logging.debug(f"Initial scope: {self.creds.scope}")

        if token:
            self.oauth = OAuth2Session(
                self.creds.client_id,
                token=token,
                redirect_uri=self.creds.redirect_uri,
                scope=self.creds.scope
            )
            self.service = self.build_service(token)
        else:
            self.oauth = OAuth2Session(
                self.creds.client_id,
                redirect_uri=self.creds.redirect_uri,
                scope=self.creds.scope
            )
        #logging.debug(f"OAuth2Session initialized with scope: {self.creds.scope}")

    def get_authorization_url(self):
        self.code_verifier, code_challenge = pkce.generate_pkce_pair()

        auth_url, state = self.oauth.authorization_url(
            self.creds.authorization_base_url,
            code_challenge=code_challenge,
            code_challenge_method='S256',
            prompt='consent'  # Force consent
        )
        self.state = state
        #logging.debug(f"Authorization URL: {auth_url}")
        return auth_url

    def fetch_token(self, authorization_response):
        code = urllib.parse.parse_qs(urllib.parse.urlparse(authorization_response).query)['code'][0]
        token_url = self.creds.token_uri
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'client_id': self.creds.client_id,
            'client_secret': self.creds.client_secret,
            'redirect_uri': self.creds.redirect_uri,
            'code': code,
            'grant_type': 'authorization_code',
            'code_verifier': self.code_verifier  # Include code_verifier
        }
        response = requests.post(token_url, headers=headers, data=data)
        token_data = response.json()
        self.save_credentials(token_data)
        return token_data
    
    def save_credentials(self, token_data):
        with open(self.token_file, 'w') as file:
            json.dump(token_data, file)
        self.creds.access_token = token_data.get('access_token')
        self.creds.refresh_token = token_data.get('refresh_token')
        self.creds.expiry = datetime.now() + timedelta(seconds=token_data.get('expires_in'))
            
    def build_service(self, token):
        headers = {'Authorization': f'Bearer {token["access_token"]}'}
        self.service = OutlookGraphService(headers)
        return self.service

    def get_tokens(self):
        return self.creds.access_token, self.creds.refresh_token

    def start_auth_flow(self):
        authorization_url, state = self.get_authorization_url()
        return authorization_url, state

    def list_messages(self, user_id='me', query='', max_results=None):
        """List all messages of the user's mailbox matching the query."""
        print(max_results)
        print(query)
        try:
            endpoint = f'/me/messages?$search="{query}"'
            if max_results is not None:
                endpoint += f"&$top={max_results}"
                
            response = self.service.get(endpoint).json()
            messages = response.get('value', [])
            return messages
        except Exception as e:
            logging.error(f"Error listing messages: {e}")
            raise

    def get_message(self, message_id):
        response = self.service.get(f'https://graph.microsoft.com/v1.0/me/messages/{message_id}')
        return response.json()

    def revoke_token(self, token):
        outlook = OAuth2Session(self.creds.client_id, token=token)
        outlook.post('https://login.microsoftonline.com/common/oauth2/v2.0/logout', token=token)

    def load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as token_file:
                return json.load(token_file)
            
        return None
    

            
    def get_user_info(self):
        """Get user info using the stored credentials."""
        headers = {'Authorization': f'Bearer {self.creds.access_token}'}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        user_info = response.json()
        email = user_info.get('mail') or user_info.get('userPrincipalName')
        
        '''Parse the user_principal info'''
        # Step 1: Remove the #EXT# and everything after it
        if '#EXT#' in email:
            email = email.split('#EXT#')[0]
            
        # Step 2: Replace the first underscore with an at symbol
        email = email.replace('_', '@', 1)
        return {'email': email}
  
  
    def check_creds(self):
        if self.creds is None:
            return False
        if self.creds.access_token is None:
            return False
        if self.creds.expiry is None:
            return False
        if datetime.now() >= self.creds.expiry:
            return False
        return True      
    def refresh_or_reauthorize_credentials(self, manager_id, account):
        tok_man = TokenManager(account)
        creds_id = tok_man.get_id_by_account(manager_id)
        if creds_id: 
            if tok_man.is_expired(creds_id):
                print("Token is expired.")
                if self.creds.refresh_token:
                    try:
                        logging.debug(f"Attempting to refresh credentials with refresh token: {self.creds.refresh_token}")
                        self.oauth = OAuth2Session(self.creds.client_id, token={
                            'refresh_token': self.creds.refresh_token,
                            'token_type': 'Bearer',
                            'expires_in': -30  # Forces token refresh
                        })
                        token = self.oauth.refresh_token(
                            self.creds.token_uri,
                            refresh_token=self.creds.refresh_token,
                            client_id=self.creds.client_id,
                            client_secret=self.creds.client_secret
                        )
                        logging.debug("Refreshed credentials.")
                        self.save_credentials(token)
                        tok_man.update_tokens_in_db(
                            manager_id, account, token['access_token'],
                            token.get('refresh_token'),
                            (datetime.now() + timedelta(seconds=token.get('expires_in'))).isoformat() if token.get('expires_in') else None,
                            self.creds.token_uri
                        )
                    except Exception as e:
                        logging.error(f"Error refreshing credentials: {e}. Starting a new authorization flow.")
                        self.start_auth_flow()
            
                        token_data = self.oath.fetch_token(
                            self.creds.token_uri,
                            authorization_response=self.oauth.authorization_response,
                            client_secret=self.creds.client_secret,
                            code_verifier=self.code_verifier
                        )

                        # Save new credentials
                        self.save_credentials(token_data)

                        # Update tokens in the database
                        tok_man.update_tokens_in_db(
                            manager_id, account, token_data['access_token'], token_data.get('refresh_token'),
                            (datetime.now() + timedelta(seconds=token_data.get('expires_in'))).isoformat() if token_data.get('expires_in') else None,
                            self.creds.token_uri
                        )
                else:
                    logging.debug("Refresh token is not available. Starting a new authorization flow.")
                    self.start_auth_flow()
            
                    token_data = self.oath.fetch_token(
                        self.creds.token_uri,
                        authorization_response=self.oauth.authorization_response,
                        client_secret=self.creds.client_secret,
                        code_verifier=self.code_verifier
                    )

                    # Save new credentials
                    self.save_credentials(token_data)

                    # Update tokens in the database
                    tok_man.update_tokens_in_db(
                        manager_id, account, token_data['access_token'], token_data.get('refresh_token'),
                        (datetime.now() + timedelta(seconds=token_data.get('expires_in'))).isoformat() if token_data.get('expires_in') else None,
                        self.creds.token_uri
                    )
            else:
                logging.debug("Credentials are valid. No need to refresh or reauthorize.")
        else:
            logging.debug("Credentials object does not exist. Starting a new authorization flow.")
            self.start_auth_flow()
            
            token_data = self.oath.fetch_token(
                self.creds.token_uri,
                authorization_response=self.oauth.authorization_response,
                client_secret=self.creds.client_secret,
                code_verifier=self.code_verifier
            )

            # Save new credentials
            self.save_credentials(token_data)

            # Update tokens in the database
            tok_man.update_tokens_in_db(
                manager_id, account, token_data['access_token'], token_data.get('refresh_token'),
                (datetime.now() + timedelta(seconds=token_data.get('expires_in'))).isoformat() if token_data.get('expires_in') else None,
                self.creds.token_uri
            )

            
