import tkinter as tk
from PhishingDetection.src.GUI.initial_screen import Initial_Screen
from PhishingDetection.src.GUI.menu import Menu_Screen
from PhishingDetection.src.GUI.scan import Scan_Screen
from PhishingDetection.src.GUI.returnUser import ReturnUser_Screen
from PhishingDetection.src.GUI.results import Result_Screen 

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PhishDetect")
        self.geometry("1024x780")
        self.minsize(800, 600)

        self.frames = {}
        initial_screen = Initial_Screen(parent=self, controller=self)
        self.frames["Initial_Screen"] = initial_screen

        self.frames["Menu_Screen"] = None
        self.frames["Scan_Screen"] = None
        self.frames["ReturnUser_Screen"] = None
        self.frames["Result_Screen"] = None

        # Grid layout configuration to expand and fill the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        initial_screen.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Initial_Screen")

    def show_frame(self, page_name, user_id=None, account=None, service=None, message_ids=None):
        print(f"Showing frame: {page_name}, Service: {service}")

        if page_name == "Menu_Screen" and self.frames["Menu_Screen"] is None:
            menu_screen = Menu_Screen(parent=self, controller=self, user_id=user_id)
            self.frames["Menu_Screen"] = menu_screen
            menu_screen.grid(row=0, column=0, sticky="nsew")
            
        elif page_name == "Scan_Screen":
            if self.frames["Scan_Screen"] is None:
                scan_screen = Scan_Screen(parent=self, controller=self, account=account, service=service, user_id=user_id)
                self.frames["Scan_Screen"] = scan_screen
                scan_screen.grid(row=0, column=0, sticky="nsew")
            else:
                if service is not None:
                    self.frames["Scan_Screen"].service = service
                    
        elif page_name == "ReturnUser_Screen":
            if self.frames["ReturnUser_Screen"] is None:
                return_user_screen = ReturnUser_Screen(parent=self, controller=self, user_id=user_id)
                self.frames["ReturnUser_Screen"] = return_user_screen
                return_user_screen.grid(row=0, column=0, sticky="nsew")
            else:
                # Update the user_id for ReturnUser_Screen
                return_user_screen = self.frames["ReturnUser_Screen"]
                return_user_screen.user_id = user_id
                return_user_screen.update_screen()
                
        elif page_name == "Result_Screen":
            if self.frames["Result_Screen"] is None:
                result_screen = Result_Screen(parent=self, controller=self, service=service, message_ids=message_ids)
                self.frames["Result_Screen"] = result_screen
                result_screen.grid(row=0, column=0, sticky="nsew")
            else:
                # Update the message_ids for Result_Screen
                result_screen = self.frames["Result_Screen"]
                result_screen.update_message_ids(message_ids)
                
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
