import re
import PhishingDetection.files.Training_Files.Email_Segmentation.segmentation_training as seg_train
import PhishingDetection.files.Training_Files.Signature_Analysis.sig_training as sig
from fuzzywuzzy import fuzz
class SenderInfo:
    def __init__(self, sender_info):
        self.domain = None
        self.no_reply = False
        self.classification = None
        self.header_name = None
        self.header_email = None
        self.body_name = None
        self.body_organization = None
        self.sig_name = None
        self.sig_organization = None

        self.extract_sender_info(sender_info)
    
    def extract_sender_info(self, sender_info):
        self.domain = sender_info.get("domain")
        self.no_reply = sender_info.get("no_reply", False)
        self.classification = sender_info.get("classification")
        self.header_name = sender_info.get("header_name")
        self.header_email = sender_info.get("email")

        # Validate and handle missing fields if necessary
        if self.domain is None:
            print("Domain is from a personal account")
        if self.classification is None:
            print("Warning: 'classification' key is missing in sender_info")
        if self.header_name is None:
            print("Warning: 'header_name' key is missing in sender_info")
        if self.header_email is None:
            print("Warning: 'email' key is missing in sender_info")


    @property
    def body_name(self):
        return self._body_name
    @body_name.setter
    def body_name(self, n):
        self._body_name = n
        
    @property
    def body_organization(self):
        return self._body_organization

    @body_organization.setter
    def body_organization(self, o):
        self._body_organization = o
    
    @property
    def sig_name(self):
        return self._sig_name
    
    @sig_name.setter
    def sig_name(self, n):
        self._sig_name = n
        
    @property
    def sig_organization(self):
        return self._sig_organization

    @sig_organization.setter
    def sig_organization(self, o):
        self._sig_organization = o
        
    @property
    def domain(self):
        return self._domain
    
    @domain.setter
    def domain(self, d):
        self._domain = d
        
    @property
    def no_reply(self):
        return self._no_reply
    
    @no_reply.setter
    def no_reply(self, n):
        self._no_reply = n
        
    @property
    def classification(self):
        return self._classification
    
    @classification.setter
    def classification(self, c):
        self._classification = c
        
    @property
    def header_name(self):
        return self._header_name
    
    @header_name.setter
    def header_name(self, n):
        self._header_name = n
        
    @property
    def header_email(self):
        return self._header_email
    
    @header_email.setter
    def header_email(self, e):
        self._header_email = e
        




def clean_signature(text):
    links = re.findall(r'\[Link: .*?\]\[.*?\]', text)
    images = re.findall(r'\[Image: .*?\]\[.*?\]', text)
    
    # Remove links and images
    text = re.sub(r'\[Link: .*?\]\[.*?\]', '', text)
    text = re.sub(r'\[Image: .*?\]\[.*?\]', '', text)
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    print(text)
    return text, links, images

def process_signature(text):
    '''Add code that if both overlap, confidence level increases'''
   # ner_entities = sig.extract_entities(text)
   # print(ner_entities)
   
   ##GET RID OF LINKS AND STUFF
    cleaned_text,links,images = clean_signature(text)
    #links and images to be later looked at
    if cleaned_text is None:
        return None, None, links, images
    print(f"Cleaned Signature: {cleaned_text}")
    
    
    organization, person = sig.extract_contextual_info(cleaned_text)
    
    #if organization is not "none": update the email to be of organization type Feed
    #back into AI
        
    
    
    print(f"Extracted organization: {organization}\nExtracted Person: {person}")
    return organization, person, links, images




def preprocess_email(email):
    email = re.sub(r'<br\s*/?>', '\n', email)  # Convert <br> to newline
    email = re.sub(r'<[^>]+>', '', email)  # Remove HTML tags
    email = re.sub(r'\r\n', '\n', email)  # Normalize line breaks
    return email.strip()


def clean_body(text):
    text = re.sub(r'\[Link: .*?\]\[.*?\]', '', text)
    # Remove images
    text = re.sub(r'\[Image: .*?\]\[.*?\]', '', text)
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\n', '', text)
    return text
    
    
def process_body(text):
    # Join the list of text segments into a single string
    text = clean_body(text)
    
    
    Name = None
    if isinstance(text, list):
        text = ' '.join(text)
    # First extract "I am"
    sender_name = seg_train.extract_sender_name(text)  # Extract the sender name
    print(sender_name)
    # If None then pass, else store
    if sender_name is None:
        Name = "No name in body"
    else:
        Name = sender_name
    
    ner_entities = sig.extract_entities(text)
    ner_orgs = [ent[0] for ent in ner_entities if ent[1] == 'ORG']
    
    return Name, ner_orgs





