import datetime


class Query():
    def __init__(self, account, service):
        self.text = None
        self.account= account
        self.service = service
        self.message_ids = []
        print("this is where the problem probably is")
        
    def get_today_query(self):
        today = datetime.date.today().strftime('%Y/%m/%d')
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y/%m/%d')
        self.query = f'after:{today} before:{tomorrow}'
        return self.query
    
    def list_message_ids(self, query):
        response = self.service.list_messages(query=query)
        if isinstance(response, list):
            self.message_ids = [message['id'] for message in response]
            return self.message_ids
        return []

    def get_yesterday_query(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_start = yesterday.strftime('%Y/%m/%d')
        today_start = today.strftime('%Y/%m/%d')
        self.query = f'after:{yesterday_start} before:{today_start}'
        return self.query

    
    def get_X_email_query(self, value):
        text = f'Past {value} emails'
        print(text)
        return text
    
    def get_past_X_emails(self, value):
        try:
            max_results = int(value)  # Ensure the input is an integer
        
            response = self.service.list_messages(max_results=max_results)
            if isinstance(response, list):
                # Handle the case where the response is a list of messages
                self.message_ids = [message['id'] for message in response]
            elif 'messages' in response:
                # Handle the case where the response contains a 'messages' key
                self.message_ids = [message['id'] for message in response['messages']]
            else:
                print("Unexpected response structure")
                self.message_ids = []

            print(f"Extracted Message IDs: {self.message_ids}")  # Debugging: Print the extracted message IDs
            return self.message_ids
        except ValueError:
            print("Invalid input for number of emails")
            return []
            
    def get_past_X_day_query(self, value):
        try:
            days = int(days)  # Ensure the input is an integer
        except ValueError:
            print("Invalid input for days")
        today = datetime.date.today()
        days_ago = today - datetime.timedelta(days = value)
        day_start = days_ago.strftime('%Y/%m/%d')
        today_end = today.strftime('%Y/%m/%d')
        self.query = f'after:{day_start} before:{today_end}'
        return self.query
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value
        
    @property
    def message_ids(self):
        return self._message_ids
    
    @message_ids.setter
    def message_ids(self, value):
        self._message_ids = value

    def __str__(self):
        return f"{self.text} with ids {self.message_ids}"