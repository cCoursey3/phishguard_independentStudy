from bs4 import BeautifulSoup
from bs4.element import NavigableString
import re
from email import policy
from email.parser import Parser
from quopri import decodestring

def translate_unicode_to_plaintext(text):
    """Translate quoted-printable and unicode sequences to plaintext"""
    try:
        text = decodestring(text).decode('utf-8')
    except Exception as e:
        print(f"Error decoding: {e}")
    return text


def preprocess_html(html_text):
    # Remove all \n characters and instances of =\n
    html_text = html_text.replace('=\n', '').replace('\n', '')
    return html_text


def count_nested_spans(element):
    """Count the number of nested <span> tags within an element"""
    span_count = 0
    for child in element.descendants:
        if child.name == 'span':
            span_count += 1
    return span_count

def get_text_with_spaces(element):
        text = element.get_text(separator=" ", strip=True)
        return re.sub(r'\s+', ' ', text)  # Normalize whitespace



def parse_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for br in soup.find_all("br"):
        br.replace_with(NavigableString("\n"))

    for tr in soup.find_all("tr"):
        tr.append(NavigableString("\n"))
        
    for a in soup.find_all("a"):
        if a.get('href'):
            span_count = count_nested_spans(a)
            if span_count > 2:  # Adjust the threshold for "deeply nested" as needed
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

def start_process(raw_email):
    msg = Parser(policy=policy.default).parsestr(raw_email)
    decoded_payload = translate_unicode_to_plaintext(msg.get_payload(decode=True).decode('utf-8'))
    preprocessed_payload = preprocess_html(decoded_payload)

    parsed_content = parse_html_content(preprocessed_payload)
    return parsed_content
def remove_headers(email_text):
    # Define patterns for headers typically found in forwarded or replied emails
    header_patterns = [
        r"^Sent from my .+$",  # Sent from my iPhone/Android, etc.
        r"^Begin forwarded message:$",
        r"^From: .+$",
        r"^Date: .+$",
        r"^To: .+$",
        r"^Subject: .+$"
    ]

    # Compile all patterns into a single regex
    headers_regex = re.compile("|".join(header_patterns), re.MULTILINE)

    # Remove all lines matching the patterns
    cleaned_email = headers_regex.sub("", email_text).strip()
    
    return cleaned_email
    
def main():
    input_path = r"C:\Users\Chloe\Desktop\Phishing\html_parsing\email24.txt"
    output_directory = r"C:\Users\Chloe\Desktop\Phishing\html_parsing"
    output_filename = f"email24_cleaned.txt"

    with open(input_path, 'r', encoding='utf-8') as f:
        raw_email = f.read()

    msg = Parser(policy=policy.default).parsestr(raw_email)
    decoded_payload = translate_unicode_to_plaintext(msg.get_payload(decode=True).decode('utf-8'))
    preprocessed_payload = preprocess_html(decoded_payload)

    parsed_content = parse_html_content(preprocessed_payload)
    parsed_content = remove_headers(parsed_content)

    output_path = f"{output_directory}/{output_filename}"
    with open(output_path, "w", encoding='utf-8') as output_file:
        output_file.write(parsed_content)

    print(f"Parsed content written to {output_path}")

if __name__ == "__main__":
    main()
