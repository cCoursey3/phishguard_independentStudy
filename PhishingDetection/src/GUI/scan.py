import tkinter as tk
from tkinter import font

from googleapiclient.discovery import build
from PhishingDetection.src.service.gmailService import GmailService
from PhishingDetection.src.models.account import Account
from PhishingDetection.src.manager.emailManager import EmailManager
from PhishingDetection.src.manager.accountManager import AccountManager
from PhishingDetection.src.emails.query import Query
from PhishingDetection.src.manager.queryManager import Query_Manager
from PhishingDetection.src.manager.tokenManager import TokenManager
from PhishingDetection.src.reader.email_reader import Email_Reader
from PhishingDetection.src.models.email import Email

SERVICE = None
ACCOUNT = None
OWNER = None

class Scan_Screen(tk.Frame):
    def __init__(self, parent, controller, account, service, user_id):
        super().__init__(parent)
        self.controller = controller
        print(account)
        self.service = service
        self.account = account
        global SERVICE, ACCOUNT, OWNER
        SERVICE = service
        ACCOUNT = self.account
        OWNER = user_id
        self.account.active_account = True
 
        self.controller = controller
        self.configure(bg='#464343')
        # Fonts for the title
        title_font = font.Font(family="Ink Free", size=48, weight="bold")
        font_2 = font.Font(family="Ink Free", size=24, weight="bold")
        small_font = font.Font(family="Ink Free", size=10, weight="bold")

        # Back to Menu button
        back_button = tk.Button(self, text="Back to Menu", command=lambda: controller.show_frame("Menu_Screen"), bg='#464343', fg='blue', font=small_font, relief="flat", cursor="hand2")
        back_button.place(x=10, y=10)

        # Create the title frame
        title_frame = tk.Frame(self, bg='#464343')
        title_frame.pack(fill="x", pady=(40, 10))

        # Create the "Scan Emails" label
        title_label = tk.Label(title_frame, text="Scan Emails", font=title_font, fg="white", bg='#464343')
        title_label.pack(anchor="center")

        # Create a label with instructions or information
        info_label = tk.Label(self, text="Select the emails you want to scan for phishing.", font=font_2, fg="white", bg='#464343')
        info_label.pack(pady=20)

        # Add the options
        self.options()

    def options(self):
        font_2 = font.Font(family="Ink Free", size=18, weight="bold")

        options_frame = tk.Frame(self, bg='#464343')
        options_frame.pack(pady=10, anchor="center")

        # Today's Emails
        today_button = tk.Button(options_frame, text="Today's Emails", command=lambda: handle_option("today", self.controller), bg='#1E1E1E', fg='white', font=font_2)
        today_button.grid(row=0, column=0, pady=5, columnspan=4)

        # Yesterday's Emails
        yesterday_button = tk.Button(options_frame, text="Yesterday's Emails", command=lambda: handle_option("yesterday", self.controller), bg='#1E1E1E', fg='white', font=font_2)
        yesterday_button.grid(row=1, column=0, pady=5, columnspan=4)

        # Emails from past X days
        past_days_label = tk.Label(options_frame, text="Emails from past", font=font_2, fg='white', bg='#464343')
        past_days_label.grid(row=2, column=0, pady=5, sticky="e")

        self.past_days_entry = tk.Entry(options_frame, font=font_2, width=6)
        self.past_days_entry.grid(row=2, column=1, pady=5)

        past_days_text = tk.Label(options_frame, text="days", font=font_2, fg='white', bg='#464343')
        past_days_text.grid(row=2, column=2, pady=5, sticky="w")

        past_days_submit = tk.Button(options_frame, text="Submit", command=lambda: handle_option("past_days", self.controller,self.past_days_entry.get()), bg='#1E1E1E', fg='white', font=font_2)
        past_days_submit.grid(row=2, column=3, pady=5)

        # Past X emails
        past_emails_label = tk.Label(options_frame, text="Past", font=font_2, fg='white', bg='#464343')
        past_emails_label.grid(row=3, column=0, pady=5, sticky="e")

        self.past_emails_entry = tk.Entry(options_frame, font=font_2, width=6)
        self.past_emails_entry.grid(row=3, column=1, pady=5)

        past_emails_text = tk.Label(options_frame, text="emails", font=font_2, fg='white', bg='#464343')
        past_emails_text.grid(row=3, column=2, pady=5, sticky="w")

        past_emails_submit = tk.Button(options_frame, text="Submit", command=lambda: handle_option("past_emails", self.controller, self.past_emails_entry.get()), bg='#1E1E1E', fg='white', font=font_2)
        past_emails_submit.grid(row=3, column=3, pady=5)

        # Choose which emails
        choose_button = tk.Button(options_frame, text="Choose which emails", command=lambda: handle_option("choose", self.controller), bg='#1E1E1E', fg='white', font=font_2)
        choose_button.grid(row=4, column=0, columnspan=4, pady=5)

def handle_option(option, controller, value=None):
    global SERVICE, ACCOUNT, OWNER
    
    query = Query(ACCOUNT, SERVICE)
    
    manager_id = AccountManager().get_manager_id(OWNER)
    
    account_id = TokenManager(account = ACCOUNT).get_id_by_account(manager_id)
    
    
    match option:
        case "today":
            query.text = query.get_today_query()
            query.message_ids = query.list_message_ids(query.text)   
            
        case "yesterday":
            query.text = query.get_yesterday_query()
            query.message_ids = query.list_message_ids(query.text)
        case "past_days":
            query.text = query.get_past_X_day_query(value)
            query.message_ids = query.list_message_ids(query.text)
        case "past_emails":
            query.text = query.get_X_email_query(value)
            query.message_ids = query.get_past_X_emails(value)
        case "choose":
            print("This will be implemented in later versions")
        case _:
            print("Invalid option")

    Query_Manager(query).save_to_db(account_id)
    controller.show_frame("Result_Screen", service=SERVICE, message_ids=query.message_ids)
    
    

