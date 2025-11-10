'''

            Sentiment|      
---------------------------------------------------------------------------------------------------------











Items included:
Sentiment
Number of phishing images
number of name mismatches
number of organization mismatches

extracted threats
extracted promises
extracted link requests
extracted personal info requests

number suspicious links (that or extracted links with descriptions)

external vs internal


Following grammar errors lists:
        'Spelling Mistakes': [],
        'Punctuation Errors': [],
        'Capitalization Errors': [],
        'Subject-Verb Agreement Errors': [],
        'Tense Errors': [],
        'Run-On Sentences': [],
        'Fragmented Sentences': [],
        'Incorrect Pronoun Usage': [],
        'Awkward Phrasing': [],
        'Incorrect Prepositions': [],
        'Redundancy': [],
        'Improper Use of Articles': [],
        'Spacing Errors': [],
        'Incorrect Word Usage': []


Did AI write it

Clarity
        
Potentially attachment virus scanning












'''



PROBABILITY = {
        "sender_analysis": 0.25,
        "sentiment_grammar": 0.25,
        "Threat_PII_Benefit": 0.3,
        "Link_Images": 0.2
        }


THREAT_PII_BENEFIT_WEIGHTS = {
                            "Threat": 0.45,
                            "PII": 0.45,
                            "Benefit": 0.1
                            }

SENTIMENT_GRAMMAR_WEIGHTS = {
                            "Sentiment": 0.5,
                            "Grammar": 0.5
                            }

SENTIMENT_WEIGHT = {
                "Urgent_Threatening": 0.85,
                "Neutral/Benign": 0.02,
                "Suspicious/Scam": 0.75,
                }


SENDER_ANALYSIS_WEIGHTS = {
                        "External": 0,
                        "Mismatch":0,
                        "Fake_no_reply":0,
}

GRAMMAR_WEIGHTS = {
    
}


LINK_WEIGHTS = {
    
}

IMAGE_WEIGHTS = {
    
}

def calcualte_probability(data_object):
    pass