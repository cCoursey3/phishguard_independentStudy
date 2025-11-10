import os
import requests
import re
from google.cloud import vision
import PhishingDetection.src.emails.email_parser as parser 




def is_logo(image_url):
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_url
    
    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    
    if logos:
        return True, logos[0].description
    return False, None


def extract(links):
        # Define the regex pattern
    pattern = re.compile(r'\[Image: (.*?)\]\[(.*?)\]')

    # Extract images
    images = []

    for link in links:
        matches = pattern.findall(link)
        for match in matches:
            description, url = match
            images.append({'description': description, 'link': url})
    return images

def search_image(image_url):
    search_api_url = image_url
    response = requests.post(search_api_url, json={'imageUrl': image_url})
    return response.json()

def image_check(links):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\phishingdetect-v12023-43b4984126cb.json"
    images = extract(links)
    count = 0
    for image_url in images:
        is_logo_image, logo_description = is_logo(image_url)
        if is_logo_image:
            print(f'Logo detected: {logo_description}')
            search_results = search_image(image_url)
            print(f'Search Results: {search_results}')
        else:
            print(f'No logo detected for image: {image_url}')
            count += 1