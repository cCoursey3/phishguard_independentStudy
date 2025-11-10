import tkinter as tk
from tkinter import font, messagebox
import os
from PIL import Image, ImageTk
import psd_tools
import hashlib
from PhishingDetection.src.models.owner import Owner
from PhishingDetection.src.manager.ownerManager import OwnerManager
from PhishingDetection.src.manager.accountManager import AccountManager


'''A global variable to store the active user account'''
ACTIVE_USER = None

'''A global variable to establish if we are logging in or signing up'''
LOGIN = False


class Initial_Screen(tk.Frame):
    '''
        The initial screen of the application. It contains the login and sign up buttons. As well
        as login and signup functionalities. It is called through main.py
        
        Keyword arguments:
        tk.Frame -- 
    '''
    def __init__(self, parent, controller):
        '''
            The constructor of the class. It creates the widgets and binds the events to the
            corresponding functions. It also sets the background color of the frame.
            
            Keyword arguments:
            parent -- the parent of the frame
            controller -- the controller of the frame
        '''
        super().__init__(parent)
        self.controller = controller
        self.owner_manager = OwnerManager()  # Instantiate OwnerManager

        self.configure(bg='#464343')

        # Fonts for the title and buttons
        title_font = font.Font(family="Ink Free", size=48, weight="bold")
        
        # Create the title frame
        title_frame = tk.Frame(self, bg='#464343')
        title_frame.pack(fill="x", pady=(20, 10))

        # Create the "Welcome to" label
        fish_icon = "🎣"
        phish_label = tk.Label(title_frame, text=f"Welcome to Ph{fish_icon}shDetect!", font=title_font, fg="white", bg='#464343')
        phish_label.pack(anchor="center")

        # Animation frame
        animation_frame = tk.Frame(self, bg='#464343')
        animation_frame.pack(fill="x", pady=(10, 10))

        self.animation_label = tk.Label(animation_frame, bg='#464343')
        self.animation_label.pack(anchor="center")

        self.image_folder = r"C:\Users\Chloe\git\IndependentStudy\phishingDetection\PhishingDetection\files\images\LoginBackground"  # Replace with your image folder path
        self.image_file = "earth_01.psd"  # Single image file to load

        self.desired_size = (750, 400)  # Size for the images
        self.load_single_image()

        # Check if there is already an active owner
        active_owner = self.owner_manager.get_active_owner()
        if active_owner is not None: #if so, automatically welcome the user
            global ACTIVE_USER
            ACTIVE_USER = active_owner
            self.display_logged_in_screen(active_owner)
        else:  #if not, display the option to login or signup
            self.display_login_signup_screen()
        
    

    def display_logged_in_screen(self, active_owner):
        '''
        
        '''
        question_font = submit_font = font.Font(family="Times New Roman", size=16)
        submit_font = font.Font(family="Ink Free", size=18, weight="bold")
        input_font = font.Font(family="Ink Free", size=18)
        self.welcome_frame = tk.Frame(self, bg='#464343')
        self.welcome_label = tk.Label(self.welcome_frame, text=f"Welcome back {active_owner.firstName} {active_owner.lastName}.", font=submit_font, fg="white", bg='#464343')
        self.welcome_label.pack(fill="x", pady=(20, 10))
        self.welcome_frame.pack()
        
        self.pin_frame = tk.Frame(self, bg='#464343')
        self.pin_entry = tk.Entry(self.pin_frame, font=input_font, fg="light grey", show="", width=30)
        self.pin_entry.insert(0, "PIN")
        self.pin_entry.bind("<FocusIn>", self.clear_placeholder)
        self.pin_entry.bind("<FocusOut>", self.add_placeholder)
        self.pin_entry.pack(side="left", padx=10)
        self.info_icon = tk.Label(self.pin_frame, text="ⓘ", font=input_font, fg="white", bg='#464343')
        self.info_icon.pack(side="left", padx=10)
        self.info_icon.bind("<Enter>", self.show_info)
        self.info_icon.bind("<Leave>", self.hide_info)
        self.info_label = tk.Label(self.pin_frame, text="Create a 4-6 digit PIN", font=input_font, fg="light grey", bg='#464343')
        self.info_label.pack_forget()
        self.pin_frame.pack(pady=(10, 0))
        
        #########################################################################
        self.submit_frame = tk.Frame(self, bg='#464343')
        self.submit_frame.pack(pady=(10,0))
        self.submit_button = tk.Button(self.submit_frame, text="Login", font=submit_font, fg="white", bg='#1E1E1E', command=self.attempt_login)
        self.submit_button.pack(pady=5)       

        # Create a button/link to logout
        self.logout_frame = tk.Frame(self.submit_frame, bg='#464343')
        self.logout_frame.pack(pady=(4,0))
        
        question_font2 = font.Font(family="Times New Roman", size=16, underline=True)
        
        self.logout_label = tk.Label(self.logout_frame, text="Not you? click", font=question_font, fg="white", bg='#464343')
        self.logout_button = tk.Label(self.logout_frame, text="here", font=question_font2, fg="blue", bg='#464343', cursor="hand2")
        self.logout_label2 = tk.Label(self.logout_frame, text="to login as another user or ", font=question_font, fg="white", bg='#464343')
        self.logout_button2 = tk.Label(self.logout_frame, text="here", font=question_font2, fg="blue", bg='#464343', cursor="hand2")
        self.logout_label3 = tk.Label(self.logout_frame, text="to signup as a new user ", font=question_font, fg="white", bg='#464343')
        
        
        self.logout_label.pack(side="left", pady=(0, 0))
        self.logout_button.pack(side="left", padx=(5, 0))
        self.logout_button.bind("<Button-1>", self.logout)
        self.logout_label2.pack(side="left", padx=(5, 0))
        self.logout_button2.pack(side="left", padx=(5, 0))
        self.logout_label3.pack(side="left", padx=(5, 0))
        self.logout_button2.bind("<Button-1>", self.logoutToSignUp)
        
        # Message label for validation feedback
        self.message_label = tk.Label(self, text="", font=input_font, fg="red", bg='#464343')
        self.message_label.pack(pady=(0, 20))

    def logout(self, event=None):
        # Display login/signup inputs and buttons
        LOGIN = True
        self.welcome_label.pack_forget()
        self.logout_frame.pack_forget()
        self.submit_button.pack_forget()
        id = self.owner_manager.get_owner_id(ACTIVE_USER)
        self.owner_manager.set_owner_inactive(id)
        self.display_input()
        
    def logoutToSignUp(self, event = None):
        # Display login/signup inputs and buttons
        global LOGIN
        LOGIN = False
        self.welcome_label.pack_forget()
        self.logout_frame.pack_forget()
        self.submit_button.pack_forget()
        id = self.owner_manager.get_owner_id(ACTIVE_USER)
        self.owner_manager.set_owner_inactive(id)
        self.display_input()
        
    def display_login_signup_screen(self):      
        button_font = font.Font(family="Ink Free", size=24, weight="bold")
        # Create a frame for login inputs and buttons        
        self.button_frame = tk.Frame(self, bg='#464343')
        self.button_frame.pack(fill="x", pady=(20, 20))

        # Create LOGIN button
        self.login_button = tk.Button(self.button_frame, text="LOGIN", font=button_font, fg="white", bg='#1E1E1E', command=self.login)
        self.login_button.pack(side="left", padx=20, pady=20, expand=True)

        # Create SIGNUP button
        self.signup_button = tk.Button(self.button_frame, text="SIGNUP", font=button_font, fg="white", bg='#1E1E1E', command=self.signup)
        self.signup_button.pack(side="right", padx=20, pady=20, expand=True)


    def display_input(self):
        global LOGIN
        # Create a frame for login inputs and buttons 
        if hasattr(self, 'welcome_frame'):
            self.name_frame = tk.Frame(self.welcome_frame, bg='#464343')
            self.name_frame.pack(fill="x", padx=35, pady=(10, 0))
        else:
            self.input_frame = tk.Frame(self.button_frame, bg='#464343')
            self.input_frame.pack()
            self.name_frame = tk.Frame(self.input_frame, bg='#464343')
            self.name_frame.pack(fill="x", padx=35, pady=(10, 0))

        submit_font = font.Font(family="Ink Free", size=20, weight="bold")
        input_font = font.Font(family="Ink Free", size=20)
        #########################################################################
        # Create the frame for first name and last name to begin creating an "owner"
        self.first_name_entry = tk.Entry(self.name_frame, font=input_font, fg="light grey", width=15)
        self.first_name_entry.insert(0, "First Name")
        self.first_name_entry.bind("<FocusIn>", self.clear_placeholder)
        self.first_name_entry.bind("<FocusOut>", self.add_placeholder)
        self.first_name_entry.grid(row=0, column=0, padx=(10, 10), pady=10)

        # Last Name entry
        self.last_name_entry = tk.Entry(self.name_frame, font=input_font, fg="light grey", width=18)
        self.last_name_entry.insert(0, "Last Name")
        self.last_name_entry.bind("<FocusIn>", self.clear_placeholder)
        self.last_name_entry.bind("<FocusOut>", self.add_placeholder)
        self.last_name_entry.grid(row=0, column=1, padx=(10, 10), pady=10)

        self.name_frame.pack(fill="x", padx=35, pady=(10, 0))
        
        #########################################################################
        if not hasattr(self, 'pin_frame'):
            self.pin_frame = tk.Frame(self.input_frame, bg='#464343')
            self.pin_entry = tk.Entry(self.pin_frame, font=input_font, fg="light grey", show="", width=30)
            self.pin_entry.insert(0, "PIN")
            self.pin_entry.bind("<FocusIn>", self.clear_placeholder)
            self.pin_entry.bind("<FocusOut>", self.add_placeholder)
            self.pin_entry.pack(side="left", padx=10)
            self.info_icon = tk.Label(self.pin_frame, text="ⓘ", font=input_font, fg="white", bg='#464343')
            self.info_icon.pack(side="left", padx=10)
            self.info_icon.bind("<Enter>", self.show_info)
            self.info_icon.bind("<Leave>", self.hide_info)
            self.info_label = tk.Label(self.pin_frame, text="Create a 4-6 digit PIN", font=input_font, fg="light grey", bg='#464343')
            self.info_label.pack_forget()
            self.pin_frame.pack(pady=(10, 0))

    #########################################################################
    # Create the submit frame
        if hasattr(self, 'submit_frame'):
            if LOGIN is True:
                self.submit_button = tk.Button(self.submit_frame, text="Login", font=submit_font, fg="white", bg='#1E1E1E', command=self.submit)
            else: 
               self.submit_button = tk.Button(self.submit_frame, text="Signup", font=submit_font, fg="white", bg='#1E1E1E', command=self.submit)
               
        else:
            self.submit_frame = tk.Frame(self.input_frame, bg='#464343')
            if LOGIN is True:
                self.submit_button = tk.Button(self.submit_frame, text="Login", font=submit_font, fg="white", bg='#1E1E1E', command=self.submit)
            else: 
               self.submit_button = tk.Button(self.submit_frame, text="Signup", font=submit_font, fg="white", bg='#1E1E1E', command=self.submit)
            self.submit_frame.pack()
            # Message label for validation feedback
            self.message_label = tk.Label(self.input_frame, text="", font=input_font, fg="red", bg='#464343')
            self.message_label.pack(pady=(5, 0))

            # Message label for validation feedback
            self.message_label = tk.Label(self.input_frame, text="", font=input_font, fg="red", bg='#464343')
            self.message_label.pack(pady=(5, 0))
        
        self.submit_button.pack(pady=20)




    def load_single_image(self):
        image_path = os.path.join(self.image_folder, self.image_file)
        try:
            psd = psd_tools.PSDImage.open(image_path)
            image = psd.compose()
            image = image.resize(self.desired_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.animation_label.config(image=photo)
            self.animation_label.image = photo
        except FileNotFoundError as e:
            print(f"Error: {e}")

    def hide_buttons(self):
        self.login_button.pack_forget()
        self.signup_button.pack_forget()

    def login(self):
        global LOGIN
        LOGIN = True
        self.hide_buttons()  # Hide login and signup buttons
        self.display_input()  # Show input fields for login
        self.submit_button.config(command=self.attempt_login)  # Set submit button command for login

    def signup(self):
        global LOGIN
        LOGIN = False
        self.hide_buttons()  # Hide login and signup buttons
        
        if ACTIVE_USER is not None:
            id = self.owner_manager.get_owner_id(ACTIVE_USER)
            self.owner_manager.set_owner_inactive(id)
            self.welcome_frame.pack_forget()
            self.logout_frame.pack_forget()
            
        self.display_input()  # Show input fields for signup
        self.submit_button.config(command=self.submit)  # Set submit

    def clear_placeholder(self, event):
        if event.widget.get() in ["First Name", "Last Name", "PIN"]:
            event.widget.delete(0, tk.END)
            event.widget.config(fg="black")

    def add_placeholder(self, event):
        if event.widget.get() == "":
            if event.widget == self.first_name_entry:
                event.widget.insert(0, "First Name")
            elif event.widget == self.last_name_entry:
                event.widget.insert(0, "Last Name")
            else:
                event.widget.pinsert(0, "PIN")
            event.widget.config(fg="light grey")


    def show_info(self, event):
        self.info_label.pack(side="left", padx=10)

    def hide_info(self, event):
        self.info_label.pack_forget()

    def submit(self):
        firstNAME = self.first_name_entry.get()
        lastNAME = self.last_name_entry.get()
        pin = self.pin_entry.get()
        # Validate PIN length
        if len(pin) < 4:
            messagebox.showerror("Error", "The PIN is too short")
        elif len(pin) > 6:
            messagebox.showerror("Error", "The PIN is too long")
        elif len(firstNAME) is None or len(lastNAME) is None:
            messagebox.showerror("Error", "Please enter a first and last name")
        else:
            hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
            owner = Owner(firstNAME, lastNAME, hashed_pin, bypass_pin_validation = True)
            ACTIVE_USER = owner
            if (self.owner_manager.add_owner(ACTIVE_USER)): #owner is now in the database
                id = self.owner_manager.get_owner_id(ACTIVE_USER)
                self.owner_manager.set_owner_active(id)
                account_manager = AccountManager(id)
                account_id = account_manager.get_manager_id(id)
                self.owner_manager.add_manager_id(id, account_id)
                self.controller.show_frame("Menu_Screen", id)  # Transition to the Menu_Screen
            else:
               messagebox.showerror("Error", "Username is already taken, please enter a different one.")
            
    def attempt_login(self):
        global ACTIVE_USER
        if ACTIVE_USER is None:
            new_owner = Owner(self.first_name_entry.get(), self.last_name_entry.get(),pin = self.pin_entry.get())
            ACTIVE_USER = new_owner

        response = self.owner_manager.find_owner(ACTIVE_USER, self.pin_entry.get())
        
        if response == "Success":
            id = self.owner_manager.get_owner_id(ACTIVE_USER)
            self.owner_manager.set_owner_active(id)
                
            acc_manager_ID = self.owner_manager.get_manager_id()
            account_manager = AccountManager()
            accounts = account_manager.get_accounts_by_id(acc_manager_ID, id)
                
            if accounts is None:
                self.controller.show_frame("Menu_Screen", id)  # Call the next screen
            else:
                self.controller.show_frame("ReturnUser_Screen", id)
                    
        elif response == "Invalid User Names or PIN":
            messagebox.showerror("Error", "Invalid username or PIN!")
        else:
            messagebox.showerror("Error" "you may not have an account with us, try signing up or try again")



