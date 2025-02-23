import json
import pyttsx3
import speech_recognition as sr
import datetime
import os
import cv2
import pyautogui
import time
import pywhatkit as wk
from difflib import get_close_matches
import spacy
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import requests
import webbrowser
import random
#=========================================================NLP & LEARNING MODE========================================================================#

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Learning Mode Flag
LEARNING_MODE = False

def extract_keywords(user_query):
    """Extracts important keywords (nouns, verbs) from the user command."""
    doc = nlp(user_query)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "VERB", "PROPN"]]
    return " ".join(keywords)

def match_command(user_query):
    """Matches user query with available commands using fuzzy matching and past learning."""
    processed_query = extract_keywords(user_query)
    command_list = list(commands.keys())

    # Check past interactions for better matching
    past_data = load_past_interactions()
    if user_query in past_data:
        return past_data[user_query]  # Return the stored command if found

    best_match, score = process.extractOne(processed_query, command_list)

    if score > 60:  # Confidence threshold
        return best_match
    else:
        return None

def process_command(user_query):
    matched_command = match_command(user_query)

    if matched_command:
        response = f"Executing {matched_command}"
        speak(response)
        commands[matched_command]()

        if LEARNING_MODE:
            store_interaction(user_query, matched_command)
    else:
        response = "Sorry, I didn't understand that command."
        speak(response)

        if LEARNING_MODE:
            store_interaction(user_query, "Unknown")

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 200)

use_voice = False  # Default mode is Voice Input

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def switch_input_mode():
    """Toggles between voice mode and manual typing mode."""
    global use_voice
    use_voice = not use_voice
    mode = "voice mode" if use_voice else "manual typing mode"
    speak(f"Switched to {mode}.")
    print(f"Mode changed: {mode}")


def takeCommand():
    """Takes user input either by voice or manual typing based on mode."""
    if use_voice:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=1)
            r.pause_threshold = 0.8
            audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that. Please say that again.")
            return "None"
        except sr.RequestError:
            print("Could not request results. Check your internet connection.")
            return "None"
    else:
        query = input("Type your command: ").lower()
        return query

# Data Storage Functions

def store_interaction(user_input, system_response):
    """Stores user commands and system responses for learning."""
    data = load_past_interactions()
    data[user_input] = system_response

    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

def load_past_interactions():
    """Loads stored user interactions from file."""
    if os.path.exists("data.json"):
        with open("data.json", "r") as file:
            return json.load(file)
    return {}

#=========================================================NLP & LEARNING MODE========================================================================#

# Functionalities

def get_time():
    return datetime.datetime.now().strftime("%H:%M")

def get_date():
    return datetime.datetime.now().strftime('%d %B %Y')

def get_day():
    return datetime.datetime.now().strftime("%A")

def open_youtube():
    speak("Which song would you like to listen to?")
    song = takeCommand()
    if song != "None":
        wk.playonyt(song)

def get_google_summary(query):
    search_url = f"https://www.google.com/search?q={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    summary = soup.find('span', {'class': 'aCOpRe'})
    if summary:
        return summary.text
    else:
        return "I could not find a summary for that topic."

def ok_google():  
    speak("What should I search for you, sir?")
    qry = takeCommand().lower()
    if qry != "None":
        summary = get_google_summary(qry)
        speak(summary)
        webbrowser.open(f"https://www.google.com/search?q={qry}")
        speak("These are some of the most viewed sites.")

