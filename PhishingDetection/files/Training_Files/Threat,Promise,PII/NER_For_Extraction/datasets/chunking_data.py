import json
import re
from typing import List, Dict

# Define the paths
input_file_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\datasets\ner.json"
output_file_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training_Files\Threat,Promise,PII\NER_For_Extraction\datasets\ner_chunked.json"

# Function to split text into sentences
def split_into_sentences(text: str) -> List[str]:
    sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
    sentences = sentence_endings.split(text)
    return sentences

# Process annotations within the chunks
def process_annotations(chunk_text: str, chunk_start_idx: int, annotations: List[Dict]) -> List[Dict]:
    chunk_annotations = []
    for annotation in annotations:
        label = annotation["label"]
        start_offset = annotation["start_offset"]
        end_offset = annotation["end_offset"]
        
        if chunk_start_idx <= start_offset < chunk_start_idx + len(chunk_text):
            annotation_start = max(0, start_offset - chunk_start_idx)
            if start_offset <= end_offset < chunk_start_idx + len(chunk_text):
                annotation_end = end_offset - chunk_start_idx
                chunk_annotations.append({
                    "label": label,
                    "text": annotation["text"],
                    "start_offset": annotation_start,
                    "end_offset": annotation_end
                })
            else:
                annotation_end = len(chunk_text) - 1
                chunk_annotations.append({
                    "label": label,
                    "text": annotation["text"][:annotation_end],
                    "start_offset": annotation_start,
                    "end_offset": annotation_end
                })
    return chunk_annotations

# Chunk the emails and process annotations
def chunk_emails(data: List[Dict], limit: int = None) -> List[Dict]:
    chunked_data = []
    for i, entry in enumerate(data[:limit]):
        email_id = f"email{i + 1}"
        email_text = entry["row_data"]
        annotations = entry["annotations"]
        
        sentences = split_into_sentences(email_text)
        chunk_start_idx = 0

        for j in range(0, len(sentences), 3):
            chunk_sentences = sentences[j:j + 3]
            chunk_text = " ".join(chunk_sentences)
            chunk_end_idx = chunk_start_idx + len(chunk_text)
            
            chunk_annotations = process_annotations(chunk_text, chunk_start_idx, annotations)
            
            chunked_data.append({
                "id": email_id,
                "external_id": f"{email_id}.sentence_{j+1}-{j+len(chunk_sentences)}",
                "sentence_text": chunk_text,
                "annotations": chunk_annotations,
                "chunk_start_idx": chunk_start_idx,
                "chunk_end_idx": chunk_end_idx
            })
            
            chunk_start_idx = chunk_end_idx + 1  # Adjust for next chunk

    return chunked_data

# Load the data
with open(input_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Process the first entry for testing
chunked_data = chunk_emails(data)

# Save the chunked data to a new file
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(chunked_data, f, indent=4)

print(f"Processed data saved to {output_file_path}")
