from PhishingDetection.src.models.email import Email
from email import policy
from email.parser import Parser
from quopri import decodestring
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import base64
import email
import mysql.connector
import re
import requests
from google.cloud import vision
from google.oauth2 import service_account

def preprocess_html(html_text):
    html_text = html_text.replace('=\n', '').replace('\n', '')
    return html_text

def count_nested_spans(element):
    span_count = 0
    for child in element.descendants:
        if child.name == 'span':
            span_count += 1
    return span_count

def get_text_with_spaces(element):
    text = element.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', text)

def parse_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for br in soup.find_all("br"):
        br.replace_with(NavigableString("\n"))

    for tr in soup.find_all("tr"):
        tr.append(NavigableString("\n"))
        
    for a in soup.find_all("a"):
        if a.get('href'):
            span_count = count_nested_spans(a)
            if span_count > 2:
                link_str = f"[Link][{a['href']}]"
            else:
                link_text = get_text_with_spaces(a)
                link_str = f"[Link: {link_text}][{a['href']}]"
            a.append(NavigableString("\n" + link_str + "\n"))
    for img in soup.find_all("img"):
        img_alt = img.get('alt', 'Image')
        src = img.get('src', '')
        img_str = f"[Image: {img_alt}][{src}]" if src else "[Image: Empty Link]"
        img.append(NavigableString(img_str + "\n"))

    for button in soup.find_all("button"):
        button_text = get_text_with_spaces(button)
        href = button.get('href', '')
        button_str = f"[Button: {button_text}][{href}]" if href else f"[Button][{href}]"
        button.append(NavigableString(button_str + "\n"))

    return soup.get_text()

def translate_unicode_to_plaintext(text):
    encodings = ['utf-8', 'iso-8859-1', 'latin-1']
    for encoding in encodings:
        try:
            text = decodestring(text).decode(encoding)
            return text
        except Exception as e:
            continue
    print(f"Error decoding: {e}")
    raise UnicodeDecodeError("All decoding attempts failed")

def start_process(raw_email):
    msg = Parser(policy=policy.default).parsestr(raw_email)
    decoded_payload = translate_unicode_to_plaintext(msg.get_payload(decode=True))
    preprocessed_payload = preprocess_html(decoded_payload)
    parsed_content = parse_html_content(preprocessed_payload)
    return parsed_content

class Email_Reader():
    def __init__(self, service, message_id):
        self.service = service.service 
        self.message_id = message_id

    def parse_header(self):        
        message = self.service.users().messages().get(userId='me', id=self.message_id, format='metadata', metadataHeaders=['From', 'To', 'Subject']).execute()
        
        headers = message['payload']['headers']
        sender = None
        subject = None
        recipient = None
        for header in headers:
            if header['name'] == 'From':
                sender_info = header['value']
                sender_name, sender_email = self.parse_email(sender_info)
                sender = Email.Sender(sender_name, sender_email)
            if header['name'] == 'Subject':
                subject = f"Subject: {header['value']}"
            if header['name'] == 'To':
                recipient_info = header['value']
                recipient_name, recipient_email = self.parse_email(recipient_info)
                recipient = Email.Recipient(recipient_name, recipient_email)
        return [str(sender), subject, str(recipient)]
    
    def parse_email(self, email_info):
        match = re.match(r'(.*) <(.*)>', email_info)
        if match:
            name = match.group(1).replace('"', '').strip()
            email = match.group(2).replace('"', '').strip()
            return name, email
        return "", email_info

    def decode_payload(self, payload):
        encodings = ['utf-8', 'iso-8859-1', 'latin-1']
        for encoding in encodings:
            try:
                return payload.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("All decoding attempts failed")

    def parse_message(self, mime_msg):
        email_parts = {
            'text': None,
            'html': None
        }
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        email_parts['text'] = self.decode_payload(part.get_payload(decode=True))
                    except UnicodeDecodeError as e:
                        print(f"Failed to decode text part: {e}")
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        email_parts['html'] = self.decode_payload(part.get_payload(decode=True))
                    except UnicodeDecodeError as e:
                        print(f"Failed to decode HTML part: {e}")
        else:
            content_type = mime_msg.get_content_type()
            if content_type == "text/plain":
                try:
                    email_parts['text'] = self.decode_payload(mime_msg.get_payload(decode=True))
                except UnicodeDecodeError as e:
                    print(f"Failed to decode text part: {e}")
            elif content_type == "text/html":
                try:
                    email_parts['html'] = self.decode_payload(mime_msg.get_payload(decode=True))
                except UnicodeDecodeError as e:
                    print(f"Failed to decode HTML part: {e}")
        
        return email_parts

  
    def parse_body(self):
        message = self.service.users().messages().get(userId='me', id=self.message_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)
        email_parts = self.parse_message(mime_msg)
        if email_parts['html']:
            parsed = start_process(email_parts['html'])
            return remove_headers(parsed)
        else:
            return email_parts['text']
    

def remove_headers(email_text):
    header_patterns = [
        r"^Sent from my .+$",
        r"^Begin forwarded message:$",
        r"^From: .+$",
        r"^Date: .+$",
        r"^To: .+$",
        r"^Subject: .+$"
    ]

    headers_regex = re.compile("|".join(header_patterns), re.MULTILINE)
    cleaned_email = headers_regex.sub("", email_text).strip()
    
    return cleaned_email

