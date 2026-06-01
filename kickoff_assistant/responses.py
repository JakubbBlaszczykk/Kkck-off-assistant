from __future__ import annotations

import random
from typing import Any, Iterable


NATIONALITY_NAMES = {
    "ALB": "Albanian", "ALG": "Algerian", "ANG": "Angolan", "ARG": "Argentinian",
    "ARM": "Armenian", "AUS": "Australian", "AUT": "Austrian", "BEL": "Belgian",
    "BEN": "Beninese", "BIH": "Bosnian", "BRA": "Brazilian", "BUL": "Bulgarian",
    "BUR": "Burkinabè", "CAM": "Cameroonian", "CAN": "Canadian", "CGO": "Congolese",
    "CHI": "Chilean", "CIV": "Ivorian", "COD": "Congolese", "COL": "Colombian",
    "COM": "Comorian", "CRC": "Costa Rican", "CRO": "Croatian", "CZE": "Czech",
    "DEN": "Danish", "ECU": "Ecuadorian", "EGY": "Egyptian", "ENG": "English",
    "EQG": "Equatoguinean", "ESP": "Spanish", "EST": "Estonian", "FIN": "Finnish",
    "FRA": "French", "GAB": "Gabonese", "GAM": "Gambian", "GEO": "Georgian",
    "GER": "German", "GHA": "Ghanaian", "GNB": "Bissau-Guinean", "GRE": "Greek",
    "GUI": "Guinean", "HON": "Honduran", "HUN": "Hungarian", "IRL": "Irish",
    "IRN": "Iranian", "ISL": "Icelandic", "ISR": "Israeli", "ITA": "Italian",
    "JAM": "Jamaican", "JPN": "Japanese", "KEN": "Kenyan", "KOR": "South Korean",
    "KOS": "Kosovar", "KVX": "Kosovar", "LUX": "Luxembourgish", "MAD": "Malagasy",
    "MAR": "Moroccan", "MEX": "Mexican", "MLI": "Malian", "MNE": "Montenegrin",
    "MOZ": "Mozambican", "NED": "Dutch", "NGA": "Nigerian", "NIR": "Northern Irish",
    "NOR": "Norwegian", "NZL": "New Zealander", "PAR": "Paraguayan", "PER": "Peruvian",
    "PHI": "Filipino", "POL": "Polish", "POR": "Portuguese", "ROU": "Romanian",
    "RSA": "South African", "RUS": "Russian", "SCO": "Scottish", "SEN": "Senegalese",
    "SLE": "Sierra Leonean", "SRB": "Serbian", "SUI": "Swiss", "SVK": "Slovak",
    "SVN": "Slovenian", "SWE": "Swedish", "TAN": "Tanzanian", "TGO": "Togolese",
    "TUN": "Tunisian", "TUR": "Turkish", "UKR": "Ukrainian", "URU": "Uruguayan",
    "USA": "American", "UZB": "Uzbekistani", "VEN": "Venezuelan", "WAL": "Welsh",
    "ZIM": "Zimbabwean",
}

POSITION_NAMES = {
    "GK": "goalkeeper",
    "DF": "defender",
    "MF": "midfielder",
    "FW": "forward",
    "DF,MF": "defender/midfielder",
    "MF,FW": "midfielder/forward",
    "FW,MF": "forward/midfielder",
    "DF,FW": "defender/forward",
    "MF,DF": "midfielder/defender",
    "FW,DF": "forward/defender",
}


def pick(options: Iterable[str]) -> str:
    return random.choice(list(options))


def natural_nationality(code: str) -> str:
    return NATIONALITY_NAMES.get(code.upper().strip(), code)


def natural_position(code: str) -> str:
    return POSITION_NAMES.get(code.strip(), code.lower())


