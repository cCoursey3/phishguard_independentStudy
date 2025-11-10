import json
import re

input_file = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\datasets\ner_chunked_reduced.json"
output_file = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\datasets\ner_coverted.json"

# Define labels
LABELS = {'O': 0, 'pii_request': 1, 'threat': 2, 'promise': 3}


def get_word_indices(text):
    """Get start and end indices of each word in the text."""
    words = text.split()
    word_indices = []
    start = 0
    for word in words:
        start = text.find(word, start)
        end = start + len(word) - 1
        word_indices.append((start, end))
        start += len(word)
    return word_indices

def label_text(text, annotations):
    """Label text based on annotations."""
    word_indices = get_word_indices(text)
    labels = [LABELS['O']] * len(word_indices)
    
    for annotation in annotations:
        label_type = annotation['label']
        start_offset = annotation['start']
        end_offset = annotation['end']
        
        for i, (start, end) in enumerate(word_indices):
            if start >= start_offset and end <= end_offset:
                labels[i] = LABELS[label_type]
    
    return labels

def process_json(data):
    """Process each JSON entry to label text and return processed entries."""
    processed_entries = []
    for entry in data:
        row_text = entry['sentence_text']
        annotations = entry['annotations']
        labels = label_text(row_text, annotations)
        processed_entries.append({'row_text': row_text, 'labels': labels})
    return processed_entries

def write_to_json(processed_entries, output_file):
    """Write processed entries to a new JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_entries, f, ensure_ascii=False, indent=4)


# Load JSON data
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Process JSON data
processed_entries = process_json(data)

# Write processed data to a new file
write_to_json(processed_entries, output_file)