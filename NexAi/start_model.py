import platform
import subprocess
import time
import shutil
import os
import ollama
import pathlib

MODEL_NAME = "NexAi:latest"
MODEL_FILE_PATH = BASE_DIR = pathlib.Path(__file__).resolve().parent
model_file = BASE_DIR / "MODELFILE"


if platform.system() == "Linux":

    # Check ollama installed
    if shutil.which("ollama") is None:
        print("Ollama is not installed. Please install it from https://ollama.com")
        exit()

    # Restart ollama
    subprocess.run("pkill -f ollama", shell=True)
    time.sleep(2)

    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(2)

    # Check if model exists
    model_list = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True
    ).stdout

    if MODEL_NAME not in model_list:

        if os.path.exists(MODEL_FILE_PATH):

            print(f"Model '{MODEL_NAME}' not found. Creating from MODELFILE...")

            subprocess.run([
                "ollama",
                "create",
                MODEL_NAME,
                "-f",
                MODEL_FILE_PATH
            ])

        else:
            print(f"ERROR: MODELFILE not found at {MODEL_FILE_PATH}")
            exit()

    # Run model in Ghostty
    subprocess.Popen([
        "ghostty",
        "-e",
        "bash",
        "-c",
        f"ollama run {MODEL_NAME}; exec bash"
    ])

    print(f"{MODEL_NAME} running in terminal.")

else:
    print("This script only supports Linux.")