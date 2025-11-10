import joblib
import PhishingDetection.src.analysis.email_class as classification
#from analysis.email_data import EmailData
from PhishingDetection.src.models.email import Email
import PhishingDetection.src.analysis.sender_analysis as s_analysis
import PhishingDetection.src.analysis.link_analysis as link_analysis
import PhishingDetection.src.analysis.grammarCheck as grammar
import re
import PhishingDetection.src.analysis.threat_Pii_promise as extract
import PhishingDetection.src.analysis.image_check as i_analysis


    
class Sentiment:
        def __init__(self, sentiment, confidence):
            self.sentiment = sentiment
            self.confidence = confidence
            
        @property
        def sentiment(self):
            return self._sentiment
        
        @sentiment.setter
        def sentiment(self, sentiment):
            self._sentiment = sentiment
            
            
        @property
        def confidence(self):
            return self._confidence
        
        
        @confidence.setter
        def confidence(self, confidence):
            self._confidence = confidence
            
            
            
            
class EmailData:
    def __init__(self):
        self.sentiment = None
        self.grammar_errors = {}
        self.suspicious_links = {}
        self.invalid_images = None
        self.virus_in_attachment = None
        self.urgency_score = None
        self.ai_probability = None
        self.email_segments = {}
        self.sender_name = None
        self.external = False
        self.sender_info= {}
        self.email = None
        self.threats_promise_pii = {}
        
    
    @property
    def grammar_errors(self):
        return self._grammar_errors
    
    @grammar_errors.setter
    def grammar_errors(self, g):
        self._grammar_errors = g
    
    @property
    def sentiment(self):
        return self._sentiment
    
    @sentiment.setter
    def sentiment(self, g):
        self._sentiment = g
    
    
    @property
    def threats_promise_pii(self):
        return self._threats_promise_pii
    
    @threats_promise_pii.setter
    def threats_promise_pii(self, value):
        self._threats_promise_pii = value
        
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        self._email = email
    
    @property
    def suspicious_links(self):
        return self._suspicious_links
    
    @suspicious_links.setter
    def suspicious_links(self, l):
        self._suspicious_links = l
        
    @property
    def email_segments(self):
        return self._email_segments
    
    @email_segments.setter
    def email_segments(self, s):
        self._email_segments = s
    @property
    def sender_name(self):
        return self._sender_name
    
    @sender_name.setter
    def sender_name(self, s):
        self._sender_name = s
    @property
    def external(self):
        return self._external
    
    @external.setter
    def external(self, e):
        self._external = e
        
    @property
    def sender_info(self):
        return self._sender_info
    
    @sender_info.setter
    def sender_info(self, d):
        self._sender_info = d

    
    @property
    def invalid_images(self):
        return self._invalid_images
    
    @invalid_images.setter
    def invalid_images(self, i):
        self._invalid_images = i
        
        
def process_sentiment(subject, body):
    print("check")
    sentiment_vectonzer_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\SentimentModel\vectorizer.pkl"
    sentiment__model_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\SentimentModel\sentiment_model.pkl"


    prepared_email = f"Subject: {subject}\n{body}"
    loaded_vectorizer = joblib.load(sentiment_vectonzer_path)
    loaded_model = joblib.load(sentiment__model_path)

    # Prepare the email for the model
    new_text_vec = loaded_vectorizer.transform([prepared_email])  # Note the list wrapping
    prediction = loaded_model.predict(new_text_vec)
    print(prediction)
    prediction_proba = loaded_model.predict_proba(new_text_vec)
    confidence = max(prediction_proba[0])
    return prediction, confidence
            




def classify_emails(email):
    '''
        This method is designed to use the email classification AI model to check the type
        of emails for the sender and recipient. 
        This will be used to determine if the emails are external or not
    '''
    label, no_reply = classification.classify(email)
    
    no_reply_map = {0.0: False, 1.0: True}
    no_reply_bool = no_reply_map.get(no_reply)
    
    return label, no_reply_bool





'''   
Steps in email checking
    1) check the sentiment of the email [COMPLETED]
    2) Email classification, is it external or a no_reply address [COMPLETED]
        [NOTE: do they claim to be from an organization but use a personal email address]
    3) Text segmentation 
        Signature:[COMPLETED]
            - Check the signature to extract organization from the sender [TRAIN a model]
            - Check the signature for identifiable information or social media [USE REGEX]
            - Check the name
        Body:
            - Check for an organization [COMPLETED]
            - Check for Threats, PII, or Promises [IN PROCESS]
            
        
    4) Process the sender information:
        - Take the signature info Org, Name, socials along witht he 
        body organization and the header email.
        Do the organizations in the body and signature match? Do the names in the signature and body match?
        Does the domain line up with someone from an organization? (CHECK REPLY TO Come back to if you have time)
    5) Classify the Threats, PII, Promises
    6) Check the grammar of the email
    7) Check Links, Logos, Attachments  
    
'''


