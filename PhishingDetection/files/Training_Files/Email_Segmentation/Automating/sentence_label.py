import json
import re

# Load the JSON file with UTF-8 encoding
file_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\temp.json"
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Mapping for entity types
entity_map = {
    "intro": 0,
    "body": 1,
    "signature": 2
}

def check_and_label_words(data):
    labeled_data = []

    for idx, entry in enumerate(data):
        text = entry["sentence_text"]
        annotations = entry["annotations"]
        
        # Sort annotations by start offset to ensure correct order
        annotations = sorted(annotations, key=lambda x: x['start'])
        
        # Use regex to split the text into words and capture their start and end positions
        words = re.finditer(r'\b\w+\b', text)
        words = [(match.group(), match.start(), match.end()) for match in words]

        # Initialize the labels array with -1 (default value for no label)
        labels = [-1] * len(words)

        # Update labels based on annotations
        for annotation in annotations:
            entity = annotation["label"]
            start = annotation["start"]
            end = annotation["end"]
            label = entity_map[entity]
            
            # Find the word indices that match the start and end offsets
            for i, (word, word_start, word_end) in enumerate(words):
                if word_start >= start and word_end <= end:
                    labels[i] = label

        # Check if any word is not labeled
        unlabeled_words = [words[i][0] for i in range(len(words)) if labels[i] == -1]
        entry_id = entry.get('id', idx)  # Use the index as a fallback ID
        if unlabeled_words:
            print(f"Entry ID: {entry_id} has unlabeled words: {unlabeled_words}")
        else:
            labeled_data.append({
                "id": entry_id,
                "text": text,
                "labels": labels
            })

    return labeled_data

# Label the words in the data
labeled_data = check_and_label_words(data)

# Save the labeled data to a new JSON file if all words are labeled
if labeled_data:
    output_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\temp_converted.json"
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(labeled_data, outfile, indent=4, ensure_ascii=False)
