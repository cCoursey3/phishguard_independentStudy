import json
import os

# Define the path to the JSON file
json_path = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\datasets\ner_chunked_reduced.json'

# Define the directory where the text files will be saved
output_dir = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\datasets\output'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read the JSON file
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract the sentence_text and save each to a separate text file
for i, item in enumerate(data):
    sentence_text = item.get('sentence_text', '')
    file_name = f'sentence_text_{i+1}.txt'
    file_path = os.path.join(output_dir, file_name)
    
    with open(file_path, 'w', encoding='utf-8') as text_file:
        text_file.write(sentence_text)

print("Sentence texts have been extracted and saved to text files.")