#Check Images
def update_link_class(email, links_with_descriptions):
    for link, description in links_with_descriptions.items():
        link_obj = email.links.Link(link_address=link, description=description)
        email.links.add_link(link_obj)



def process_email(email):
    data_object = EmailData()
    s, c = (process_sentiment(email.subject, email.body))        #TODO DETERMINE CONFIDENCE LEVEL data_object.sentiment = process_sentiment(email.subject, email.body)  
    data_object.sentiment = Sentiment(s, c)
    print(f"Sentiment: {data_object.sentiment.sentiment}\nConfidence: {data_object.sentiment.confidence}")
    
    recipient_type,_ = classify_emails(email.recipient.email)       #TODO DETERMINE CONFIDENCE LEVEL
    print(f"Recipient Type: {recipient_type}")
    cleaned_r_email = re.sub(r'[<>]', '', email.recipient.email)
    sender_type,no_reply = classify_emails(cleaned_r_email)
    print(f"Sender type: {sender_type}")
    print(f"NO Reply: {no_reply}")
    if recipient_type != sender_type and recipient_type in ["Organizational", "School"]:
        data_object.external = True
        
    if sender_type in ["Organizational", "School"]:
        cleaned_email = re.sub(r'[<>]', '', email.sender.email)
        domain_pattern = r'@([^@]+)$'
        match = re.search(domain_pattern, cleaned_email)
        sender_domain = match.group(1)

            # Search for the email address in the sender header
        '''FUTURE DEVELOPMENT: ADD PROCESSING OF FIRST HALF OF EMAIL'''
            
        '''
                Sender Data includes:
                    (1) the domain
                    (2) If it is a no_reply address
                    (3) classification type
                    (4) Their name if found in the header
            
            '''
        data_object.sender_info = {"domain": sender_domain, 
                                    "no_reply": no_reply, 
                                    "classification": sender_type,
                                    "header_name": email.sender.name,
                                    "email": email.sender.email
                                    }
        print(f"Domain: {sender_domain}")
    else:
        data_object.sender_info = {"domain": None,
                                   "no_reply": no_reply, 
                                    "classification": sender_type,
                                    "header_name": email.sender.name,
                                    "email": email.sender.email
                                    }
                                   
            
        #print(f"No Reply: {no_reply}\nDomain Sender: {sender_domain}")
    # Search for the domain using the regular expression
    #print(f"External Status: {data_object.external}")
    
    body_text, signature_text = s_analysis.extract_body_and_signature(email.body)
    data_object.email_segments = {"body": body_text, "signature": signature_text}
    email_mismatch, sig_links,_ = s_analysis.determine_mismatch(data_object.sender_info, data_object.email_segments)
    print(email_mismatch)
    
    
    

    #Process Signature links
    
    #TODO: Check reply-to
    #TODO CHeck RE
    
    #Check Links    data_object.suspicious_links, link_descriptions = link_analysis.link_analysis(email, body_text)
    
    data_object.suspicious_links, link_list = link_analysis.link_analysis(email, body_text)
    print(data_object.suspicious_links)
    data_object.invalid_images = i_analysis.image_check(link_list)
     
   # update_link_class(email, link_descriptions) #perhaps save to databse?
    
    print(f"Suspicious Links: {data_object.suspicious_links}")
    
    #for every 4 sentences, run the check for threat, pii, and responses and develop a cohesive list
    results = extract.analyze_entities(body_text, chunk_size=4)
    print(f"Personal Information: {results['personal_info']}")
    print(f"Urgent or Threatening Language: {results['urgent_threatening']}")
    print(f"Requests to Follow a Link: {results['follow_link']}")
    print(f"Promises or Benefits: {results['promises_benefits']}")
    data_object.threats_promise_pii = results



    #Check Grammar
    data_object.grammar_errors = grammar.check(body_text)
    for category, issues in data_object.grammar_errors:
        print(f"{category}:")
        for issue in issues:
            print(f" - {issue['message']} (Context: {issue['context']})")
    
    
    print("MADE IT ALL THE WAY")
    return data_object
    




    





