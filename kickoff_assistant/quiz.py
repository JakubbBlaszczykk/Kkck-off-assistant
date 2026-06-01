from __future__ import annotations

import json
import random
import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


DEFAULT_QUIZ_PATH = Path("data/quiz_questions.json")

NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "twenty one": "21",
    "twenty two": "22",
    "twenty three": "23",
    "twenty four": "24",
    "twenty five": "25",
    "thirty": "30",
}

ANSWER_ALIASES = {
    "df": {"defender", "defence", "defense", "centre back", "center back", "full back"},
    "mf": {"midfielder", "midfield"},
    "fw": {"forward", "striker", "winger", "attacker"},
    "gk": {"goalkeeper", "keeper"},
    "premier league": {"epl", "english premier league"},
    "la liga": {"laliga", "spanish league"},
    "serie a": {"italian league"},
    "ligue 1": {"french league"},
    "bundesliga": {"german league"},
    "nott ham forest": {"nottingham forest", "forest"},
    "paris s g": {"psg", "paris saint germain", "paris st germain"},
}


def normalize(value: str) -> str:
    without_accents = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = without_accents.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return NUMBER_WORDS.get(value, value)


def answer_variants(answer: str) -> set[str]:
    normalized = normalize(answer)
    variants = {normalized, normalized.replace(" ", "")}
    variants.update(ANSWER_ALIASES.get(normalized, set()))

    for token in re.split(r"[,/ ]+", normalized):
        if token in ANSWER_ALIASES:
            variants.update(ANSWER_ALIASES[token])
    return {normalize(item) for item in variants if item}


def is_correct(user_answer: str, accepted_answers: list[str]) -> bool:
    user = normalize(user_answer)
    if not user:
        return False

    all_answers = set()
    for answer in accepted_answers:
        all_answers.update(answer_variants(str(answer)))

    if user in all_answers or user.replace(" ", "") in all_answers:
        return True

    for answer in all_answers:
        if len(answer) >= 5 and (answer in user or user in answer):
            return True
        if len(answer) >= 5 and SequenceMatcher(None, user, answer).ratio() >= 0.84:
            return True
    return False


def load_questions(path: Path = DEFAULT_QUIZ_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


@dataclass
class QuizSession:
    questions: list[dict[str, Any]]
    total_questions: int = 7
    index: int = 0
    score: int = 0
    asked: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(cls, question_bank: list[dict[str, Any]], total_questions: int = 7) -> "QuizSession":
        selected = random.sample(question_bank, k=min(total_questions, len(question_bank)))
        return cls(questions=selected, total_questions=len(selected))

    def current_question(self) -> dict[str, Any]:
        return self.questions[self.index]

    def prompt(self) -> str:
        return f"Question {self.index + 1} of {self.total_questions}: {self.current_question()['question']}"

    def answer(self, user_answer: str) -> tuple[str, bool]:
        question = self.current_question()
        accepted = [question["answer"], *question.get("accepted_answers", [])]
        correct = is_correct(user_answer, [str(item) for item in accepted])
        if correct:
            self.score += 1
        self.asked.append(question)
        self.index += 1

        verdict = "Correct." if correct else f"Not quite. The answer was {question['answer']}."
        if self.finished:
            return (
                f"{verdict} Final score: {self.score}/{self.total_questions}. "
                f"Say quiz to play again, or ask me a football question.",
                correct,
            )
        return f"{verdict} {self.prompt()}", correct

    @property
    def finished(self) -> bool:
        return self.index >= self.total_questions
