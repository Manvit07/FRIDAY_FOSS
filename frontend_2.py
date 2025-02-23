import customtkinter as ctk
import threading
from FRIDAY import takeCommand, speak, switch_input_mode, commands, create_project

# Initialize main window
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("blue")  # Blue theme

class FridayGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FRIDAY - AI Assistant")
        self.geometry("600x400")
        
        # Status Label
        self.status_label = ctk.CTkLabel(self, text="FRIDAY is Ready", font=("Arial", 16))
        self.status_label.pack(pady=10)
        
        # Output Box
        self.output_box = ctk.CTkTextbox(self, height=5)
        self.output_box.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Input Box
        self.input_entry = ctk.CTkEntry(self, placeholder_text="Type a command...")
        self.input_entry.pack(pady=5, padx=10, fill='x')
        self.input_entry.bind("<Return>", self.process_text_command)
        
        # Buttons
        self.voice_button = ctk.CTkButton(self, text="Voice Command", command=self.process_voice_command)
        self.voice_button.pack(pady=5)
        
        self.switch_mode_button = ctk.CTkButton(self, text="Switch Mode", command=self.toggle_mode)
        self.switch_mode_button.pack(pady=5)
        
        self.create_project_button = ctk.CTkButton(self, text="Create Project", command=self.create_project_ui)
        self.create_project_button.pack(pady=5)
    
    def process_text_command(self, event=None):
        command = self.input_entry.get()
        self.input_entry.delete(0, 'end')
        self.display_output(f"You: {command}")
        threading.Thread(target=self.execute_command, args=(command,)).start()
    
    def process_voice_command(self):
        self.display_output("Listening...")
        threading.Thread(target=self.handle_voice_input).start()
    
    def handle_voice_input(self):
        command = takeCommand()
        self.display_output(f"You: {command}")
        self.execute_command(command)
    
    def execute_command(self, command):
        if command == "create project":
            self.create_project_ui()
        elif command in commands:
            commands[command]()
        else:
            speak("Command not recognized.")
        self.display_output("FRIDAY: Command Executed.")
    
    def display_output(self, message):
        self.output_box.insert('end', message + '\n')
        self.output_box.see('end')
    
    def toggle_mode(self):
        switch_input_mode()
        self.display_output("Input mode switched.")
    
    def create_project_ui(self):
        self.display_output("Select a project category: 1) frontend, 2) backend, 3) data science, 4) machine learning, 5) mobile app, 6) cpp project, 7) c project")
        threading.Thread(target=create_project).start()

if __name__ == "__main__":
    app = FridayGUI()
    app.mainloop()
