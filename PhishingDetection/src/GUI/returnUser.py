import tkinter as tk
from tkinter import ttk, Canvas, font, messagebox
from PhishingDetection.src.manager.accountManager import AccountManager
from PhishingDetection.src.manager.ownerManager import OwnerManager
from PhishingDetection.src.manager.tokenManager import TokenManager
from PhishingDetection.src.service.gmailService import GmailService
from PhishingDetection.src.service.yahooService import YahooService
from PhishingDetection.src.service.outlookService import OutlookService
class ReturnUser_Screen(tk.Frame):
    def __init__(self, parent, controller, user_id):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.configure(bg='#464343')
        self.service = None

        title_font = font.Font(family="Ink Free", size=24, weight="bold")
        title_font2 = font.Font(family="Ink Free", size=16, slant="italic")
        small_font = font.Font(family="Ink Free", size=12, underline=True)

        
        back_button = tk.Button(self, text="Add a new Account", command=lambda: controller.show_frame("Menu_Screen", self.user_id), bg='#464343', fg='white', font=small_font, relief="flat", cursor="hand2")
        back_button.place(x=10, y=10)
        
        
        title_frame = tk.Frame(self, bg='#464343')
        title_frame.pack(fill="x", pady=(40, 10))
        title_label = tk.Label(title_frame, text="Welcome Back!", font=title_font, fg="white", bg='#464343')
        title_label2 = tk.Label(title_frame, text="Please choose one of your accounts to connect with", font=title_font2, fg="white", bg="#464343")
        title_label.pack(pady = 10)
        title_label2.pack(pady=10)

        self.canvas = tk.Canvas(self, bg='#464343')
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="center")

        self.retrieve_accounts(self.user_id)

    def retrieve_accounts(self, user_id):
        account_manager = AccountManager()
        owner_manager = OwnerManager()
        acc_manager_ID = owner_manager.get_manager_id()
        accounts = account_manager.get_accounts_by_id(acc_manager_ID, user_id)
        for a in accounts:
            a.active_account = False
            self.create_account_button(a)

    def create_account_button(self, account):
        button_frame = tk.Frame(self.scrollable_frame, bg='#464343', bd=2, relief="solid")
        button_frame.pack(fill="both", expand=True)

        text = f"{(account.service).capitalize()}\n{account.emailAddress}"
        title_font2 = font.Font(family="Times New Roman", size=16)
        rounded_button = RoundedButton(button_frame, text=text, font=title_font2, command=lambda: self.reconnect_account(account), radius=25)
        rounded_button.pack(expand=True, pady=10)

    def reconnect_account(self, account):
        token_manager = TokenManager()
        account_manager = AccountManager()
        manager_id = account_manager.get_manager_id(self.user_id)

        if account.service.lower() == "gmail":
            print("Checking tokens for Gmail account...")
            id = token_manager.get_token_id_from_db(manager_id, account)
            creds = token_manager.get_creds_from_db(id, r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\credentials.json')
            #gmail_service = check_and_refresh_gmail_credentials(manager_id, account, token_manager, creds_file_path)
            gmail_service = GmailService(creds)
            
            print(f"\n\n\n\n\n{gmail_service.credentials.expired}")
            if not gmail_service.credentials.valid or gmail_service.credentials.expired:
                print("Credentials are not valid, refreshing or reauthorizing...")
                gmail_service.refresh_or_reauthorize_credentials(manager_id, account)
            self.controller.show_frame("Scan_Screen", account = account, service=gmail_service, user_id=self.user_id)
            
        elif account.service.lower() in ["yahoo", "aol"]:
            id = token_manager.get_token_id_from_db(manager_id, account)
            creds = token_manager.get_creds_from_db(id, r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\yahoo_credentials.json')
            yahoo_service = YahooService(service_name = account.service, credentials=creds)
            if not yahoo_service.credentials.valid:
                yahoo_service.refresh_or_reauthorize_credentials(manager_id, account)
            self.controller.show_frame("Scan_Screen", account = account, service=yahoo_service, user_id=self.user_id)
        
        elif account.service.lower() == "outlook":
            id = token_manager.get_token_id_from_db(manager_id, account)
            creds = token_manager.get_creds_from_db(id, r'C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\config\outlook_credentials.json')
            outlook_service = OutlookService(credentials=creds)
            if not outlook_service.check_creds():
                outlook_service.refresh_or_reauthorize_credentials(manager_id, account)
            self.controller.show_frame("Scan_Screen", account = account, service=outlook_service, user_id=self.user_id)

class RoundedButton(Canvas):
    def __init__(self, parent, text, font, command=None, radius=5, padding=10, *args, **kwargs):
        Canvas.__init__(self, parent, height=50, bg='#464343', highlightthickness=0, *args, **kwargs)
        self.command = command
        self.radius = radius
        self.padding = padding
        self.text = text
        self.font = font

        self.bind("<Button-1>", self.on_click)
        self.create_rounded_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), radius, fill="#5a9", outline="")

        self.label = tk.Label(self, text=text, font=font, bg="#5a9", fg="white", bd=0, highlightthickness=0)
        self.label.bind("<Button-1>", self.on_click)
        self.create_window((self.winfo_reqwidth()//2, self.winfo_reqheight()//2), window=self.label, anchor="center")

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]

        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        if self.command:
            self.command()
