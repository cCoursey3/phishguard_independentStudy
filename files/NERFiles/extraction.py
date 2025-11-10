import json
from transformers import LongformerTokenizerFast
from datasets import Dataset, DatasetDict

# Load the JSON file with utf-8 encoding
input_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\datasets\ner_converted.json"
output_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\ner_processed.json"

with open(input_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize the tokenizer
tokenizer = LongformerTokenizerFast.from_pretrained('allenai/longformer-base-4096')

processed_data = []
whitespace_char = 'Ġ'

max_length = 2048  # Define a maximum length for the sequences
for entry in data:
    row_text = entry['row_text']    #retrieve the text  
    labels = entry['labels']    #retreive original labels
    
    '''Use this to track which word we are on using the original labels data'''
    word_idx = 0
    
    '''Use this to track which token we are on in tokenized data'''
    token_idx = 0
    
    
    tokenized_input = tokenizer(row_text, return_offsets_mapping=True, truncation=True, max_length=max_length)
    
    #print("Tokens:", tokenized_input.tokens())
   # print("Offset Mapping:", tokenized_input['offset_mapping'])
    
    new_labels = []
    tokens = tokenized_input.tokens()
    
    offsets = tokenized_input['offset_mapping']
    for o in offsets:
        start, end = o
        if (start == 0 and end == 0) or start == end:  # Special token (e.g., [CLS], [SEP])
            new_labels.append(0)
            token_idx += 1
        else:
            if tokens[token_idx].startswith(whitespace_char): #if there is a whitespace we are on another word                word_idx += 1
                current_label = labels[word_idx]
            else:
                current_label = labels[word_idx] # Get the label for the current word
            new_labels.append(current_label)
            token_idx += 1
    
            
    '''now we need to pad'''
    #first get the last index of the token
    if len(new_labels) < max_length:
        new_labels += [0] * (max_length - len(new_labels))
    new_labels = new_labels[:max_length]  # Ensure it's not longer than max_length
    
    
    processed_data.append({
        "row_text": row_text,
        "tokens": tokens,
        "labels": new_labels
    })

# Save the processed data to a new JSON file without utf-8 encoding
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(processed_data, file, indent=4, ensure_ascii=False)
