import PhishingDetection.src.analysis.analyze_email as analysis
from PhishingDetection.src.manager.emailManager import EmailManager
import tkinter as tk
from tkinter import font
import threading
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk
import PhishingDetection.src.analysis.analyze_email as analysis
from PhishingDetection.src.models.email import Email
from PhishingDetection.src.reader.email_reader import Email_Reader
import PhishingDetection.src.analysis.image_check as i_check
import PhishingDetection.src.analysis.probability as res


class Result_Screen(tk.Frame):
    def __init__(self, parent, controller, service, message_ids):
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.message_ids = message_ids
        self.configure(bg='#464343')

        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=2, uniform="group1")
        self.grid_rowconfigure(0, weight=1)

        # Create the left frame (1/3 of the width)
        self.left_frame = tk.Frame(self, bg='#333333')
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Create the right frame (2/3 of the width)
        self.right_frame = tk.Frame(self, bg='#555555')
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Create a scrollable canvas for the left frame
        self.canvas = tk.Canvas(self.left_frame, bg='#333333')
        self.scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview, width=15)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#333333')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Load and display emails
        self.email_buttons = []
        self.load_emails()

    def load_emails(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for idx, email_id in enumerate(self.message_ids):
                executor.submit(self.process_email, email_id, idx)

    def process_email(self, email_id, idx):
        
        reader = Email_Reader(self.service, email_id)
        header = reader.parse_header()
        body = reader.parse_body()
        
        email = Email(sender=header[0], recipient=header[2], subject=header[1], body=body)
        mgr = EmailManager(service=self.service, email=email, message_id=email_id)
        mgr.add_to_database(header=header, body=body)
        
        
        print(f"\n\n\n{body}")
        result = analysis.process_email(email)
        #res.calcualte_probability(result)
            
        
        #TODO Implement image checks
        #i_check.image_check(image_urls)
        

        #TODO implement attachment checks
    

        
        

        
    