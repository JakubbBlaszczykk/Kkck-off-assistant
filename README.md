# ⚽ KickOff Assistant - Voice-Enabled Football Dialog System

> A conversational AI assistant for football fans - ask about players, squads, careers, or test your knowledge with an interactive quiz. Fully voice-enabled with Speech-to-Text and Text-to-Speech.

---

## 📌 Project Overview

**KickOff Assistant** is a dialog system built with [Rasa Open Source](https://rasa.com/) that lets users interact naturally - by voice or text - with a football knowledge base covering the **Top 5 European Leagues** (Premier League, La Liga, Bundesliga, Serie A, Ligue 1).

Built as a practical assignment for the *Introduction to Speech and Natural Language Processing* course @ University of Aveiro (Erasmus), 2025/2026.

---

## 🎯 Features

| Mode | Description |
|------|-------------|
| 🗣️ **Info Mode** | Ask about players, squads, careers, nationalities, positions |
| 🧠 **Quiz Mode** | Interactive football trivia - bot asks questions, scores your answers |
| 🎙️ **Voice I/O** | Speech-to-Text input + Text-to-Speech output |

### Example interactions

```
User: "Tell me about Vinicius Junior"
Bot:  "Vinicius Junior is a Brazilian winger playing for Real Madrid..."

User: "Who plays for Arsenal?"
Bot:  "Arsenal's squad includes Saka, Odegaard, Havertz..."

User: "Let's do a quiz"
Bot:  "Great! Question 1: Which club did Erling Haaland join in 2022?"
```

---

## 🏗️ Architecture

```
Voice Input (mic)
      │
      ▼
 STT (speech_recognition / Whisper)
      │
      ▼
 Rasa NLU  ──►  Intent + Entity Detection
      │
      ▼
 Dialog Manager  ──►  Stories / Rules
      │
      ▼
 Custom Actions  ──►  players.json / teams.json / quiz_questions.json
      │
      ▼
 Response Text
      │
      ▼
 TTS (pyttsx3 / gTTS)
      │
      ▼
 Voice Output
```

---

## 🧠 NLU - Intents & Entities

### Intents

| Intent | Example utterances |
|--------|-------------------|
| `greet` | *"Hi"*, *"Hello"*, *"Hey there"* |
| `goodbye` | *"Bye"*, *"See you"*, *"That's all"* |
| `ask_player_info` | *"Tell me about Mbappe"*, *"Who is Pedri?"* |
| `ask_team_squad` | *"Who plays for Bayern?"*, *"Show me Real Madrid's squad"* |
| `ask_player_career` | *"What clubs did Ronaldo play for?"*, *"Zidane's career"* |
| `ask_player_position` | *"What position does Salah play?"* |
| `ask_player_nationality` | *"Where is Lewandowski from?"* |
| `start_quiz` | *"Let's play a quiz"*, *"Test me"*, *"Quiz mode"* |
| `answer_quiz` | *"Barcelona"*, *"I think it's Juventus"* |
| `stop_quiz` | *"Stop the quiz"*, *"Quit"*, *"No more questions"* |
| `out_of_scope` | anything unrelated to football |

### Entities

- `player_name` - e.g. *Haaland*, *Mbappe*, *Bellingham*
- `team_name` - e.g. *Arsenal*, *Barcelona*, *PSG*

---

## 📁 Project Structure

```
kickoff-assistant/
│
├── data/
│   ├── nlu.yml                  # Training examples for NLU
│   ├── stories.yml              # Conversation flows
│   ├── rules.yml                # Rule-based responses
│   ├── players.json             # Football player knowledge base
│   ├── teams.json               # Team squads & info
│   └── quiz_questions.json      # Quiz question bank
│
├── actions/
│   └── actions.py               # Custom Rasa actions
│
├── models/                      # Trained Rasa models (auto-generated)
│
├── tests/
│   └── test_stories.yml         # End-to-end conversation tests
│
├── voice_interface.py           # STT + TTS wrapper script
├── domain.yml                   # Rasa domain config
├── config.yml                   # Rasa NLU pipeline config
├── credentials.yml              # Rasa channel credentials
├── endpoints.yml                # Action server endpoint
└── requirements.txt             # Python dependencies
```

---

## 📦 Dataset

Player and team data sourced from:

**[Football Players Stats 2024-2025 — Kaggle](https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2024-2025)**
> Player statistics from the 2024-2025 season across the Big 5 European Leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1).

Quiz questions sourced from:

**[Open Trivia Database](https://opentdb.com/api.php?amount=50&category=21&type=multiple)**
> Free, community-maintained trivia API. Category 21 = Sports.

> ⚠️ The raw dataset is pre-processed into `data/players.json` and `data/teams.json` - only relevant fields (name, club, nationality, position, age) are kept to keep the system lightweight.

---

## 🛠️ Installation

> ⚠️ Rasa requires **Python 3.9**. It does not work reliably on 3.10+.

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/kickoff-assistant.git
cd kickoff-assistant

# 2. Create virtual environment with Python 3.9
python3.9 -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the Rasa model
rasa train

# 5. Start the action server (in a separate terminal)
rasa run actions

# 6. Run in text mode
rasa shell

# 7. Run in voice mode
python voice_interface.py
```

---

## 🎙️ Voice Interface

The `voice_interface.py` script connects everything:

- **STT**: `speech_recognition` library with Google Speech API (free, no key needed for basic use)
- **TTS**: `pyttsx3` (offline) or `gTTS` (Google, requires internet)
- **Communication**: sends recognized text to Rasa REST API at `localhost:5005`

To run with voice:
```bash
# Terminal 1 — Rasa server
rasa run --enable-api --cors "*"

# Terminal 2 — Action server
rasa run actions

# Terminal 3 — Voice interface
python voice_interface.py
```

---

## 📋 Requirements

```
rasa==3.6.x
SpeechRecognition
pyttsx3
gTTS
pyaudio
requests
```

Full list in `requirements.txt`.

---

## 🗺️ Dialog Flows

### Info Flow
```
greet → ask_player_info → [ActionPlayerInfo] → response → (follow-up or goodbye)
greet → ask_team_squad  → [ActionTeamSquad]  → response → (follow-up or goodbye)
```

### Quiz Flow
```
start_quiz → [ActionStartQuiz] → question
           → answer_quiz       → [ActionCheckAnswer] → correct/wrong + next question
           → stop_quiz         → [ActionQuizScore]   → final score + goodbye
```

---

## 👤 Author

**Jakub Błaszczyk**
Erasmus Student @ University of Aveiro - DETI
Home university: Lodz University of Technology
Course: Introduction to Speech and Natural Language Processing, 2025/2026
Supervisor: Prof. António Teixeira

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

Dataset credits to respective Kaggle authors and Open Trivia DB contributors.
