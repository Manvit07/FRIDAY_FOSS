import customtkinter as ctk
import threading
from FRIDAY import takeCommand, speak, commands

# Initialize GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AssistantGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Personal AI Assistant")
        self.geometry("500x600")
        
        # Label
        self.label = ctk.CTkLabel(self, text="FRIDAY - AI Assistant", font=("Arial", 20))
        self.label.pack(pady=10)
        
        # Textbox for logs
        self.log_box = ctk.CTkTextbox(self, height=300)
        self.log_box.pack(pady=10, padx=10, fill='both')
        
        # Text Input
        self.entry = ctk.CTkEntry(self, placeholder_text="Type a command...")
        self.entry.pack(pady=5, padx=10, fill='x')
        
        # Buttons
        self.send_button = ctk.CTkButton(self, text="Send", command=self.process_input)
        self.send_button.pack(pady=5)
        
        self.voice_button = ctk.CTkButton(self, text="Use Voice", command=self.listen_voice)
        self.voice_button.pack(pady=5)
        
        self.clear_button = ctk.CTkButton(self, text="Clear Logs", command=self.clear_logs)
        self.clear_button.pack(pady=5)
        
    def log_message(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def process_input(self):
        command = self.entry.get().strip().lower()
        if command:
            self.log_message(f"You: {command}")
            self.execute_command(command)
        self.entry.delete(0, 'end')
    
    def listen_voice(self):
        self.log_message("Listening...")
        threading.Thread(target=self.voice_thread, daemon=True).start()
    
    def voice_thread(self):
        command = takeCommand()
        if command and command != "None":
            self.log_message(f"You: {command}")
            self.execute_command(command)
    
    def execute_command(self, command):
        if command in commands:
            commands[command]()
            self.log_message(f"FRIDAY: Executed '{command}'")
        else:
            self.log_message("FRIDAY: I didn't understand that.")
            speak("I didn't understand that.")
    
    def clear_logs(self):
        self.log_box.delete("1.0", "end")

# Run GUI
if __name__ == "__main__":
    app = AssistantGUI()
    app.mainloop()
