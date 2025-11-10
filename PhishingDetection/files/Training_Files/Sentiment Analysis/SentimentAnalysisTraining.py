import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import stopwords
import re
import os

# Set the NLTK data path to the directory where stopwords are stored
nltk.data.path.append('C:\\Users\\Chloe\\nltk_data')

# Download stopwords
nltk.download('stopwords')

# Load CSV file
df = pd.read_csv(r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\Training Files\Sentiment Analysis\sentiment_classification.csv')

# Preview the data
print(df.head())

# Handle missing values in the text column
df['email_text'] = df['email_text'].fillna('')
# Ensure the email_text column is of string type
df['email_text'] = df['email_text'].astype(str)

# Handle missing values in the sentiment column by dropping them
df = df.dropna(subset=['sentiment'])

# Preprocess text data
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    # Remove URLs, mentions, and hashtags
    text = re.sub(r"http\S+|@\S+|#\S+", "", text)
    # Remove special characters, numbers, and punctuation
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    # Convert to lowercase
    text = text.lower()
    # Remove stopwords
    text = " ".join([word for word in text.split() if word not in stop_words])
    return text

df['email_text'] = df['email_text'].apply(preprocess_text)

# Encode labels
df['sentiment'] = df['sentiment'].map({'Suspicious/Scam': 1, 'Urgent/Threatening': 0, 'Neutral/Benign': 2})

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['email_text'], df['sentiment'], test_size=0.2, random_state=42)

# Vectorize text data
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train Logistic Regression model
model = LogisticRegression()
model.fit(X_train_vec, y_train)

# Predict on test set
y_pred = model.predict(X_test_vec)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print("Classification Report:")
print(report)

# Save the vectorizer and model (optional)
import joblib
joblib.dump(vectorizer, 'vectorizer.pkl')
joblib.dump(model, 'sentiment_model.pkl')


