#NexAi 🚀

Welcome! This repo helps you build the `NexAi` Ollama model from the `MODELFILE`. Below you'll find quick, Arch Linux + ghostty terminal instructions so you can get started fast. ✨

**Prerequisites**
- Python 3.8+ installed on your Arch Linux system or VS Code with Python plugin.
- Ollama installed and available on your PC
- You must run commands in the `ghostty` terminal (the project currently only supports Arch Linux + ghostty)

**Create and activate a Python virtual environment** 🐍

#Open your `ghostty` terminal and run:

```bash
# open ghostty and navigate to the project directory
open the project directory in ghostty (navigate to where you cloned this repo)

```
```bash
# create a python virtual environment
python -m venv venv

```
```bash

# activate the virtual environment (you should see (venv) in your terminal prompt)
source venv/bin/activate

```
```bash

# confirm activation (you should see (venv) in your terminal prompt)
ls #- to confirm you're in the project directory and the venv is active)
```

After the venv is active, install Python dependencies:

```bash
pip install -r requirements.txt
```

**Ollama** 🐘

You need Ollama installed on your machine. On Arch Linux, follow the Ollama documentation or use an AUR helper if a community package exists. Make sure Ollama is installed!

**Running the model builder** ⚙️

- `start_model.py` will build the `NexAi` Ollama model from the `MODELFILE` when run.
- Important: `start_model.py` currently only works on Arch Linux when run inside the `ghostty` terminal.

```bash
**Customize your own AI model** 🛠️

- Want your own model? Edit the `MODELFILE` to change model contents and behavior. `start_model.py` uses that file to construct the model.

**Files of interest**
- `MODELFILE` — edit to change model definition
- `start_model.py` — builds the NexAi Ollama model from `MODELFILE`
- `requirements.txt` — Python dependencies

