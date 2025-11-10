import json
import requests
import urllib.parse
import os
from requests_oauthlib import OAuth2Session
from PhishingDetection.src.emails.credentials import Credentials
from datetime import datetime, timedelta
from PhishingDetection.src.manager.tokenManager import TokenManager
import logging

class YahooService:
    def __init__(self, service_name, credentials=None):
        self.oauth = None
        self.state = None
        self.service = None

        if credentials is not None:
            self.creds = credentials
        elif service_name == "Yahoo":
            self.token_file = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\yahoo_token.json'
            self.creds = Credentials(service="Yahoo")
        else:
            self.token_file = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\aol_token.json'
            self.creds = Credentials(service="AOL")

        self.initialize_session()

    def initialize_session(self):
        token = self.load_token()

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

    def get_authorization_url(self):
        auth_url, state = self.oauth.authorization_url(
            self.creds.authorization_base_url,
            prompt='consent'  # Force consent
        )
        self.state = state
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
        }
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()  # Raise an error for bad responses
        token_data = response.json()
        self.save_credentials(token_data)
        return token_data

    def save_credentials(self, token_data):
        with open(self.token_file, 'w') as file:
            json.dump(token_data, file)

    def build_service(self, token):
       self.service = OAuth2Session(
        self.creds.client_id,
        token=token,
        redirect_uri=self.creds.redirect_uri,
        scope=self.creds.scope
    )

    def get_tokens(self):
        return self.oauth.token['access_token'], self.oauth.token['refresh_token']

    def start_auth_flow(self):
        authorization_url, state = self.get_authorization_url()
        return authorization_url, state

    def list_messages(self):
        headers = {'Authorization': f'Bearer {self.oauth.token["access_token"]}'}
        response = self.oauth.get('https://api.mail.yahoo.com/ws/v3/mailboxes/@.id/messages', headers=headers)
        response.raise_for_status()
        return response.json()

    def get_message(self, message_id):
        headers = {'Authorization': f'Bearer {self.oauth.token["access_token"]}'}
        response = self.oauth.get(f'https://api.mail.yahoo.com/ws/v3/mailboxes/@.id/messages/{message_id}', headers=headers)
        response.raise_for_status()
        return response.json()

    def revoke_token(self, token):
        revoke_url = 'https://api.login.yahoo.com/oauth2/revoke'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {token}'
        }
        data = {
            'token': token,
            'token_type_hint': 'access_token',
            'client_id': self.creds.client_id,
            'client_secret': self.creds.client_secret
        }
        response = requests.post(revoke_url, headers=headers, data=data)
        response.raise_for_status()
        return response.status_code == 200

    def load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as token_file:
                return json.load(token_file)
        return None


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

            



    def get_user_info(self):
        """Get user info using the stored credentials."""
        headers = {'Authorization': f'Bearer {self.creds.access_token}'}
        response = self.oauth.get('https://api.login.yahoo.com/openid/v1/userinfo', headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        user_info = response.json()
        email = user_info.get('email')
        return {'email': email}
