import json
import csv

# Open and read the JSON file
with open(r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\NERFiles\structured_threat_emails.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Prepare the CSV file
csv_file_path = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\NERFiles\structured_threat_emails.csv'

# Normalize newline characters and write to CSV
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    for entry in data:
        # Normalize the row_data by removing newline characters
        normalized_row_data = entry['row_data'].replace('\n', ' ')
        # Write the row data to CSV
        writer.writerow([normalized_row_data])
