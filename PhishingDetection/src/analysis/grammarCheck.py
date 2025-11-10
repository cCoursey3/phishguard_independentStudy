import re
import requests
import json

LANGUAGE_TOOL_API_URL = "https://api.languagetool.org/v2/check"
API_KEY = "pit-XcuBaw2TyCDb"

def remove_links_and_images(text):
    # Remove all URLs
    text = re.sub(r'\[Link: .*?\]\[.*?\]', '', text)
    # Remove images
    text = re.sub(r'\[Image: .*?\]\[.*?\]', '', text)
    return text

def check_grammar(text):
    max_chunk_size = 2000  # Define a max chunk size, adjust based on API limits
    text = remove_links_and_images(text)  # Clean the text
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    issues = []
    for index, chunk in enumerate(chunks):
        payload = {
            'text': chunk,
            'language': 'en-US',
            'enabledOnly': False,
        }
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        print(f"Sending chunk {index+1}/{len(chunks)} to LanguageTool API")
        print(f"Payload: {json.dumps(payload)}")
        
        response = requests.post(LANGUAGE_TOOL_API_URL, data=payload, headers=headers)
        
        print(f"Response status code for chunk {index+1}: {response.status_code}")
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"Response JSON for chunk {index+1}: {response_json}")
                if 'matches' in response_json:
                    issues.extend(response_json['matches'])
                else:
                    print(f"No matches found in chunk {index+1}. Response: {response_json}")
            except ValueError as e:
                print(f"Error decoding JSON in chunk {index+1}: {e}")
        else:
            print(f"Error {response.status_code} in chunk {index+1}: {response.text}")
            # Handle error as needed, e.g., log or raise an exception
            
    return {'matches': issues}

def parse_issues(response):
    issues = []
    for match in response['matches']:
        issue = {
            'message': match['message'],
            'replacements': [repl['value'] for repl in match['replacements']],
            'offset': match['offset'],
            'length': match['length'],
            'context': match['context']['text'],
            'rule': match['rule']['issueType']
        }
        issues.append(issue)
    return issues

def categorize_issues(issues):
    categories = {
        'Spelling Mistakes': [],
        'Punctuation Errors': [],
        'Capitalization Errors': [],
        'Subject-Verb Agreement Errors': [],
        'Tense Errors': [],
        'Run-On Sentences': [],
        'Fragmented Sentences': [],
        'Incorrect Pronoun Usage': [],
        'Awkward Phrasing': [],
        'Incorrect Prepositions': [],
        'Redundancy': [],
        'Improper Use of Articles': [],
        'Spacing Errors': [],
        'Incorrect Word Usage': []
    }
    for issue in issues:
        if issue['rule'] == 'TYPOS':
            categories['Spelling Mistakes'].append(issue)
        elif issue['rule'] == 'PUNCTUATION':
            categories['Punctuation Errors'].append(issue)
        elif issue['rule'] == 'CAPITALIZATION':
            categories['Capitalization Errors'].append(issue)
        elif issue['rule'] == 'SUBJECT_VERB_AGREEMENT':
            categories['Subject-Verb Agreement Errors'].append(issue)
        elif issue['rule'] == 'TENSE':
            categories['Tense Errors'].append(issue)
        elif issue['rule'] == 'RUN_ON_SENTENCE':
            categories['Run-On Sentences'].append(issue)
        elif issue['rule'] == 'SENTENCE_FRAGMENT':
            categories['Fragmented Sentences'].append(issue)
        elif issue['rule'] == 'PRONOUN_USAGE':
            categories['Incorrect Pronoun Usage'].append(issue)
        elif issue['rule'] == 'AWKWARD_PHRASING':
            categories['Awkward Phrasing'].append(issue)
        elif issue['rule'] == 'PREPOSITIONS':
            categories['Incorrect Prepositions'].append(issue)
        elif issue['rule'] == 'REDUNDANCY':
            categories['Redundancy'].append(issue)
        elif issue['rule'] == 'ARTICLES':
            categories['Improper Use of Articles'].append(issue)
        elif issue['rule'] == 'SPACING':
            categories['Spacing Errors'].append(issue)
        elif issue['rule'] == 'WORD_USAGE':
            categories['Incorrect Word Usage'].append(issue)
    return categories

def check(email_text):
    response = check_grammar(email_text)
    issues = parse_issues(response)
    categorized_issues = categorize_issues(issues)
    return categorized_issues