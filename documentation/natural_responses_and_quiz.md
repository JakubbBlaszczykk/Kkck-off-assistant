# Natural Responses And Quiz Update

## Goal

The professor's feedback was to make Raza's output sound less mechanical and to add quiz content for a demo. This update addresses both points:

- Raza now has multiple templates for common response types.
- Quiz mode has 50 simple dataset-based questions.
- Quiz sessions use seven questions and count the user's score.
- Spoken answers are handled through text normalization and fuzzy matching, not a separate keyword-spotting model.

## Naturalized Responses

Natural response templates live in:

```text
kickoff_assistant/responses.py
```

The module contains several variants for:

- greeting the user,
- explaining what Raza can do,
- player information,
- player position,
- player nationality,
- player stats,
- team squads,
- not-found messages,
- out-of-scope messages.

The same response layer is reused by:

- Rasa custom actions in `actions/actions.py`,
- the local text mode in `kickoff_assistant/text_cli.py`,
- the web demo in `kickoff_assistant/web_app.py`.

This keeps the speaking style consistent across interfaces.

## Rasa Domain Templates

`domain.yml` was also updated with several variants for:

- `utter_greet`,
- `utter_goodbye`,
- `utter_thanks`,
- `utter_out_of_scope`,
- `utter_ask_rephrase`.

That means Rasa can vary simple built-in responses without calling a custom action.

## Quiz Question Bank

The quiz questions are stored in:

```text
data/quiz_questions.json
```

The file contains 50 simple questions based on `data/processed/players.json` and `data/processed/teams.json`.

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
Raza: Hi, I'm Raza. We can talk football, or I can run a short quiz...

User: Let's do a quiz
Raza: Question 1 of 7: ...

User: Arsenal
Raza: Correct. Question 2 of 7: ...
```

The user can also ask dataset questions such as:

```text
Tell me about Erling Haaland
Who plays for Arsenal?
How many goals did Mohamed Salah score?
What position is Pedri?
```
