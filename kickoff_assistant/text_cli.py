from __future__ import annotations

import sys
from typing import Optional

from kickoff_assistant.knowledge_base import KnowledgeBase


HELP_TEXT = (
    "Ask about a player, a team squad, position, nationality, or stats. "
    "Examples: 'Tell me about Haaland', 'Who plays for Arsenal?', "
    "'What position is Pedri?', 'Where is Lewandowski from?'."
)

GREETINGS = {"hi", "hello", "hey", "good morning", "good evening"}
CLOSINGS = {"quit", "exit", "bye", "goodbye", "thanks", "thank you", "thx"}


def player_answer(message: str, kb: KnowledgeBase, player: dict[str, object]) -> str:
    text = message.casefold().strip()
    if any(phrase in text for phrase in ["which team", "what team", "team of", "club", "where"]) and "from" not in text:
        return kb.player_teams(player)
    if any(word in text for word in ["position", "where does", "role"]):
        return f"{player['name']} plays as: {player['position']}."
    if any(word in text for word in ["nationality", "from", "country"]):
        return f"{player['name']} represents {player['nationality']}."
    if any(word in text for word in ["goals", "assists", "stats", "numbers", "scored"]):
        return (
            f"{player['name']} recorded {player['goals']} goals and "
            f"{player['assists']} assists in {player['matches']} matches."
        )
    if "asked" in text or "sorry" in text or "not" in text:
        return f"Sorry, you're right. {kb.player_info(player)}"
    return kb.player_info(player)


def answer(message: str, kb: KnowledgeBase) -> str:
    text = message.casefold().strip()
    if not text:
        return "Type a football question or 'help'."
    if text in {"help", "commands"}:
        return HELP_TEXT
    if text in GREETINGS:
        return "Hey! Ask me about players or squads from the 2024/25 Top 5 leagues dataset."
    if text in {"thanks", "thank you", "thx"}:
        return "You're welcome. See you!"

    if "top scorer" in text or "top scorers" in text or "most goals" in text:
        return kb.top_scorers(kb.find_league(message))

    if any(word in text for word in ["won", "winner", "champion", "title"]):
        return (
            "I do not have league winners in this player dataset yet. "
            "For now I can answer player, team squad, position, nationality, and stats questions."
        )

    if any(phrase in text for phrase in ["clubs played", "teams played", "clubs in", "teams in"]):
        league = kb.find_league(message)
        if league:
            return kb.teams_in_league(league)

    if "players" in text and ("from" in text or "nationality" in text or "polish" in text):
        nationality = kb.find_nationality(message)
        if nationality:
            return kb.players_by_nationality(nationality)

    if text.startswith("who is from") or text.startswith("who comes from"):
        nationality = kb.find_nationality(message)
        if nationality:
            return kb.players_by_nationality(nationality)

    if any(
        phrase in text
        for phrase in [
            "squad",
            "all",
            "list",
            "plays for",
            "playing for",
            "players in",
            "players for",
            "who plays",
            "who is playing",
        ]
    ):
        team = kb.find_team(message)
        if team:
            return kb.team_squad(team, limit=50 if "all" in text else 15)
        return "I could not find that team in the processed dataset."

    team = kb.find_team(message)
    if team and any(phrase in text for phrase in ["what is", "tell me about", "something about"]):
        return kb.team_squad(team)

    player = kb.find_player(message)
    if player:
        return player_answer(message, kb, player)

    return "I can only answer football dataset questions for now. Try a player or team name."


def ambiguity_prompt(candidates: list[dict[str, object]]) -> str:
    names = "; ".join(
        f"{index}. {player['name']} ({player['team']})"
        for index, player in enumerate(candidates, start=1)
    )
    return f"Which player do you mean? {names}."


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    kb = KnowledgeBase.load()
    greeted = False
    pending_disambiguation: Optional[dict[str, object]] = None
    print("KickOff Assistant text mode. Start with 'hello'. Type 'help' for examples, 'bye' to exit.")

    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: See you!")
            break

        text = message.casefold()
        if text in CLOSINGS:
            if text in {"thanks", "thank you", "thx"}:
                print("Bot: You're welcome. See you!")
            else:
                print("Bot: See you!")
            break

        if not greeted:
            if text in GREETINGS:
                greeted = True
            else:
                print("Bot: Say 'hello' first, then ask me about a player or team.")
                continue

        if text in GREETINGS and greeted:
            print("Bot: Hey! Ask me about players or squads from the 2024/25 Top 5 leagues dataset.")
            continue

        if text in {"quit", "exit", "bye", "goodbye"}:
            print("Bot: See you!")
            break

        if pending_disambiguation:
            candidates = pending_disambiguation["candidates"]
            original_message = str(pending_disambiguation["message"])
            player = kb.find_player_by_choice(message, candidates)
            if player:
                print(f"Bot: {player_answer(original_message, kb, player)}")
                pending_disambiguation = None
                continue

            print("Bot: Please choose one of the listed players by first name or number.")
            continue

        candidates = kb.ambiguous_player_candidates(message)
        if candidates:
            pending_disambiguation = {"message": message, "candidates": candidates}
            print(f"Bot: {ambiguity_prompt(candidates)}")
            continue

        print(f"Bot: {answer(message, kb)}")


if __name__ == "__main__":
    main()
