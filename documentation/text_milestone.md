# Text-only Milestone

This milestone builds a working text assistant before adding speech input and speech output.

## Scope

- Process the selected football CSV into lightweight JSON files.
- Run a local command-line assistant for quick testing.
- Provide a Rasa text-mode project scaffold with custom actions.
- Keep speech-to-text and text-to-speech for the next milestone.

## Data Processing

The raw CSV should live in:

```bash
data/raw/players_data-2024_2025.csv
```

Process it into assistant-ready JSON files:

```bash
python scripts/preprocess_data.py
```

Generated files:

```bash
data/processed/players.json
data/processed/teams.json
```

The generated files are derived from the selected CSV and are ignored by git.

## Local Text CLI

Run:

```bash
python -m kickoff_assistant.text_cli
```

Example questions:

```text
hello
Tell me about Erling Haaland
Who plays for Arsenal?
List all Barcelona players
What position does Pedri play?
Where is Robert Lewandowski from?
How many goals did Mohamed Salah score?
Who was top scorer in 2024/25?
Who was top scorer in La Liga 2024/25?
Tell me which clubs played in Premier League in season 2024/25
List me Polish players
thanks
```

The CLI expects the user to start with a greeting such as `hello` and finish with `thanks` or `bye`.

If a surname matches multiple players, the assistant asks for clarification:

```text
You: Where Mbappe plays?
Bot: Which player do you mean? 1. Kylian Mbappé (Real Madrid); 2. Ethan Mbappé (Lille).
You: Kylian
Bot: Kylian Mbappé plays for Real Madrid in La Liga.
```

## Rasa Text Mode

Train and run Rasa:

```bash
rasa train
rasa run actions
rasa shell
```

The custom Rasa actions read from `data/processed`, so run the preprocessing step first.
