'''



# Function to test the model on a sample input
def test_model(input_text):
    # Tokenize the input
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get the predicted labels
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)
    
    # Convert predicted label IDs to actual labels
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    labels = predictions[0].tolist()
    
    # Print the tokens with their predicted labels
    label_map = {0: "O", 1: "pii_request", 2: "promise"}  # Update this mapping as per your labels
    labeled_tokens = [(token, label_map.get(label, "O")) for token, label in zip(tokens, labels)]
    
    for token, label in labeled_tokens:
        print(f"{token}: {label}")

# Example input text
input_text = "My name is Miss. Mariam Abdullah, from Sierra Leone, I am 19years old girl, my father was director of finance gold and diamond company in my country Sierra Leone, my parents have an auto accident of which my mother died instantly, before the death of my father in one of private hospital in our country Sierra Leone, my father called me secretly and told me that he deposited $9.000,000,00 million dollars into fixed deposit account with gold to the bank in Cote d'Ivoire, and he used my name as next of kin, I contacting you to help me to transfer the money into your account for my investment in your country where I will be saved, sincerely I have been facing a difficulties life since the death of my parents, my uncles plan to take away this money from me they have tried to kill me, I need to leave this place before my uncles killed me, be assured if you help me to transfer this money into your account, I will offer you 20% from the money as compensation, I am waiting to hear from you for more information."

# Test the model with the sample input
test_model(input_text)
'''

import json
import torch
from transformers import LongformerTokenizerFast, AutoModelForTokenClassification

# Paths to the saved model and tokenizer
model_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_Model"
tokenizer_path = r"allenai/longformer-base-4096"


# Load the trained model and tokenizer
tokenizer = LongformerTokenizerFast.from_pretrained(tokenizer_path, add_prefix_space=True)
model = AutoModelForTokenClassification.from_pretrained(model_path)

def test_tokenization(input_text):
    # Tokenize the input
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    print("Tokens:", tokens)

# Example input text
input_text = "Subject: Urgent: Verify Your Social Security Number Dear Director Hughes, We need to verify your Social Security Number to maintain your account's integrity. Please click the link below and enter your SSN to continue using our services without interruption. Link Thank you for your cooperation. Best regards, DOJ Verification Team."

# Test tokenization
test_tokenization(input_text)
