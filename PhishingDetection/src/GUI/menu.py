import os
import tkinter as tk
from tkinter import font
from psd_tools import PSDImage
from PIL import Image, ImageTk
from PhishingDetection.src.service.gmailService import GmailService
from PhishingDetection.src.service.yahooService import YahooService
from PhishingDetection.src.service.outlookService import OutlookService
from PhishingDetection.src.models.account import Account
from PhishingDetection.src.manager.accountManager import AccountManager
from PhishingDetection.src.manager.ownerManager import OwnerManager
from PhishingDetection.src.manager.tokenManager import TokenManager
from PhishingDetection.src.emails.OAuthHandler import OAuthHandler
import logging

SERVICE = None
#logging.basicConfig(level=logging.DEBUG)

class Menu_Screen(tk.Frame):
    def __init__(self, parent, controller, user_id):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.configure(bg='#464343')
        
        arrow = "←"
        back_text = f"{arrow} Back"
        back_font = font.Font(family = "Times New Roman", size = 18, weight = "bold")
        back_button =  tk.Button(self, text=f"{back_text}", font= back_font, command=self.go_back, bg='#464343', bd=0)
        back_button.pack()

        
        # Fonts for the title and buttons
        title_font = font.Font(family="Ink Free", size=48, weight="bold")
        button_font = font.Font(family="Ink Free", size=24, weight="bold")

        # Create the title frame
        title_frame = tk.Frame(self, bg='#464343')
        title_frame.pack(fill="x", pady=(20, 10))
        
        # Create the "Choose a service to connect with" label
        title_label = tk.Label(title_frame, text="Choose a service to connect with", font=title_font, fg="white", bg='#464343')
        title_label.pack(anchor="center")

        # Service selection frame using grid layout
        self.service_frame = tk.Frame(self, bg='#464343')
        self.service_frame.pack(expand=True, fill="both")

        self.service_frame.columnconfigure(0, weight=1)
        self.service_frame.columnconfigure(1, weight=1)
        self.service_frame.rowconfigure(0, weight=1)
        self.service_frame.rowconfigure(1, weight=1)

        # Correct image folder path
        image_folder = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\images\EMAIL_LOGOS"

        # Load images
        self.gmail_image = self.load_psd_image(os.path.join(image_folder, "GMAILLOGO.psd"))
        self.aol_image = self.load_psd_image(os.path.join(image_folder, "AOLLOGO.psd"))
        self.yahoo_image = self.load_psd_image(os.path.join(image_folder, "YAHOOLOGO.psd"))
        self.outlook_image = self.load_psd_image(os.path.join(image_folder, "OUTLOOKLOGO.psd"))

        # Service buttons with images
        self.gmail_button = tk.Button(self.service_frame, image=self.gmail_image, command=self.connect_gmail, bg='#464343', bd=0)
        self.gmail_button.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.aol_button = tk.Button(self.service_frame, image=self.aol_image, command=self.connect_aol, bg='#464343', bd=0)
        self.aol_button.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.yahoo_button = tk.Button(self.service_frame, image=self.yahoo_image, command=self.connect_yahoo, bg='#464343', bd=0)
        self.yahoo_button.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.outlook_button = tk.Button(self.service_frame, image=self.outlook_image, command=self.connect_outlook, bg='#464343', bd=0)
        self.outlook_button.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        self.current_service = None
        self.webview_window = None  # Store the webview window reference

    def load_psd_image(self, path):
        psd = PSDImage.open(path)
        image = psd.topil()
        image = image.convert("RGB")
        image = image.resize((400, 400), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def go_back(self):
        self.controller.show_frame("Initial_Screen", user_id=self.user_id)
        
    def connect_gmail(self):
        global SERVICE
        SERVICE = "Gmail"
        self.current_service = GmailService()
        auth_url = self.current_service.get_authorization_url()
        OAuthHandler(self.controller).start_local_server(SERVICE, auth_url, self.user_id)

    def connect_aol(self):
        global SERVICE
        SERVICE = "AOL"
        self.current_service = YahooService(service_name = SERVICE)
        auth_url = self.current_service.get_authorization_url()
        OAuthHandler(self.controller).start_local_server(SERVICE, auth_url, self.user_id)

    def connect_outlook(self):
        global SERVICE
        SERVICE = "Outlook"
        self.current_service = OutlookService()
        auth_url = self.current_service.get_authorization_url()
        self.controller.code_verifier = self.current_service.code_verifier 
        OAuthHandler(self.controller).start_local_server(SERVICE, auth_url, self.user_id)

        
    def connect_yahoo(self):
        global SERVICE
        SERVICE = "Yahoo"
        self.current_service = YahooService(service_name = SERVICE)
        auth_url = self.current_service.get_authorization_url()
        OAuthHandler(self.controller).start_local_server(SERVICE, auth_url, self.user_id)



