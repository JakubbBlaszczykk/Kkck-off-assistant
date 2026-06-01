from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from kickoff_assistant import responses
from kickoff_assistant.knowledge_base import KnowledgeBase
from kickoff_assistant.quiz import QuizSession, load_questions
from kickoff_assistant.text_cli import answer


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
HOST = "127.0.0.1"
PORT = 8080


class DemoState:
    def __init__(self) -> None:
        self.kb = KnowledgeBase.load(ROOT / "data" / "processed")
        self.quiz_questions = load_questions(ROOT / "data" / "quiz_questions.json")
        self.sessions: dict[str, dict[str, Any]] = {}

    def session(self, session_id: str) -> dict[str, Any]:
        return self.sessions.setdefault(session_id, {"mode": "home", "quiz": None, "score": 0})

    def handle(self, session_id: str, message: str) -> dict[str, Any]:
        session = self.session(session_id)
        text = message.casefold().strip()

        if not text:
            return self.payload(responses.help_prompt(), session)

        if text in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}:
            session["mode"] = "home"
            session["quiz"] = None
            return self.payload(responses.intro(), session)

        if "quiz" in text or "test me" in text:
            quiz = QuizSession.create(self.quiz_questions)
            session["mode"] = "quiz"
            session["quiz"] = quiz
            return self.payload(f"Great, let's play seven questions. {quiz.prompt()}", session)

        if any(phrase in text for phrase in ["ask", "question", "football", "data", "players", "squads"]):
            if session["mode"] == "home":
                session["mode"] = "qa"
                return self.payload("Perfect. Ask me about a player, a club, stats, or a squad.", session)

        quiz = session.get("quiz")
        if isinstance(quiz, QuizSession):
            reply, correct = quiz.answer(message)
            session["score"] = quiz.score
            if quiz.finished:
                session["mode"] = "home"
                session["quiz"] = None
            return self.payload(reply, session, correct=correct)

        session["mode"] = "qa"
        return self.payload(answer(message, self.kb), session)

    def payload(self, reply: str, session: dict[str, Any], correct: bool | None = None) -> dict[str, Any]:
        quiz = session.get("quiz")
        quiz_index = quiz.index if isinstance(quiz, QuizSession) else 0
        quiz_total = quiz.total_questions if isinstance(quiz, QuizSession) else 7
        score = quiz.score if isinstance(quiz, QuizSession) else session.get("score", 0)
        return {
            "reply": reply,
            "mode": session["mode"],
            "score": score,
            "quizIndex": quiz_index,
            "quizTotal": quiz_total,
            "correct": correct,
        }


STATE = DemoState()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/message":
            self.send_error(404)
            return

        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length)
        try:
            request = json.loads(body.decode("utf-8"))
            session_id = str(request.get("sessionId", "default"))
            message = str(request.get("message", ""))
            response = STATE.handle(session_id, message)
        except Exception as exc:
            self.send_error(500, str(exc))
            return

        payload = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Kick-Off Assistant demo running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
