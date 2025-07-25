import pyttsx3
import speech_recognition as sr
import webbrowser
import sympy as sp
import re
from pywikihow import search_wikihow
import pywhatkit
from bs4 import BeautifulSoup
import os
import wikipedia
import pyautogui
from datetime import datetime
import requests
import keyboard
import pyjokes
from PyDictionary import PyDictionary as Diction
import random
from plyer import notification
import openai_request as ai
import mtranslate
import subprocess
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import threading
import pygame
import numpy as np
import sys
import json

# Initialize pygame for sounds
pygame.mixer.init()

# Global variable for listening state
is_listening = False

class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AIML Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg="#2c3e50")
        
        # Initialize states
        self.listening = False
        self.jarvis_chat = []
        
        # Make window resizable
        self.root.minsize(800, 600)
        
        # Initialize assistant engine
        try:
            self.Assistant = pyttsx3.init('sapi5')
            voices = self.Assistant.getProperty('voices')
            self.Assistant.setProperty('voice', voices[0].id)
            self.Assistant.setProperty('rate', 170)
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.Assistant = None
        
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        
        # Setup UI
        self.setup_ui()
        
        # Conversation history
        self.conversation_history = []
        
        # Animation variables
        self.animation_phase = 0
        self.animation_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f']
        
        # Play welcome sound
        self.play_welcome_sound()
        
        # Load todo list if exists
        self.todo_file = "todolist.txt"
        if not os.path.exists(self.todo_file):
            with open(self.todo_file, 'w') as f:
                f.write("")
    
    def play_welcome_sound(self):
        """Play welcome sound in a separate thread"""
        def play():
            try:
                self.Speak("Hello this is AIML Assistance")
                self.Speak("How can I help You?")
            except Exception as e:
                print(f"Error playing welcome sound: {e}")
        
        threading.Thread(target=play, daemon=True).start()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Label(main_frame, text="WELCOME TO AIML ASSISTANT", 
                         font=("Helvetica", 24, "bold"), 
                         fg="#ecf0f1", bg="#2c3e50")
        header.pack(pady=(0, 20))
        
        # Subheader
        subheader = tk.Label(main_frame, text="This is AIML Department Assistant", 
                            font=("Helvetica", 14), 
                            fg="#bdc3c7", bg="#2c3e50")
        subheader.pack(pady=(0, 30))
        
        # Display area
        self.display_frame = tk.Frame(main_frame, bg="#34495e", bd=2, relief=tk.RAISED)
        self.display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.conversation_display = scrolledtext.ScrolledText(
            self.display_frame, 
            wrap=tk.WORD, 
            font=("Helvetica", 12), 
            bg="#34495e", 
            fg="#ecf0f1", 
            padx=10, 
            pady=10,
            state='disabled'
        )
        self.conversation_display.pack(fill=tk.BOTH, expand=True)
        
        # Mic button frame
        mic_frame = tk.Frame(main_frame, bg="#2c3e50")
        mic_frame.pack(pady=(10, 0))
        
        # Create mic button (using text since images might not be available)
        self.mic_button = tk.Button(
            mic_frame, 
            text="Start Listening",
            font=("Helvetica", 14, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            bd=0,
            relief=tk.FLAT,
            command=self.toggle_listening
        )
        self.mic_button.pack(pady=10)
        
        # Animation canvas for mic
        self.animation_canvas = tk.Canvas(mic_frame, width=120, height=120, bg="#2c3e50", highlightthickness=0)
        self.animation_canvas.pack()
        
        # Status label
        self.status_label = tk.Label(
            main_frame, 
            text="Ready", 
            font=("Helvetica", 12), 
            fg="#bdc3c7", 
            bg="#2c3e50"
        )
        self.status_label.pack(pady=(10, 0))
        
        # Start animation
        self.animate_mic()
    
    def animate_mic(self):
        if self.listening:
            self.animation_phase = (self.animation_phase + 1) % 360
            radius = 50 + 10 * np.sin(np.radians(self.animation_phase * 5))
            
            self.animation_canvas.delete("all")
            color_idx = int(self.animation_phase / 90) % len(self.animation_colors)
            color = self.animation_colors[color_idx]
            
            # Draw pulsing circle
            self.animation_canvas.create_oval(
                60 - radius, 60 - radius, 
                60 + radius, 60 + radius, 
                outline=color, 
                width=3,
                tags="pulse"
            )
            
            # Draw mic icon
            self.animation_canvas.create_oval(40, 40, 80, 80, fill="#e74c3c", outline="")
        
        self.root.after(50, self.animate_mic)
    
    def toggle_listening(self):
        global is_listening
        if not is_listening:
            is_listening = True
            self.start_listening()
        else:
            is_listening = False
            self.stop_listening()
    
    def start_listening(self):
        self.listening = True
        self.mic_button.config(text="Stop Listening", bg="#2ecc71")
        self.status_label.config(text="Listening...", fg="#2ecc71")
        
        # Start listening in a separate thread
        threading.Thread(target=self.listen_for_speech, daemon=True).start()
    
    def stop_listening(self):
        self.listening = False
        self.mic_button.config(text="Start Listening", bg="#e74c3c")
        self.status_label.config(text="Ready", fg="#bdc3c7")
    
    def listen_for_speech(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.update_display("Listening...", "assistant")
                
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    query = self.recognizer.recognize_google(audio, language='en-in')
                    query = mtranslate.translate(query, to_language="en-in").lower()
                    
                    self.update_display(query, "user")
                    self.TaskExe(query)
                    
                except sr.WaitTimeoutError:
                    self.update_display("I didn't hear anything", "assistant")
                    self.Speak("I didn't hear anything")
                except sr.UnknownValueError:
                    self.update_display("Could not understand audio", "assistant")
                    self.Speak("Could not understand audio")
                except Exception as e:
                    self.update_display(f"Error: {str(e)}", "assistant")
                    print(f"Error in speech recognition: {str(e)}")
        except Exception as e:
            self.update_display("Microphone not available", "assistant")
            self.Speak("Microphone not available")
            print(f"Microphone error: {e}")
        
        # Automatically stop listening after processing
        self.root.after(100, self.stop_listening)
    
    def update_display(self, text, sender):
        self.conversation_display.config(state='normal')
        
        if sender == "user":
            prefix = "You: "
            tag = "user"
            self.conversation_display.tag_config(tag, foreground="#3498db")
        else:
            prefix = "Assistant: "
            tag = "assistant"
            self.conversation_display.tag_config(tag, foreground="#2ecc71")
        
        self.conversation_display.insert(tk.END, prefix + text + "\n\n", tag)
        self.conversation_display.config(state='disabled')
        self.conversation_display.see(tk.END)
    
    def Speak(self, audio):
        if not self.Assistant:
            print(f"TTS not available: {audio}")
            return
            
        self.update_display(audio, "assistant")
        try:
            self.Assistant.say(audio)
            self.Assistant.runAndWait()
        except Exception as e:
            print(f"Error in TTS: {e}")
            self.update_display(f"[Error in speech output: {e}]", "assistant")

    # All your original functionality integrated below
    
    def Music(self):
        self.Speak("Tell me the Name of the Song!")
        musicName = self.listen_for_speech()
        
        if musicName:
            if 'akeli' in musicName:
                os.startfile('E:\\Songs\\akeli.mp3')
            elif 'blanko' in musicName:
                os.startfile('E:\\Songs\\blanko.mp3')
            else:
                pywhatkit.playonyt(musicName)
            self.Speak("Your Song has been Started! , Enjoy Sir!")

    def tell_date(self):
        today = datetime.now().strftime("%B %d, %Y")  
        self.Speak(f"Today's date is {today}")

    def tell_time(self):
        current_time = datetime.now().strftime("%I:%M %p")  
        self.Speak(f"The current time is {current_time}")

    def aptitude_calculation(self, query):
        try:
            if "percentage of" in query:
                match = re.search(r'(\d+)%\s+of\s+(\d+)', query)
                if match:
                    percent = int(match.group(1))
                    total = int(match.group(2))
                    result = (percent / 100) * total
                    self.Speak(f"{percent}% of {total} is {result}")

            elif "profit" in query or "loss" in query:
                match = re.search(r'cost price\s+(\d+).*selling price\s+(\d+)', query)
                if match:
                    cost_price = int(match.group(1))
                    selling_price = int(match.group(2))
                    if selling_price > cost_price:
                        profit = selling_price - cost_price
                        self.Speak(f"The profit is {profit}")
                    else:
                        loss = cost_price - selling_price
                        self.Speak(f"The loss is {loss}")

            elif "average of" in query:
                numbers = list(map(int, re.findall(r'\d+', query)))
                if numbers:
                    average = sum(numbers) / len(numbers)
                    self.Speak(f"The average is {average}")

            elif "ratio of" in query:
                match = re.search(r'ratio of (\d+) to (\d+)', query)
                if match:
                    num1 = int(match.group(1))
                    num2 = int(match.group(2))
                    gcd = sp.gcd(num1, num2)
                    simplified_ratio = f"{num1 // gcd} : {num2 // gcd}"
                    self.Speak(f"The ratio of {num1} to {num2} is {simplified_ratio}")

        except Exception as Error:
            self.Speak("Sorry, I couldn't perform the aptitude calculation.")
            print(Error)

    def get_latest_news(self):
        api_key = "cd138b6931984aa3a61dc91e5ea1ce7a"
        url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={api_key}"

        try:
            response = requests.get(url)
            news_data = response.json()
            articles = news_data.get("articles", [])

            if not articles:
                self.Speak("Sorry, I couldn't find any news at the moment.")
                return
            self.Speak("Here are the latest technical news headlines:")
            for i, article in enumerate(articles[:5]): 
                title = article["title"]
                self.Speak(f"News {i + 1}: {title}")

        except Exception as Error:
            self.Speak("Sorry, I couldn't fetch the news.")
            print(Error)

    def play_trivia_quiz(self):
        Questions = {
            "What is the capital of France?": "paris",
            "What is the largest planet in our solar system?": "jupiter",
            "Who wrote 'To Kill a Mockingbird'?": "harper lee",
            "What is the smallest prime number?": "2",
            "What year did the Titanic sink?": "1912"
        }
        score = 0
        total_questions = len(Questions)
        self.Speak("Let's play a trivia quiz! I will ask you a few questions. Try to answer them.")

        for question, answer in random.sample(list(Questions.items()), total_questions):
            self.Speak(question)
            user_answer = self.listen_for_speech()

            if user_answer is None:
                self.Speak("I didn't catch that. Please try again.")
                continue

            if user_answer == answer:
                self.Speak("Correct!")
                score += 1
            else:
                self.Speak(f"Sorry, the correct answer is {answer}.")

        self.Speak(f"Game over! You got {score} out of {total_questions} questions correct.")
        if score == total_questions:
            self.Speak("Excellent! You got all answers correct.")
        elif score > total_questions / 2:
            self.Speak("Good job! You did well.")
        else:
            self.Speak("Better luck next time!")

    def OpenApps(self, query):
        self.Speak("Ok Sir, Wait a Second")
        
        if 'code' in query:
            os.startfile("C:\\Users\\prath\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
        elif 'telegram' in query:
            webbrowser.open("https://www.telegram.com/")
        elif 'chrome' in query:
            os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        elif 'facebook' in query:
            webbrowser.open("https://www.facebook.com/")
        elif 'youtube' in query:
            webbrowser.open("https://www.youtube.com/")
        elif 'instagram' in query:
            webbrowser.open("https://www.instagram.com/")

        self.Speak("Your command has been completed sir!")             

    def Temp(self):
        search = "temperature in Satara"
        url = f"https://www.google.com/search?q={search}"
        r = requests.get(url)
        data = BeautifulSoup(r.text,"html.parser")
        temperature = data.find("div",class_ = "BNeawe").text
        self.Speak(f"The Temperature Outside Is {temperature} celcius")

    def CloseApps(self, query):
        self.Speak("Ok Sir, Wait a Second")

        if 'youtube' in query:
            os.system("TASKKILL /f /im chrome.exe")
        elif 'chrome' in query:
            os.system("TASKKILL /f /im chrome.exe")
        elif 'telegram' in query:
            os.system("TASKKILL /f /im chrome.exe")
        elif 'facebook' in query:
            os.system("TASKKILL /f /im chrome.exe")
        elif 'code' in query:
            os.system("TASKKILL /f /im code.exe")
        elif 'instagram' in query:
            os.system("TASKKILL /f /im chrome.exe")

        self.Speak("Your command has been successfully completed!")

    def YoutubeAuto(self):
        self.Speak("Whats Your Command ?")
        comm = self.listen_for_speech()

        if comm:
            if 'pause' in comm:
                keyboard.press('space bar')
            elif 'restart' in comm:
                keyboard.press('0')
            elif 'mute' in comm:
                keyboard.press('m')
            elif 'skip' in comm:
                keyboard.press('l')
            elif 'back' in comm:
                keyboard.press('j')
            elif 'full screen' in comm:
                keyboard.press('f')
            elif 'film mode' in comm:
                keyboard.press('t')

            self.Speak("Done Sir")

    def ChromeAuto(self):
        self.Speak("Chrome Automation started!")
        command = self.listen_for_speech()

        if command:
            if 'close in tab' in command:
                keyboard.press_and_release('ctrl + W')
            elif 'open new tab' in command:
                keyboard.press_and_release('ctrl + t')
            elif 'open new window' in command:
                keyboard.press_and_release('ctrl + n')
            elif 'history' in command:
                keyboard.press_and_release('ctrl + h')

    def TaskExe(self, query):
        if 'hello' in query:
            self.Speak("Hello sir , I Am Jarvis .")
            self.Speak("Your AI Assistant!")
            self.Speak("How May I Help You Sir?")

        elif 'how are you' in query:
            self.Speak("I Am Fine Sir!")
            self.Speak("Whats About You?")

        elif 'you need a break' in query:
            self.Speak("Ok Sir , You Can Call Me Anytime !")
            self.root.destroy()

        elif 'bye' in query:
            self.Speak("OK Sir , Bye!")
            self.root.destroy()

        elif 'youtube search' in query:
            self.Speak("Ok Sir, This is what i found for your Search!")
            query = query.replace("youtube search","")
            web = 'https://www.youtube.com/results?search_query=' + query
            webbrowser.open(web)
            self.Speak("Done sir")

        elif 'google search' in query:
            self.Speak("This is what I found for Your Search sir")
            query = query.replace("jarvis","")
            query = query.replace("google search","")
            pywhatkit.search(query)
            self.Speak("Done Sir!")

        elif 'website' in query:
            self.Speak("Ok Sir, Launching.....")
            query = query.replace("jarvis","")
            query = query.replace("website","")
            query = query.replace(" ","")
            web1 = query.replace("open","")
            web2 = 'https://www.' + web1 + '.com'
            webbrowser.open(web2)
            self.Speak("Launched!")

        elif 'launch' in query:
            self.Speak("Tell me the Name of the website!")
            name = self.listen_for_speech()
            if name:
                web = 'https://www.' + name + '.com'
                webbrowser.open(web)
                self.Speak("Done Sir!")

        elif "what is the date" in query or "today's date" in query:
            self.tell_date()

        elif "what time is it" in query or "current time" in query:
            self.tell_time()

        elif 'music' in query:
            self.Music()

        elif any(keyword in query for keyword in ["percentage", "profit", "loss", "average", "ratio"]):
            self.aptitude_calculation(query)

        elif "tell me news" in query:
            self.get_latest_news()

        elif "play trivia quiz" in query:
            self.play_trivia_quiz()

        elif 'wikipedia' in query:
            self.Speak("Searching Wikipedia.....")
            query = query.replace("jarvis","")
            query = query.replace("search ","")
            query = query.replace("wikipedia","")
            wiki = wikipedia.summary(query, sentences=2)
            self.Speak(f"According to wikipedia : {wiki}")

        elif 'open facebook' in query or 'open instagram' in query or 'open youtube' in query or 'open chrome' in query or 'open code' in query or 'open telegram' in query:
            self.OpenApps(query)

        elif 'close facebook' in query or 'close chrome' in query or 'close youtube' in query or 'close code' in query or 'close telegram' in query or 'close instagram' in query:
            self.CloseApps(query)

        elif 'youtube tool' in query:
            self.YoutubeAuto()

        elif 'chrome automation' in query:
            self.ChromeAuto()

        elif 'joke' in query:
            get = pyjokes.get_joke()
            self.Speak(get)

        elif 'repeat my words' in query:
            self.Speak("Speak sir!")
            jj = self.listen_for_speech()
            if jj:
                self.Speak(f"You Said : {jj}")

        elif 'remember that' in query:
            remeberMsg = query.replace("remember that","")
            remeberMsg = remeberMsg.replace("jarvis","")
            self.Speak("You Tell Me To Remind you that :" + remeberMsg)
            remeber = open("data.txt","w")
            remeber.write(remeberMsg)
            remeber.close()

        elif 'new task' in query:
            query = query.replace("new task","")
            query = query.replace("jarvis","")
            query = query.strip()
            if query != "":
                self.Speak("Adding task : "+ query)
                with open(self.todo_file, "a") as file:
                    file.write(query + "\n")

        elif 'speak task' in query:
            with open(self.todo_file, "r") as file:
                self.Speak("Work we have today is :\n" + file.read())

        elif 'today work' in query:
            with open(self.todo_file, "r") as file:
                tasks = file.read()
            notification.notify(
                title = "Today's Work",
                message = tasks
            )

        elif query in ['java road map','python road map','computer science road map','c plus plus road map','data analyst road map','data structures and algorithms road map','devops road map','frontend road map','full stack road map','git road map','github road map','javascript road map','kubernets road map','mongodb road map','nodejs road map','react road map','reactjs road map','sql road map','powerbi road map']:
            self.Speak("Ok Sir, Wait a second")
            if 'java' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\new jarvis one\\java.pdf")
            elif 'python' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\python.pdf")
            elif 'computer science' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\computer science.pdf")
            elif 'c plus plus' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\cpp.pdf")
            elif 'data analyst' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\data analyst.pdf")
            elif 'data structures and algorithms' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\data structures and algorithms.pdf")
            elif 'devops' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\devops.pdf")
            elif 'frontend' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\frontend.pdf")
            elif 'full stack' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\full stack.pdf")
            elif 'git' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\git github.pdf")
            elif 'github' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\git github.pdf")
            elif 'javascript' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\javascript.pdf")
            elif 'kubernetes' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\kubernetes.pdf")
            elif 'mongodb' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\mongodb.pdf")
            elif 'nodejs' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\nodejs.pdf")
            elif 'react' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\react.pdf")
            elif 'reactjs' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\react.pdf")
            elif 'sql' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\sql.pdf")
            elif 'powerbi' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Roadmaps\\powerbi.pdf")
                 
            
            self.Speak("Your command has been completed sir!")
        
        elif query in ['first year syllabus','second year syllabus','third year syllabus','last year syllabus','fourth year syllabus','final year syllabus','fe syllabus','se syllabus','te syllabus','be syllabus','3rd year syllabus','4th year syllabus']:
            self.Speak("Ok Sir, Wait a second")
            if 'first year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\FE Syllabus.pdf")
            elif 'second year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\SE Syllabus.pdf") 
            elif 'third year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\TE Syllabus.pdf") 
            elif '3rd year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\TE Syllabus.pdf")
            elif 'final year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\BE Syllabus.pdf")
            elif '4th year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\BE Syllabus.pdf")
            elif 'last year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\BE Syllabus.pdf")
            elif 'fourth year' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\BE Syllabus.pdf")
            elif 'fe syllabus' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\FE Syllabus.pdf")
            elif 'se syllabus' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\SE Syllabus.pdf")
            elif 'te syllabus' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\TE Syllabus.pdf")
            elif 'be syllabus' in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Syllabus\\BE Syllabus.pdf")
        
        elif query in ['abhijit salunkhe','dhanashri gore','deepali gupta','aiml hod','kolhe','Madhuri pujari','mitesh sarjare','nita dimble','rucha bhuvad','sadhana shelar','sheetal patil','sonali singh','who is abhijit salunkhe','who is dhanashri gore','who is deepali gupta','who is aiml hod','who is kolhe','who is madhuri pujari','who is mitesh sarjare','who is nita dimble','who is rucha bhuvad','who is sadhana shelar','who is sheetal patil','who is sonali singh']:
            self.Speak("Ok Sir, Wait a second")
            if "abhijit salunkhe" in query or "who is abhijit salunkhe" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Abhijit Salunkhe.pdf")
            elif "dhanashri gore" in query or "who is dhanashri gore" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Dhanashri Gore.pdf")
            elif "deepali gupta" in query or "who is deepali gupta" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Dipali Gupta.pdf")
            elif "aiml hod" in query or "who is aiml hod" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\HOD AIML.pdf")
            elif "kolhe" in query or "who is kolhe" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Kolhe.pdf")
            elif "madhuri pujari" in query or "who is madhuri pujari" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Madhuri pujari.pdf")
            elif "mitesh sarjare" in query or "who is mitesh sarjare" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Mitesh Sarjare.pdf")
            elif "nita dimble" in query or "who is nita dimble" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Nita Dimble.pdf")
            elif "rucha bhuvad" in query or "who is rucha bhuvad" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Rucha Bhuvad.pdf")
            elif "sadhana shelar" in query or "who is sadhana shelar" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Sadhana Shelar.pdf")
            elif "sheetal patil" in query or "who is sheetal patil" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Shital Patil.pdf")
            elif "sonali singh" in query or "who is sonali singh" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\Faculty Members\\Sonali Singh.pdf")

        elif query in ['give me academic information','show academic information','show me academic information','display academic information','department information','information of department']:
            self.Speak("Ok Sir, Wait a second")
            self.Speak("Scan this QR code and get information")
            if "give me academic information" in query or "show academic information" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\qr_drive_link.png")
            elif "show me academic information" in query or "display academic information" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\qr_drive_link.png")
            elif "department information" in query or "information of department" in query:
                if os.name == 'nt':
                    os.startfile("C:\\Users\\prath\\Desktop\\NewNOVA\\qr_drive_link.png")
            


        elif 'google search' in query:
            import wikipedia as googleScrap
            query = query.replace("jarvis","")
            query = query.replace("google search","")
            query = query.replace("google","")
            self.Speak("This is what i found on the Web!")
            pywhatkit.search(query)

            try:
                result = googleScrap.summary(query,2)
                self.Speak(result)
            except:
                self.Speak("NO Speakable Data Available!")

        elif 'temperature' in query:
            self.Temp()
        elif 'java road map' in query:
            query = query.replace("jarvis","")
            query = query.replace("give me","")
            query = query.replace("show me","")
            self.Speak("Ok Sir, Wait a second")

            if 'java' in query:
               if os.name == 'nt':
                os.startfile("C:\\Users\\prath\\Desktop\\new jarvis one\\java.pdf")
            else:
                print("Unsupported OS")

            self.Speak("Your command has been completed sir!")

        elif 'how to' in query:
            self.Speak("Getting Data From The Internet !")
            op = query.replace("jarvis", "")
            max_result = 1
            how_to_func = search_wikihow(op,max_result)
            assert len(how_to_func) == 1
            how_to_func[0].print()
            self.Speak(how_to_func[0].summary)

        elif 'open' in query:
            query = query.replace("open","")
            pyautogui.press("super")
            pyautogui.typewrite(query)
            pyautogui.sleep(2)
            pyautogui.press("enter")

        elif 'ask ai' in query:
            self.jarvis_chat = []
            query = query.replace("jarvis","")
            query = query.replace("ask ai","")

            response = ai.send_request(self.jarvis_chat)
            self.Speak(response)

        elif 'clear chat' in query:
            self.jarvis_chat = []
            self.Speak("Chat Cleared")

        else:
            query = query.replace("jarvis","")
            self.jarvis_chat.append({"role": "user","content":query})
            response = ai.send_request(self.jarvis_chat)
            self.jarvis_chat.append({"role": "assistant","content":response})
            self.Speak(response)

def main():
    try:
        root = tk.Tk()
        app = VoiceAssistantApp(root)
        
        # Handle window close
        def on_closing():
            if hasattr(app, 'Assistant') and app.Assistant:
                app.Assistant.stop()
            root.destroy()
            sys.exit()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()