def extract_body_and_signature(email):
    # Preprocess email text
    email = preprocess_email(email)
    
    # Common sign-off phrases
    sign_off_phrases = [
        "best regards",
        "regards",
        "sincerely",
        "thanks",
        "thank you",
        "cheers",
        "kind regards",
        "yours truly",
        "yours sincerely",
        "warm regards",
        "best wishes",
        "respectfully"
    ]

    # Additional patterns to identify signature blocks
    signature_patterns = [
        r'\b(?:copyright|phone|email|fax|address|website|www|all rights reserved|confidentiality notice)\b',
        r'\b(?:team|department|group|office|management)\b',
        r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'  # Phone numbers
    ]
    
    # Regex pattern to match sign-off phrases and other signature patterns
    sign_off_pattern = re.compile(
        r'(?:' + '|'.join([re.escape(phrase) for phrase in sign_off_phrases]) + r')\W*$|' + '|'.join(signature_patterns), 
        re.IGNORECASE | re.MULTILINE
    )

    # Split email into lines
    lines = email.split('\n')

    # Reverse iterate through lines to find the signature starting point
    signature_start = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if sign_off_pattern.search(lines[i]):
            signature_start = i
            break
        # Check for empty lines or lines with just spaces (indicative of separation)
        if lines[i].strip() == '':
            signature_start = i

    # If no sign-off phrase was found, attempt to identify signature based on spacing
    if signature_start == len(lines):
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == '' and i < len(lines) - 2 and lines[i + 1].strip() != '':
                signature_start = i + 1
                break

    # Extract body and signature
    body = '\n'.join(lines[:signature_start]).strip()
    signature = '\n'.join(lines[signature_start:]).strip()

    return body, signature


def standardize_organization_name(org_name):
    if isinstance(org_name, list):
        org_name = ' '.join(org_name)
    org_name = org_name.lower()
    #TODO: create more robust regex
    org_name = re.sub(r'\b(?:inc|llc|ltd|plc|corp|corporation|company|co|copyright|management team|customer service|customer service team|management|team)\b', '', org_name)
    org_name = re.sub(r'[^a-z0-9\s]', '', org_name)
    return org_name.strip()

def check_fuzzy_match(org1, org2, threshold=80):
    return fuzz.ratio(org1, org2) >= threshold

    
def determine_mismatch(sender_array, segments):
    sender_info = SenderInfo(sender_array)
    sender_info.sig_organization, sender_info.sig_name, links, images = process_signature(segments["signature"])
    
    sender_info.body_name, sender_info.body_organization = process_body(segments["body"])
    
    mismatch_counts = {
        "name": 0,
        "organization": 0
    }
    
    name_checks = {
        "header_body": (sender_info.header_name, sender_info.body_name),
        "header_sig": (sender_info.header_name, sender_info.sig_name),
        "body_sig": (sender_info.body_name, sender_info.sig_name)
    }
    
    print(sender_info.header_name)
    
    for check, (first, second) in name_checks.items():
        if first and second and first != second:
            if (first is not None and first != "No name in body") and (second is not None and second != "No name in body"):
                print(f"Mismatch in {check}: '{first}' vs '{second}'")
                mismatch_counts["name"] += 1
    
    organization_checks = {
        "body_sig": (sender_info.body_organization, sender_info.sig_organization)
    }
    
    for check, (first, second) in organization_checks.items():
        if first and second:
            first_std = standardize_organization_name(first)
            second_std = standardize_organization_name(second)
            print(f"Comparing organizations: '{first_std}' vs '{second_std}'")
            if not check_fuzzy_match(first_std, second_std):
                if first_std != "none" and second_std!="none":
                    if first_std.lower() not in second_std.lower() and second_std.lower() not in first_std.lower:
                        print(f"Mismatch found: '{first_std}' vs '{second_std}'")
                        mismatch_counts["organization"] += 1

    return mismatch_counts, links, images
    
    '''
        Check the email
        1) IS the person's email some variation of the organization
        2) Is the claimed email one of the known spoofed organizations, yes, check json
        3) is it a gov?
    '''
    
    
    