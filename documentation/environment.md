# Environment Setup

Rasa 3.6 is intended to run with Python 3.9 for this project.

## Create Virtual Environment

```bash
C:\Users\jakub\AppData\Local\Programs\Python\Python39\python.exe -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Verify

```bash
python --version
rasa --version
python scripts/preprocess_data.py
python -m kickoff_assistant.text_cli
```
