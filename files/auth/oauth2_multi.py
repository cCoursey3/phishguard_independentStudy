import os
import json
import pickle
from selenium import webdriver
import chromedriver_autoinstaller
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from requests_oauthlib import OAuth2Session


# Scopes and Endpoints for each provider
OAUTH_PROVIDERS = {
    'gmail': {
        'scopes': ['https://www.googleapis.com/auth/gmail.readonly'],
        'client_secrets_file': r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\credentials.json',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth'
    },
    'aol': {
        'scopes': ['https://mail.aol.com/'],
        'client_secrets_file': r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\yahoo_credentials.json',
        'token_uri': 'https://api.login.aol.com/oauth2/get_token',
        'auth_uri': 'https://api.login.aol.com/oauth2/request_auth'
    },
    'outlook': {
        'scopes': ['https://outlook.office.com/Mail.Read'],
        'client_secrets_file': r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\outlook_credentials.json',
        'token_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'auth_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    },
    'yahoo': {
        'scopes': ['https://mail.yahoo.com/'],
        'client_secrets_file': r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\yahoo_credentials.json',
        'token_uri': 'https://api.login.yahoo.com/oauth2/get_token',
        'auth_uri': 'https://api.login.yahoo.com/oauth2/request_auth'
    }
}

def authenticate(service, email):
    """Authenticate the user with the given email service."""
    provider = OAUTH_PROVIDERS[service]
    creds = None
    token_path = f'token_{email}.pickle'

    # Load existing credentials if available
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_id, client_secret = load_client_secrets(provider['client_secrets_file'])
            oauth = OAuth2Session(client_id, redirect_uri='http://localhost', scope=provider['scopes'])
            authorization_url, state = oauth.authorization_url(provider['auth_uri'])

            # Start a browser session to handle the OAuth flow
            chromedriver_autoinstaller.install()  # Ensure ChromeDriver is installed
            options = webdriver.ChromeOptions()
            # options.add_argument("--headless")  # Remove headless mode
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1280,800")
            driver = webdriver.Chrome(options=options)

            driver.get(authorization_url)
            print("Please complete the authentication in the browser window that just opened.")
            while True:
                if driver.current_url.startswith('http://localhost'):
                    break
            response_url = driver.current_url
            driver.quit()

            oauth.fetch_token(provider['token_uri'], authorization_response=response_url, client_secret=client_secret)
            creds = oauth.token

        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def load_client_secrets(client_secrets_file):
    """Load client ID and client secret from a JSON file."""
    with open(client_secrets_file, 'r') as file:
        data = json.load(file)
    installed = data.get('installed') or data.get('web')  # Support both "installed" and "web" formats
    if installed:
        return installed['client_id'], installed['client_secret']
    else:
        raise KeyError('client_id and client_secret not found in the provided JSON file.')
