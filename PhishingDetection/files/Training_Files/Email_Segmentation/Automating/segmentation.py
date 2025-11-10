import json
import re
import torch
from torch.utils.data import Dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import evaluate

# Load and Parse JSON Data
def load_data(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

# Preprocess Email Text
def preprocess_email(email):
    email = re.sub(r'<br\s*/?>', '\n', email)  # Use raw string literals
    email = re.sub(r'<[^>]+>', '', email)  # Use raw string literals
    return email

# Prepare Dataset
class EmailDataset(Dataset):
    def __init__(self, emails, labels):
        self.emails = emails
        self.labels = labels

    def __len__(self):
        return len(self.emails)

    def __getitem__(self, idx):
        email = self.emails[idx]
        label = self.labels[idx]
        inputs = tokenizer(email, return_tensors='pt', truncation=True, padding='max_length', max_length=512)
        inputs = {k: v.squeeze() for k, v in inputs.items()}
        return {**inputs, 'labels': torch.tensor(label)}

def prepare_dataset(data):
    emails = []
    labels = []
    for item in data:
        if 'text' in item:
            text = preprocess_email(item['text'])
            annotation = item.get('annotations', [])
            label = 1 if annotation else 0  # Assuming 1 indicates a signature, 0 otherwise
            emails.append(text)
            labels.append(label)
    return EmailDataset(emails, labels)

# Regex for Common Signature Patterns
def regex_signature_extraction(email):
    pattern = re.compile(r'(?i)(best regards|sincerely|thanks|regards|kind regards|yours truly|yours sincerely)[\s,]*\n(\s*\w+\s*\w*)\n?')
    match = pattern.search(email)
    if match:
        return match.group(0)
    return None

# Predict Signature Using the Fine-Tuned BERT Model
def bert_signature_extraction(email):
    tokens = tokenizer(email, return_tensors='pt', truncation=True, padding='max_length', max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    predictions = torch.argmax(outputs.logits, dim=-1)
    return predictions

# Main Function to Extract Signatures
def extract_segments(email):
    email = preprocess_email(email)
    tokens = tokenizer(email, return_tensors='pt', truncation=True, padding='max_length', max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    predictions = torch.argmax(outputs.logits, dim=-1).squeeze().tolist()
    
    body = []
    signature = []
    for token, prediction in zip(tokens['input_ids'][0], predictions):
        word = tokenizer.decode([token])
        if prediction == 0:
            body.append(word)
        else:
            signature.append(word)
    
    body_text = tokenizer.convert_tokens_to_string(body)
    signature_text = tokenizer.convert_tokens_to_string(signature)
    
    return body_text, signature_text

# Load Data
json_path = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\filtered_annotations.json"
data = load_data(json_path)

# Prepare the Dataset
dataset = prepare_dataset(data)

# Split dataset into training and evaluation sets
train_size = int(0.8 * len(dataset))
train_dataset, eval_dataset = torch.utils.data.random_split(dataset, [train_size, len(dataset) - train_size])

# Load Pre-trained BERT Model and Tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

# Define Evaluation Metrics
accuracy_metric = evaluate.load("accuracy")
precision_metric = evaluate.load("precision")
recall_metric = evaluate.load("recall")
f1_metric = evaluate.load("f1")

def compute_metrics(p):
    logits, labels = p
    predictions = torch.tensor(logits).argmax(dim=-1)
    labels = torch.tensor(labels)
    accuracy = accuracy_metric.compute(predictions=predictions, references=labels)
    precision = precision_metric.compute(predictions=predictions, references=labels, average='binary')
    recall = recall_metric.compute(predictions=predictions, references=labels, average='binary')
    f1 = f1_metric.compute(predictions=predictions, references=labels, average='binary')
    return {
        'accuracy': accuracy['accuracy'],
        'precision': precision['precision'],
        'recall': recall['recall'],
        'f1': f1['f1'],
    }

# Fine-Tune the BERT Model
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=10_000,
    save_total_limit=2,
    evaluation_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

# Example Email
email = """
Hi John,

Thank you for your email. I will get back to you soon.

Best regards,
Jane Doe
"""

# Extract and Print Signature
body_text, signature_text = extract_segments(email)
print(f"{body_text}\n {signature_text}")



model_save_path = './Segmentation/email_segmentation_model'
tokenizer_save_path = './Segmentation/email_segmentation_tokenizer'
model.save_pretrained(model_save_path)
tokenizer.save_pretrained(tokenizer_save_path)