def open_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Error: Could not open camera.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            speak("Error: Failed to capture frame.")
            break
        cv2.imshow("Webcam", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def take_screenshot():
    speak("Tell me a name for the file")
    name = takeCommand()
    if name == "None":
        return
    time.sleep(2)
    screenshot_directory = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
    if not os.path.exists(screenshot_directory):
        os.makedirs(screenshot_directory)
    file_path = os.path.join(screenshot_directory, f"{name}.png")
    img = pyautogui.screenshot()
    img.save(file_path)
    speak(f"Screenshot saved as {file_path}")

def volume_up():
    for _ in range(5):
        pyautogui.press("volumeup")

def volume_down():
    for _ in range(5):
        pyautogui.press("volumedown")


#==========================================================================file_structure=================================================================#

def create_project_structure_from_text(base_dir, structure_details):
    """Parses a formatted structure list and creates directories and files accordingly."""
    stack = [(0, base_dir)]  # Stack to track directory levels

    for line in structure_details:
        indent_level = len(line) - len(line.lstrip())
        item_name = line.strip().replace("│", "").replace("├──", "").replace("└──", "").strip()

        while stack and stack[-1][0] >= indent_level:
            stack.pop()
        
        parent_dir = stack[-1][1] if stack else base_dir  # Ensure a valid parent directory

        current_path = os.path.join(parent_dir, item_name.rstrip("/"))
        
        if item_name.endswith("/"):  # Directory
            os.makedirs(current_path, exist_ok=True)
            stack.append((indent_level, current_path))
            print(f"Created directory: {current_path}")
        else:  # File
            with open(current_path, "w", encoding="utf-8") as f:
                f.write(f"// {item_name} placeholder\n")
            print(f"Created file: {current_path}")
    
    print("Project structure created successfully!")

def load_project_structures():
    """Loads predefined project structures from a JSON file."""
    with open("project_structures.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_random_structure(category):
    """Fetches a random structure from a given category."""
    structures = project_structures.get(category, [])
    if structures:
        return random.choice(structures)["details"]
    return None

def create_project():
    """Handles user input to create a project directory structure."""
    speak("Which type of project structure do you need?")
    print("Enter the project structure category 1) frontend, 2) backend, 3) data science, 4) machine learning, 5) mobile app, 6) cpp project, 7) c project")
    speak("Enter the project structure category 1) frontend, 2) backend, 3) data science, 4) machine learning, 5) mobile app, 6) cpp project, 7) c project")
    category = takeCommand().lower()

    if category in project_structures:
        while True:
            structure_details = get_random_structure(category)
            if not structure_details:
                speak("Sorry, no structures available for this category.")
                return
            
            speak("Should I create the following project structure?")
            print("\n".join(structure_details))
            
            speak("Say yes to create it or no to see another option.")
            user_response = takeCommand().lower()
            
            if "yes" in user_response:
                create_project_structure_from_text("my_project", structure_details)
                speak("Project has been successfully created.")
                break
            elif "no" in user_response:
                speak("Here is another option.")
                continue
            else:
                speak("Invalid response. Cancelling operation.")
                break
    else:
        speak("Invalid category. Please try again.")

# Load project structures from JSON file
project_structures = load_project_structures()


#==========================================================================file_structure=================================================================#

commands = {
    "switch mode": switch_input_mode,  # Command to change mode
    "time": lambda: speak(f"The time is {get_time()}"),
    "date": lambda: speak(f"Today's date is {get_date()}"),
    "day": lambda: speak(f"Today is {get_day()}"),
    "create project": create_project,
    "play music": open_youtube,
    "open camera": open_camera,
    "take screenshot": take_screenshot,
    "increase volume": volume_up,
    "decrease volume": volume_down,
    "open google": ok_google,
    "shutdown laptop": lambda: os.system("shutdown /s /t 5"),
    "restart laptop": lambda: os.system("shutdown /r /t 5"),
    "lock laptop": lambda: os.system("rundll32.exe user32.dll,LockWorkStation"),
}

if __name__ == "__main__":
    speak("Friday is now active. Do you want to enable learning mode? Say 'yes' or 'no'.")
    
    while True:
        response = takeCommand()
        if "enable learning mode" in response:
            LEARNING_MODE = True
            speak("Learning mode enabled.")
            break
        elif "disable learning mode" in response:
            LEARNING_MODE = False
            speak("Learning mode disabled.")
            break

    speak("Say 'wake up' to start.")

    while True:
        query = takeCommand()
        
        if "wake up" in query:
            speak("Friday in your service. How can I help you today?")
            
            while True:
                query = takeCommand()
                
                if "go to sleep" in query:
                    speak("Going to sleep. Say 'wake up' when you need me.")
                    break
                
                if query in commands:
                    commands[query]()  
                else:
                    process_command(query) 