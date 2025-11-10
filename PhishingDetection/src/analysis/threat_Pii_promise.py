
import re
import openai

# Define your API key
api_key = 'sk-proj-CYxsjJnomagROZVfudA4T3BlbkFJI5KcrhbokOiU3pIFBLXx'

# Initialize the OpenAI client
openai.api_key = api_key

def extract_entities(prompt, email_text):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"{prompt}\n\nEmail:\n{email_text}",
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

def analyze_entities(text, chunk_size=3):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = [' '.join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]
    
    results = {
        'personal_info': [],
        'urgent_threatening': [],
        'follow_link': [],
        'promises_benefits': []
    }

    prompts = {
        "personal_info": "Extract all instances of personal information, including full names, phone numbers, email addresses, banking information, physical addresses, debt amounts, and any other requests for personal information.",
        "urgent_threatening": "Extract all instances of urgent or threatening language, including indications of account expiration, threats, and any language suggesting immediate action is required.",
        "follow_link": "Extract all instances where the email requests the recipient to follow a link.",
        "promises_benefits": "Extract all instances where the email promises benefits or rewards to the user, including promotional offers, financial gains, or other incentives."
    }

    for chunk in chunks:
        results['personal_info'].append(extract_entities(prompts["personal_info"], chunk))
        results['urgent_threatening'].append(extract_entities(prompts["urgent_threatening"], chunk))
        results['follow_link'].append(extract_entities(prompts["follow_link"], chunk))
        results['promises_benefits'].append(extract_entities(prompts["promises_benefits"], chunk))

    return results




'''# Extract entities
personal_info = extract_entities(prompts["personal_info"], email_text)
urgent_threatening = extract_entities(prompts["urgent_threatening"], email_text)
follow_link = extract_entities(prompts["follow_link"], email_text)
promises_benefits = extract_entities(prompts["promises_benefits"], email_text)

# Print extracted entities
print("Personal Information:", personal_info)
print("Urgent or Threatening Language:", urgent_threatening)
print("Requests to Follow a Link:", follow_link)
print("Promises or Benefits:", promises_benefits)
'''