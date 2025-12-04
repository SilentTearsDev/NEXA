import os
import time
import random
import datetime

apps = {  
    "np": r"C:\Windows\notepad.exe",
    "calc": r"C:\Windows\System32\calc.exe",
    "cmd": r"C:\Windows\System32\cmd.exe",
}

jokes = [
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "I would tell you a construction joke, but I'm still working on it.",
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What do you call fake spaghetti? An impasta!",
    "Why did the math book look sad? Because it had too many problems!",
    "Why can't your nose be 12 inches long? Because then it would be a foot!",
    "What do you call cheese that isn't yours? Nacho cheese!"
]
greeting_messages = [
    "Hello! How can I help you?",
    "Hi there! What can I do for you?",
    "Hey! Need any assistance?",
    "Greetings! How may I assist you?",
    "Hello! What would you like to do today?",
    "Hi! I'm here to help you with anything you need.",
    "Hey there! How can I make your day better?",
    "Greetings! What can I do for you today?"
]


BLUE = "\033[94m"
RED = "\033[91m"
YELLOW = "\033[93m"

NEXA_NAME = f"{BLUE}Nexa\033[0m"
USER_NAME = f"{YELLOW}User\033[0m"


print(f"{NEXA_NAME}: Hi! I'm Nexa, your chat bot. Type 'help' for commands.")

while True:
    input_text = input(f"{USER_NAME}: ").strip()
    
    
    if input_text.lower() in ["/exit", "quit", "bye", "/q"]:
        print(f"[{NEXA_NAME}]: Goodbye!")
        time.sleep(0.5)
        break

  
    if input_text == "":
        print(f"{NEXA_NAME}: You didn't type anything.")
        continue

   
    parts = input_text.split()

    if len(parts) >= 2:
        command = parts[0].lower()
        argument = parts[1].lower()

        # RUN parancs
        if command in ["/r", "/run"]:
            if argument in apps:
                print(f"{NEXA_NAME}:{YELLOW} Executing {argument} ...")
                os.startfile(apps[argument])

            else:
                print(f"{RED}[{NEXA_NAME}]{RED}: Unknown program shortcut.\033[0m")
            continue

    lower = input_text.lower()

    if lower in ["hi", "hello", "hey", "hi!", "hello!", "hey!", "hi there", "hello there", "hey there", "greetings", "greetings!", "greetings there"]:
        print(f"{NEXA_NAME}: {random.choice(greeting_messages)}")
        pass

    elif lower == "/r":
        print(f"{NEXA_NAME}: What do you want to run? Use /r <shortcut>.")

    elif lower in ["help", "/help"]:
        print(f"{NEXA_NAME}: Commands:")
        print("  /r <shortcut> - Run an app (example: /r np)")
        print("  /exit or /q - Stop the chat bot")

    elif lower == "/ls":
        print(f"{NEXA_NAME}: Available shortcuts:")
        for shortcut in apps.keys():
            print(f"  {shortcut}")

    elif lower in ["how are you?", "how are you", "how do you do?", "how's it going?", "how are you doing?", "how have you been?", "how's everything?", "how's life?", "how's your day?", "how's your day going?", "how's your day been?", "how are things?", "how are things going?", "how are things been?"]:
        print(f"{NEXA_NAME}: I'm just a program, but thanks for asking!")

    elif lower in ["what is your name?", "what's your name?", "who are you?", "who am i talking to?", "identify yourself", "name please", "your name", "tell me your name", "can you tell me your name?", "may i know your name?"]:
        print(f"{NEXA_NAME}: I'm Nexa, your friendly chat bot!")

    elif lower in ["tell me a joke", "tell a joke", "joke", "make me laugh", "i want to laugh", "say a joke", "jokes", "joke please", "joke pls", "joke now", "joke me", "joke time", "joke!", "joke.", "joke?", "joke now please", "joke now pls"]:
        print(f"{NEXA_NAME}: {random.choice(jokes)}")

    elif lower in ["what time is it?", "tell me the time", "current time", "time now", "time please", "time", "time", "what's the time?", "whats the time?"]:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{NEXA_NAME}: The current time is {current_time}.")
        
    elif lower in ["what is the date today?", "tell me the date", "current date", "date today", "date please", "date"]:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"{NEXA_NAME}: Today's date is {current_date}.")
        
    else:
        print(f"{NEXA_NAME}:{RED} Sorry, I don't understand that.\033[0m")