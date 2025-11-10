class EmailData:
    def __init__(self):
        self.sentiment = None
        self.sender_email_class = None
        self.recipient_email_class = None
        self.grammar_errors = None
        self.suspicious_links = None
        self.invalid_images = None
        self.virus_in_attachment = None
        self.urgency_score = None
        self.ai_probability = None
        self.email_segments = {}
    
    @property
    def sentiment(self):
        return self._sentiment
    
    @sentiment.setter
    def sentiment(self, s):
        self._sentiment = s
        
    @property
    def email_segments(self):
        return self._email_segments
    
    @email_segments.setter
    def email_segments(self, s):
        self._email_segments = s
    
    