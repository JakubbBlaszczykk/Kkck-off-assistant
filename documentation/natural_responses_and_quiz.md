# Natural Responses And Quiz Update

## Goal

The professor's feedback was to make the assistant's output sound less mechanical and to add quiz content for a demo. This update addresses both points:

- Kick-Off Assistant now has multiple templates for common response types.
- Player responses use natural language: full nationality names (e.g. "Polish" instead of "POL") and full position names (e.g. "forward" instead of "FW").
- Quiz mode has 50 simple questions about the Top 5 Leagues Season 2024/25.
- Quiz sessions use seven questions and count the user's score.
- Spoken answers are handled through text normalization and fuzzy matching, not a separate keyword-spotting model.

## Naturalized Responses

Natural response templates live in:

```text
kickoff_assistant/responses.py
```

The module contains:

### Nationality and Position Mappings

Two dictionaries convert raw data codes into human-readable text:

- `NATIONALITY_NAMES` — maps three-letter codes (e.g. `"POL"`, `"FRA"`, `"ENG"`) to adjective forms (e.g. `"Polish"`, `"French"`, `"English"`). Covers approximately 80 nationalities found in the Top 5 Leagues data.
- `POSITION_NAMES` — maps position codes (e.g. `"GK"`, `"DF"`, `"MF"`, `"FW"`) and combined codes (e.g. `"DF,MF"`) to natural labels (e.g. `"goalkeeper"`, `"defender/midfielder"`).

Helper functions `natural_nationality(code)` and `natural_position(code)` perform the lookup with a fallback to the raw code.

### Response Templates

Several response variants exist for:

- greeting the user (as "Kick-Off Assistant"),
- explaining what the assistant can do,
- player information (natural sentence format),
- player position (e.g. "plays as a forward"),
- player nationality (e.g. "is Polish"),
- player stats (with comma-formatted minutes),
- team squads,
- not-found messages (referencing Top 5 Leagues data),
- out-of-scope messages.

Example player info output:

```text
Lewandowski is a Polish forward playing for Barcelona in La Liga.
In the 2024/25 season, he played 3,385 minutes across 45 matches,
scoring 27 goals with 2 assists.
```

The same response layer is reused by:

- Rasa custom actions in `actions/actions.py`,
- the local text mode in `kickoff_assistant/text_cli.py`,
- the web demo in `kickoff_assistant/web_app.py`.

This keeps the speaking style consistent across interfaces.

## Rasa Domain Templates

`domain.yml` was also updated with several variants for:

- `utter_greet` (as Kick-Off Assistant, referencing Top 5 Leagues),
- `utter_goodbye`,
- `utter_thanks`,
- `utter_out_of_scope` (referencing Top 5 Leagues data),
- `utter_ask_rephrase`.

That means Rasa can vary simple built-in responses without calling a custom action.

## Quiz Question Bank

The quiz questions are stored in:

```text
data/quiz_questions.json
```

The file contains 50 simple questions based on `data/processed/players.json` and `data/processed/teams.json`. All questions reference "the Top 5 Leagues Season 2024/25".

Question categories include:

- player club,
- player goals,
- player assists,
- player position,
- player nationality,
- team league.

Each question has:

- `question`,
- `answer`,
- `accepted_answers`,
- `category`.

## Quiz Logic

Quiz logic lives in:

```text
kickoff_assistant/quiz.py
```

The main class is `QuizSession`. It:

- samples seven questions from the bank,
- asks one question at a time,
- checks the user's answer,
- increments the score when the answer is accepted,
- returns a final score after question seven.

The answer checker is intentionally lightweight and interpretable. It does not depend on a neural model.

## Demo Behavior

The intended demo path is:

```text
User: Hi
Kick-Off Assistant: Hi! I'm Kick-Off Assistant. Ask me anything about the Top 5 Leagues from Season 2024/25!

User: Tell me about Lewandowski
Kick-Off Assistant: Lewandowski is a Polish forward playing for Barcelona in La Liga.
In the 2024/25 season, he played 3,385 minutes across 45 matches,
scoring 27 goals with 2 assists.

User: Let's do a quiz
Kick-Off Assistant: Question 1 of 7: Which club does Mohamed Salah play for in the Top 5 Leagues Season 2024/25?

User: Liverpool
Kick-Off Assistant: Correct. Question 2 of 7: ...
```

The user can also ask dataset questions such as:

```text
Tell me about Erling Haaland
Who plays for Arsenal?
How many goals did Mohamed Salah score?
What position is Pedri?
Where is Robert Lewandowski from?
```
