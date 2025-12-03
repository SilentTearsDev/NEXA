import os
import time


apps = {  ## nem megy!!
    "np": r"C:\Windows\notepad.exe",
    "opera": r"C:\Users\YourUser\AppData\Local\Programs\Opera GX\launcher.exe",
    "dc": r"C:\Users\YourUser\AppData\Local\Discord\Update.exe",
}


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

    if lower in ["hi", "hello", "hey"]:
        print(f"{NEXA_NAME}: Hello! How can I help you?")

    elif lower == "/r":
        print(f"{NEXA_NAME}: What do you want to run? Use /r <shortcut>.")

    elif lower == "help":
        print(f"{NEXA_NAME}: Commands:")
        print("  /r <shortcut> - Run an app (example: /r np)")
        print("  /exit or /q - Stop the chat bot")

    elif lower == "/ls":
        print(f"{NEXA_NAME}: Available shortcuts:")
        for shortcut in apps.keys():
            print(f"  {shortcut}")

    elif lower == "how are you?":
        print(f"{NEXA_NAME}: I'm just a program, but thanks for asking!")

    elif lower == "what is your name?":
        print(f"{NEXA_NAME}: I'm Nexa, your friendly chat bot!")

    elif lower == "tell me a joke":
        print(f"{NEXA_NAME}: Why did the scarecrow win an award? Because he was outstanding in his field!")

    else:
        print(f"{NEXA_NAME}:{RED} Sorry, I don't understand that.\033[0m")