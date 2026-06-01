# KickOff Assistant Demo Webapp

## What Was Added

This update adds a browser demo for Kick-Off Assistant, a football knowledge companion. The demo is designed for a classroom presentation: the user starts by saying "Hi", then chooses between asking football questions about the Top 5 European Leagues (Season 2024/25) and playing a seven-question quiz.

The implementation is intentionally simple. It does not train a new keyword spotting model or add a CNN. Voice input uses the browser's Web Speech API when available, and voice output uses the browser's speech synthesis.

## Visual Design

The web demo uses a football stadium theme inspired by pixel-art aesthetics:

- **Dark blue stadium night-sky** background with floodlight gradient effects.
- **Pixel font** (`Press Start 2P`) for titles and labels, `Inter` for body text.
- **Three-column layout**: left coverage panel, central chat area, right info panel.
- **Left panel**: shows "Season 2024/25" badge and Top 5 Leagues with flag emojis (🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League, 🇪🇸 LaLiga, 🇮🇹 Serie A, 🇩🇪 Bundesliga, 🇫🇷 Ligue 1), plus mode/mic/voice status indicators.
- **Center chat area**: speech-bubble styled messages with soccer ball avatars, animated bubble entrance.
- **Right panel**: "What Can You Do?" section with ASK and QUIZ cards, quiz scoreboard with progress meter, and quick-action buttons.
- **Input bar**: football-themed with a soccer ball icon, microphone button, and glowing green SEND button.
- **Floating particle animations** for stadium atmosphere.
- Responsive design: collapses to single column on mobile.

## Files

- `kickoff_assistant/responses.py` — natural response templates with nationality-to-name and position-to-name mappings for human-readable output.
- `kickoff_assistant/quiz.py` — quiz loading, seven-question quiz sessions, answer normalization, aliases, and fuzzy matching.
- `kickoff_assistant/web_app.py` — a small HTTP server using only Python's standard library.
- `web/index.html` — the main demo UI with three-column layout.
- `web/styles.css` — football stadium theme styling with pixel-art aesthetics.
- `web/app.js` — chat behavior, microphone handling, speech synthesis, and score updates.
- `data/quiz_questions.json` — 50 simple questions generated from the Top 5 Leagues Season 2024/25 football data.

## Conversation Flow

1. The page initially shows a welcome message from Kick-Off Assistant.
2. The user says or types "Hi" to start.
3. Kick-Off Assistant replies with one of several natural greeting variants.
4. The user can choose:
   - a football question mode,
   - a quiz mode.
5. In football question mode, the existing knowledge base is reused. Responses use natural language with full nationality names (e.g. "Polish" instead of "POL") and full position names (e.g. "forward" instead of "FW").
6. In quiz mode, Kick-Off Assistant asks seven questions and tracks the score.
7. After the seventh question, the final score is given and the user can restart the quiz or ask a football question.

## Quiz Answer Matching

Quiz checking is handled in `kickoff_assistant/quiz.py`. The matcher:

- lowercases and removes punctuation,
- removes accents,
- converts simple number words such as "four" to `4`,
- accepts known aliases such as `PSG` for `Paris S-G`,
- accepts football role words such as "defender" for `DF`,
- uses a small fuzzy-match threshold for minor speech recognition mistakes.

This keeps the quiz tolerant enough for spoken answers without adding a separate speech model.

## Running The Demo

From the project root:

```bash
python -m kickoff_assistant.web_app
```

Then open:

```text
http://127.0.0.1:8080
```

If the local virtual environment is broken, recreate it first with a Python version compatible with the project. The web demo itself only needs the standard library plus the existing project files.

## Browser Notes

Speech recognition support depends on the browser. Chrome and Edge usually support `SpeechRecognition` / `webkitSpeechRecognition`. If the browser does not support it, the demo still works with typed input.

Speech output uses `speechSynthesis`, which is available in most modern browsers. The UI shows separate statuses for:

- microphone availability,
- voice output state,
- current mode,
- quiz score.

There is also a voice output toggle button. This is useful during testing because browser speech synthesis can be muted, blocked, or interrupted by the operating system audio output.

For the microphone to work reliably:

- open the app from `http://127.0.0.1:8080` or `http://localhost:8080`, not by double-clicking the HTML file,
- use Chrome or Edge for the demo,
- allow microphone permission when the browser asks,
- make sure the external microphone is selected as the system or browser input device,
- speak in English, because the recognition language is set to `en-US`.

If microphone access fails, the app now displays a short status such as `Permission`, `No mic`, `No speech`, or `Network`. Typed input remains available as a fallback.

The microphone button first checks raw browser microphone access with `navigator.mediaDevices.getUserMedia`. If that fails, the problem is permission, device selection, or operating system microphone access. If that succeeds but speech recognition still fails, the problem is usually the browser speech-recognition service.

Voice output only selects voices whose language starts with `en`. This prevents the browser from accidentally reading English text with a Polish voice. If no English voice is available, the app shows `No English` in the voice-output status and asks the user to enable or install an English system voice.

## Current Limitations

- Session state is stored in memory, so scores reset when the server restarts.
- The quiz currently samples seven questions from the local 50-question JSON file.
- The demo uses the processed dataset already present in `data/processed`.
- The UI is English-first for presentation purposes.
- The pixel font (`Press Start 2P`) is loaded from Google Fonts and requires an internet connection on first load.