def intro() -> str:
    return pick(
        [
            "Hi! I'm Kick-Off Assistant. You can ask me a football question, or you can play a football quiz.",
            "Hey! I'm Kick-Off Assistant. Ask me anything about the Top 5 Leagues from Season 2024/25, or play a quiz.",
            "Hi there! I'm Kick-Off Assistant. I can answer football questions from the Top 5 European Leagues, or you can play a football quiz.",
            "Hello! I'm Kick-Off Assistant. We can explore player and team data from the Top 5 Leagues, or you can play a quick football quiz.",
        ]
    )


def help_prompt() -> str:
    return pick(
        [
            "You can ask about a player, a squad, a position, nationality, or stats. For example: tell me about Haaland.",
            "Try a player or team question. I can handle things like Saka's stats, Arsenal's squad, or Lewandowski's nationality.",
            "Ask me about football data from the Top 5 European Leagues Season 2024/25, or say quiz if you want a quick challenge.",
        ]
    )


def not_found(kind: str) -> str:
    return pick(
        [
            f"I could not find that {kind} in the Top 5 Leagues 2024/25 season data. Could you try the full name?",
            f"I don't see that {kind} in my Top 5 Leagues data. A more specific name might help.",
            f"That {kind} is not coming up in the season data I have here.",
        ]
    )


def out_of_scope() -> str:
    return pick(
        [
            "I can stay useful on football questions for now. Try a player, team, league, or say quiz.",
            "That is outside my Top 5 Leagues data, but I can answer player and squad questions.",
            "I don't have that topic covered yet. Football data and the quiz are my strong areas.",
        ]
    )


def player_info(player: dict[str, Any]) -> str:
    name = player['name']
    nat = natural_nationality(str(player['nationality']))
    pos = natural_position(str(player['position']))
    team = player['team']
    league = player['league']
    matches = player['matches']
    minutes = f"{int(player['minutes']):,}"
    goals = player['goals']
    assists = player['assists']
    return pick(
        [
            (
                f"{name} is a {nat} {pos} playing for {team} in {league}. "
                f"In the 2024/25 season, he played {minutes} minutes across {matches} matches, "
                f"scoring {goals} goals with {assists} assists."
            ),
            (
                f"{name} plays for {team} in {league}. "
                f"He is a {nat} {pos} — in the 2024/25 season he appeared in {matches} matches, "
                f"playing {minutes} minutes, scoring {goals} goals and providing {assists} assists."
            ),
            (
                f"{name} is a {pos} from {nat.split()[-1] if ' ' in nat else nat} descent, playing for "
                f"{team}. His 2024/25 season line reads {matches} matches, "
                f"{minutes} minutes, {goals} goals, and {assists} assists."
            ),
            (
                f"Sure! {name} is a {nat} {pos} at {team} in {league}. "
                f"This season he has {goals} goals and {assists} assists across "
                f"{minutes} minutes in {matches} matches."
            ),
        ]
    )


def player_position(player: dict[str, Any]) -> str:
    pos = natural_position(str(player['position']))
    return pick(
        [
            f"{player['name']} plays as a {pos}.",
            f"{player['name']} is a {pos}.",
            f"{player['name']} plays in the {pos} role.",
        ]
    )


def player_nationality(player: dict[str, Any]) -> str:
    nat = natural_nationality(str(player['nationality']))
    return pick(
        [
            f"{player['name']} is {nat}.",
            f"{player['name']} represents {player['nationality']} — he is {nat}.",
            f"{player['name']} is a {nat} player.",
        ]
    )


def player_stats(player: dict[str, Any]) -> str:
    minutes = f"{int(player['minutes']):,}"
    return pick(
        [
            (
                f"In the 2024/25 season, {player['name']} scored {player['goals']} goals "
                f"and provided {player['assists']} assists across {minutes} minutes "
                f"in {player['matches']} matches."
            ),
            (
                f"{player['name']} played {minutes} minutes across {player['matches']} matches "
                f"this season, scoring {player['goals']} goals and adding {player['assists']} assists."
            ),
            (
                f"{player['name']}'s 2024/25 numbers: {player['goals']} goals and {player['assists']} assists "
                f"over {player['matches']} matches ({minutes} minutes)."
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
