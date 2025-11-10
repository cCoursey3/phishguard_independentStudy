import requests
import re
from PhishingDetection.src.models.email import Email
from transformers import pipeline


model_name = "bert-base-uncased"  # Example model; choose one that fits your needs
nlp = pipeline("text-classification", model=model_name) #should actually be question answering?




def extract_links(email_body):
    # Regex pattern to find URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    links = re.findall(url_pattern, email_body)
    return links

def get_link_descriptions_huggingface(email_body, links):
    link_descriptions = {}
    for link in links:
        input_text = f"Email body: {email_body}\n\nLink: {link}\n\nPlease describe what this link is for."
        result = nlp(input_text)
        description = result[0]['label']  # Adjust based on actual model output
        link_descriptions[link] = description
    return link_descriptions


def update_link_class(email, links_with_descriptions):
    for link, description in links_with_descriptions.items():
        link_obj = email.links.Link(link_address=link, description=description)
        email.links.add_link(link_obj)


def download_openphish_feed():
    openphish_feed_url = 'https://openphish.com/feed.txt'
    response = requests.get(openphish_feed_url)
    phishing_urls = response.text.split('\n')
    return phishing_urls

def is_phishing_url(url, phishing_urls):
    return url in phishing_urls


def check_google_safe_browsing(url, api_key):
    safe_browsing_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    params = {
        "key": api_key
    }
    payload = {
        "client": {
            "clientId": "yourcompanyname",
            "clientVersion": "1.5.2"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }
    response = requests.post(safe_browsing_url, json=payload, params=params)
    result = response.json()
    matches = result.get('matches', [])
    return len(matches) > 0


def link_analysis(email, body=None):
    api_key = 'AIzaSyA8CchjpgLAOiXeRClrHm-F3nbVmBTwcCA'
    phishing_urls = download_openphish_feed()
    '''Ran into problems with longer text can come back to but done for now'''
    link_list = extract_links(body)
    #link_descriptions = get_link_descriptions_huggingface(body, extract_links(body))
    # Update Link class with descriptions
   #links_with_descriptions = update_link_class(email, link_descriptions)
    
    open_phish_count = 0
    google_safe_browsing_count = 0
    is_both = 0
    
    for link in email.links:
        is_phishing_OpenPhish = is_phishing_url(link, phishing_urls)
        is_phishing_Google = check_google_safe_browsing(link, api_key)
        if is_phishing_OpenPhish and is_phishing_Google:
            is_both += 1
        elif is_phishing_OpenPhish and not is_phishing_Google: 
            open_phish_count += 1
        elif is_phishing_Google and not is_phishing_OpenPhish:
            google_safe_browsing_count += 1
    
    phishing_counts = {
        "Both" : is_both,
        "OpenPhish_Only": open_phish_count,
        "Google_Browsing_Only": google_safe_browsing_count
    }
    
    
    
    #Look at links,
    #TODO: Later implementations may return the links, descriptions and their individual classification
    return phishing_counts, link_list        
            
            
            
            
            
            
'''
For later development
import schedule
import time

def job():
    update_openphish_feed()
    print("OpenPhish feed updated.")

# Schedule the job to run daily
schedule.every().day.at("00:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)'''