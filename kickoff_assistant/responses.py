from __future__ import annotations

import random
from typing import Any, Iterable


def pick(options: Iterable[str]) -> str:
    return random.choice(list(options))


def intro() -> str:
    return pick(
        [
            "Hi, I'm Raza. You can ask me a football question, or you can play a football quiz.",
            "Hey, I'm Raza. Ask me about football data, or you can play a football quiz.",
            "Hi there, I'm Raza. I can answer football questions from the 2024/25 dataset, or you can play a football quiz.",
            "Hello, I'm Raza. We can explore player data, or you can play a quick football quiz.",
        ]
    )


def help_prompt() -> str:
    return pick(
        [
            "You can ask about a player, a squad, a position, nationality, or stats. For example: tell me about Haaland.",
            "Try a player or team question. I can handle things like Saka's stats, Arsenal's squad, or Lewandowski's nationality.",
            "Ask me about football data from the 2024/25 Top 5 leagues, or say quiz if you want a quick challenge.",
        ]
    )


def not_found(kind: str) -> str:
    return pick(
        [
            f"I could not find that {kind} in the processed dataset. Could you try the full name?",
            f"I don't see that {kind} in my 2024/25 data. A more specific name might help.",
            f"That {kind} is not coming up in the dataset I have here.",
        ]
    )


def out_of_scope() -> str:
    return pick(
        [
            "I can stay useful on football questions for now. Try a player, team, league, or say quiz.",
            "That is outside my football dataset, but I can answer player and squad questions.",
            "I don't have that topic covered yet. Football data and the quiz are my strong areas.",
        ]
    )


def player_info(player: dict[str, Any]) -> str:
    return pick(
        [
            (
                f"{player['name']} is listed as a {player['nationality']} {player['position']} "
                f"for {player['team']} in {player['league']}. In 2024/25, he had "
                f"{player['matches']} matches, {player['minutes']} minutes, "
                f"{player['goals']} goals, and {player['assists']} assists."
            ),
            (
                f"In this dataset, {player['name']} plays for {player['team']} in {player['league']}. "
                f"He is a {player['nationality']} {player['position']}, with {player['goals']} goals "
                f"and {player['assists']} assists across {player['matches']} matches."
            ),
            (
                f"{player['name']} is a {player['position']} from {player['nationality']}, playing for "
                f"{player['team']}. His 2024/25 line is {player['matches']} matches, "
                f"{player['minutes']} minutes, {player['goals']} goals, and {player['assists']} assists."
            ),
            (
                f"Sure. {player['name']} appears for {player['team']} in {player['league']}. "
                f"The dataset lists him as a {player['nationality']} {player['position']}: "
                f"{player['goals']} goals, {player['assists']} assists, {player['minutes']} minutes."
            ),
        ]
    )


def player_position(player: dict[str, Any]) -> str:
    return pick(
        [
            f"{player['name']} is listed as {player['position']}.",
            f"The dataset has {player['name']} down as {player['position']}.",
            f"{player['name']} plays in the {player['position']} role.",
        ]
    )


def player_nationality(player: dict[str, Any]) -> str:
    return pick(
        [
            f"{player['name']} represents {player['nationality']}.",
            f"The nationality listed for {player['name']} is {player['nationality']}.",
            f"{player['name']} is marked as {player['nationality']} in the dataset.",
        ]
    )


def player_stats(player: dict[str, Any]) -> str:
    return pick(
        [
            (
                f"{player['name']} recorded {player['goals']} goals, {player['assists']} assists, "
                f"and {player['minutes']} minutes in {player['matches']} matches."
            ),
            (
                f"For {player['name']}, I have {player['matches']} matches, {player['minutes']} minutes, "
                f"{player['goals']} goals, and {player['assists']} assists."
            ),
            (
                f"{player['name']}'s numbers are {player['goals']} goals and {player['assists']} assists "
                f"over {player['matches']} matches."
            ),
        ]
    )


def team_squad(team: dict[str, Any], shown: str, extra_count: int) -> str:
    suffix = f" and {extra_count} more" if extra_count > 0 else ""
    return pick(
        [
            f"{team['name']} play in {team['league']}. The squad includes {shown}{suffix}.",
            f"For {team['name']}, I can see players like {shown}{suffix}.",
            f"{team['name']}'s {team['league']} squad includes {shown}{suffix}.",
        ]
    )
