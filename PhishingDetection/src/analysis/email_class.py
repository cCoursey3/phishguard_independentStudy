import re
import joblib
import torch
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the models
email_type_model_path = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\ClassificationModel\email_type_model.pkl'
noreply_model_path = r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\ClassificationModel\noreply_model.pkl'

email_type_model = joblib.load(email_type_model_path)
noreply_model = joblib.load(noreply_model_path)


# Function to predict email type
def predict_email_type(email_text):
    return email_type_model.predict([email_text])[0]

# Function to predict no-reply
def predict_no_reply(email_text):
    return noreply_model.predict([email_text])[0]

def classify(email):
    email_type_prediction = predict_email_type(email)
    no_reply_prediction = predict_no_reply(email)
    
    return email_type_prediction, no_reply_prediction


