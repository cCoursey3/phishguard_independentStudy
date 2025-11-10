import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import requests
from PhishingDetection.src.manager.tokenManager import TokenManager

logging.basicConfig(level=logging.DEBUG)

class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/gmail.readonly', 'openid']

    def __init__(self, credentials=None):
        """Initialize the Gmail API client."""
        self.service = None
        self.flow = None
        self.state = None
        self.credentials = credentials

        if credentials:
            print(f"Initial credentials: {credentials.to_json()}")
            if self.credentials and self.credentials.valid:
                self.service = build('gmail', 'v1', credentials=self.credentials)
                self.save_credentials()
            else:
                self.load_credentials()
        else:
            self.load_credentials()

    def get_authorization_url(self):
        self.flow = Flow.from_client_secrets_file(
            r'PhishingDetection/config/credentials.json',
            scopes=self.SCOPES,
            redirect_uri='http://localhost:8000/'
        )
        auth_url, state = self.flow.authorization_url(prompt='consent')
        self.state = state  # Save the state parameter
        logging.debug(f"Authorization URL: {auth_url}")
        return auth_url

    def fetch_token(self, authorization_response):
        self.flow.fetch_token(authorization_response=authorization_response)
        self.credentials = self.flow.credentials
        self.save_credentials()
        logging.debug("Fetched and saved credentials.")
        return self.credentials

    def load_credentials(self):
        """Load credentials from a file if available, or start a new authorization flow."""
        if os.path.exists(r'PhishingDetection/config/token.json'):
            try:
                with open(r'PhishingDetection/config/token.json', 'r') as token:
                    token_info = json.load(token)
                    self.credentials = Credentials.from_authorized_user_info(token_info, self.SCOPES)
                    logging.debug(f"Loaded credentials from file: {token_info}")
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Error reading token file: {e}. Starting a new authorization flow.")
                self.credentials = None

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    logging.debug(f"Attempting to refresh credentials with refresh token: {self.credentials.refresh_token}")
                    self.credentials.refresh(Request())
                    logging.debug("Refreshed credentials.")
                    self.save_credentials()
                except Exception as e:
                    logging.error(f"Error refreshing credentials: {e}. Starting a new authorization flow.")
                    self.start_auth_flow()
                    self.save_credentials()
            else:
                logging.debug("Credentials are invalid or do not exist. Starting a new authorization flow.")
                self.start_auth_flow()
                self.save_credentials()

        if self.credentials:
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logging.debug("Initialized Gmail API service.")
        else:
            logging.error("Failed to initialize Gmail API service due to missing credentials.")

    def save_credentials(self):
        """Save credentials to a file."""
        if self.credentials:
            credentials_data = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes,
                'expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            }
            with open(r'PhishingDetection/config/token.json', 'w') as token:
                json.dump(credentials_data, token)
            logging.debug(f"Saved credentials to file: {credentials_data}")

    def start_auth_flow(self):
        """Helper function to start the OAuth flow."""
        self.flow = Flow.from_client_secrets_file(
            r'PhishingDetection/config/credentials.json',
            scopes=self.SCOPES,
            redirect_uri='http://localhost:8000/'
        )
        return self.flow

    def list_messages(self, user_id='me', query='', max_results=None):
        """List all messages of the user's mailbox matching the query."""
        print(max_results)
        print(query)
        try:
            if max_results is not None:
                response = self.service.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()
            else:
                response = self.service.users().messages().list(userId=user_id, q=query).execute()
            
            messages = response.get('messages', [])
            return messages
        except Exception as e:
            logging.error(f"Error listing messages: {e}")
            raise
    
    def refresh_or_reauthorize_credentials(self, manager_id, account):
        tok_man = TokenManager()
        if self.credentials:
            if self.credentials.expired:
                print("Token is expired.")
                if self.credentials.refresh_token:
                    try:
                        logging.debug(f"Attempting to refresh credentials with refresh token: {self.credentials.refresh_token}")
                        self.credentials.refresh(Request())
                        logging.debug("Refreshed credentials.")
                        self.save_credentials()
                        # Update tokens in the database
                        tok_man.update_tokens_in_db(
                            manager_id, account, self.credentials.token,
                            self.credentials.refresh_token, self.credentials.expiry.isoformat() if self.credentials.expiry else None,
                            self.credentials.token_uri
                        )
                    except Exception as e:
                        logging.error(f"Error refreshing credentials: {e}. Starting a new authorization flow.")
                        self.start_auth_flow()
                        self.save_credentials()
                        # Update tokens in the database
                        tok_man.update_tokens_in_db(
                            manager_id, account, self.credentials.token,
                            self.credentials.refresh_token, self.credentials.expiry.isoformat() if self.credentials.expiry else None,
                            self.credentials.token_uri
                        )
                else:
                    logging.debug("Refresh token is not available. Starting a new authorization flow.")
                    self.start_auth_flow()
                    self.save_credentials()
                    # Update tokens in the database
                    tok_man.update_tokens_in_db(
                        manager_id, account, self.credentials.token, self.credentials.refresh_token,
                        self.credentials.expiry.isoformat() if self.credentials.expiry else None,
                        self.credentials.token_uri
                    )
            else:
                logging.debug("Credentials are valid. No need to refresh or reauthorize.")
        else:
            logging.debug("Credentials object does not exist. Starting a new authorization flow.")
            self.start_auth_flow()
            self.save_credentials()
            # Update tokens in the database
            tok_man.update_tokens_in_db(
                manager_id, account, self.credentials.token, self.credentials.refresh_token,
                self.credentials.expiry.isoformat() if self.credentials.expiry else None,
                self.credentials.token_uri
            )

    def get_tokens(self):
        """Get the access and refresh tokens."""
        tokens = {
            'access_token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token
        }
        return tokens['access_token'], tokens['refresh_token']
    
    def get_user_info(self):
            """Get user info using the stored credentials."""
            headers = {'Authorization': f'Bearer {self.credentials.token}'}
            response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
            user_info = response.json()
            logging.debug(f"User info retrieved: {user_info}")
            return user_info