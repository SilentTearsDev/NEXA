# 🚀 NexAi

> Build and customize your own Ollama AI model locally using `MODELFILE`.

NexAi is a lightweight AI model builder designed for:

* Arch Linux
* Ghostty terminal
* Python virtual environments
* Ollama

---

# Features

* Build custom Ollama AI models
* Simple Python setup
* Editable AI behavior
* Lightweight local workflow
* Easy project structure

---

# Requirements

Before starting, install:

* Python 3.8+
* Ollama
* Ghostty terminal

Optional but recommended:

* VS Code
* Git

---

# Setup

## Open Ghostty

Open the project folder inside Ghostty:

```bash
cd path/to/NexAi
```

---

## Create Python Virtual Environment

```bash
python -m venv venv
```

---

## Activate Virtual Environment

```bash
source venv/bin/activate
```

If successful, your terminal should display:

```bash
(venv)
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Install Ollama

Official website:

[https://ollama.com](https://ollama.com)

Verify installation:

```bash
ollama --version
```

---

# Build The NexAi Model

Run:

```bash
python start_model.py
```

The script will:

* Read the `MODELFILE`
* Build the AI model
* Register it inside Ollama

---

# Customize The AI

Edit:

```bash
MODELFILE
```

You can customize:

* Personality
* System prompts
* Parameters
* Instructions
* Model configuration

---

# Project Structure

```bash
NexAi/
├── MODELFILE
├── start_model.py
├── requirements.txt
└── venv/
```

---

# Important Notes

Currently supported only on:

* Arch Linux
* Ghostty terminal

Not supported:

* ❌ Windows
* ❌ macOS

---

# Troubleshooting

## Virtual Environment Does Not Activate

Correct:

```bash
source venv/bin/activate
```

Wrong:

```bash
python venv/bin/activate
```

---

## Ollama Command Not Found

Check installation:

```bash
ollama --version
```

If it fails:

* reinstall Ollama
* restart Ghostty
* verify PATH configuration

---

# Tips

* Always activate `venv`
* Keep `MODELFILE` organized
* Use VS Code for editing
* Restart terminal after installing Ollama

---

# 🔥 NexAi

Build. Modify. Experiment. Create your own AI locally.
