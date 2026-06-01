from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Optional

from kickoff_assistant import responses


DEFAULT_DATA_DIR = Path("data/processed")
STOPWORDS = {
    "a",
    "about",
    "asked",
    "but",
    "can",
    "country",
    "did",
    "do",
    "does",
    "for",
    "from",
    "goals",
    "hello",
    "how",
    "i",
    "info",
    "is",
    "many",
    "me",
    "nationality",
    "not",
    "of",
    "play",
    "playing",
    "plays",
    "player",
    "please",
    "position",
    "represents",
    "role",
    "score",
    "scored",
    "show",
    "sorry",
    "stats",
    "team",
    "tell",
    "the",
    "to",
    "what",
    "where",
    "who",
    "you",
}
NATIONALITY_ALIASES = {
    "poland": "POL",
    "polish": "POL",
    "polska": "POL",
    "france": "FRA",
    "french": "FRA",
    "england": "ENG",
    "english": "ENG",
    "spain": "ESP",
    "spanish": "ESP",
    "germany": "GER",
    "german": "GER",
    "italy": "ITA",
    "italian": "ITA",
    "brazil": "BRA",
    "brazilian": "BRA",
    "argentina": "ARG",
    "argentinian": "ARG",
    "portugal": "POR",
    "portuguese": "POR",
    "norway": "NOR",
    "norwegian": "NOR",
}
LEAGUE_ALIASES = {
    "premier league": "Premier League",
    "epl": "Premier League",
    "la liga": "La Liga",
    "laliga": "La Liga",
    "bundesliga": "Bundesliga",
    "serie a": "Serie A",
    "ligue 1": "Ligue 1",
}
TEAM_ALIASES = {
    "psg": "Paris S-G",
    "paris saint germain": "Paris S-G",
    "paris st germain": "Paris S-G",
    "man united": "Manchester Utd",
    "man utd": "Manchester Utd",
    "manchester united": "Manchester Utd",
    "nottingham forest": "Nott'ham Forest",
}


def normalize(value: str) -> str:
    without_accents = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9 ]+", " ", without_accents.casefold()).strip()


def compact(value: str) -> str:
    return normalize(value).replace(" ", "")


def query_terms(value: str) -> list[str]:
    tokens = normalize(value).split()
    if "not" in tokens:
        not_index = tokens.index("not")
        tokens = tokens[:not_index] or tokens
    return [token for token in tokens if token and token not in STOPWORDS]


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left, right).ratio()


@dataclass
class KnowledgeBase:
    players: list[dict[str, Any]]
    teams: list[dict[str, Any]]

    @classmethod
    def load(cls, data_dir: Path = DEFAULT_DATA_DIR) -> "KnowledgeBase":
        players_path = data_dir / "players.json"
        teams_path = data_dir / "teams.json"
        if not players_path.exists() or not teams_path.exists():
            raise FileNotFoundError(
                "Processed data not found. Run: python scripts/preprocess_data.py"
            )

        return cls(
            players=json.loads(players_path.read_text(encoding="utf-8")),
            teams=json.loads(teams_path.read_text(encoding="utf-8")),
        )

    def find_player(self, query: str) -> Optional[dict[str, Any]]:
        text = normalize(query)
        tight_text = compact(query)
        matches = []
        for player in self.players:
            name = str(player["name"])
            normalized_name = normalize(name)
            compact_name = compact(name)
            if normalized_name in text or (len(compact_name) >= 5 and compact_name in tight_text):
                matches.append(player)

        if matches:
            return sorted(
                matches,
                key=lambda item: (int(item.get("minutes", 0)), len(str(item["name"]))),
                reverse=True,
            )[0]

        tokens = query_terms(query)
        if not tokens:
            return None

        exact_token_candidates = [
            player
            for player in self.players
            if any(token in normalize(str(player["name"])).split() for token in tokens)
        ]
        if len(tokens) == 1 and exact_token_candidates:
            return sorted(
                exact_token_candidates,
                key=lambda item: int(item.get("minutes", 0)),
                reverse=True,
            )[0]

        best_player = None
        best_score = 0.0
        for player in self.players:
            name = normalize(str(player["name"]))
            name_tokens = name.split()
            exact_name_tokens = sum(1 for token in tokens if token in name_tokens and len(token) >= 5)
            token_scores = [
                max(similarity(token, name_token) for name_token in name_tokens)
                for token in tokens
            ]
            close_token_matches = sum(score >= 0.82 for score in token_scores)
            full_name_score = max(similarity(" ".join(tokens), name), similarity("".join(tokens), name.replace(" ", "")))
            score = (exact_name_tokens * 2.0) + close_token_matches + full_name_score
            if score > best_score:
                best_player = player
                best_score = score
            elif score == best_score and best_player is not None:
                if int(player.get("minutes", 0)) > int(best_player.get("minutes", 0)):
                    best_player = player
        return best_player if best_score >= 1.72 else None

    def find_team(self, query: str) -> Optional[dict[str, Any]]:
        text = normalize(query)
        tight_text = compact(query)
        for alias, team_name in TEAM_ALIASES.items():
            if alias in text or alias.replace(" ", "") in tight_text:
                for team in self.teams:
                    if team["name"] == team_name:
                        return team

        matches = []
        for team in self.teams:
            name = str(team["name"])
            normalized_name = normalize(name)
            compact_name = compact(name)
            if normalized_name in text or compact_name in tight_text:
                matches.append(team)

        if matches:
            return sorted(matches, key=lambda item: len(str(item["name"])), reverse=True)[0]
        return None

    def find_league(self, query: str) -> Optional[str]:
        text = normalize(query)
        compact_text = text.replace(" ", "")
        for alias, league in LEAGUE_ALIASES.items():
            if alias in text or alias.replace(" ", "") in compact_text:
                return league
        return None

    def find_nationality(self, query: str) -> Optional[str]:
        tokens = normalize(query).split()
        text = " ".join(tokens)
        for alias, code in NATIONALITY_ALIASES.items():
            if alias in tokens or alias in text:
                return code
        for player in self.players:
            nationality = normalize(str(player.get("nationality", "")))
            if nationality and nationality in tokens:
                return str(player["nationality"])
        return None

    def best_player_records(self) -> list[dict[str, Any]]:
        best_by_name: dict[str, dict[str, Any]] = {}
        for player in self.players:
            key = normalize(str(player["name"]))
            current = best_by_name.get(key)
            if current is None or int(player.get("minutes", 0)) > int(current.get("minutes", 0)):
                best_by_name[key] = player
        return list(best_by_name.values())

    def ambiguous_player_candidates(self, query: str) -> list[dict[str, Any]]:
        tokens = query_terms(query)
        if len(tokens) != 1:
            return []

        token = tokens[0]
        candidates = [
            player
            for player in self.best_player_records()
            if token in normalize(str(player["name"])).split()
        ]
        candidates.sort(key=lambda item: int(item.get("minutes", 0)), reverse=True)
        return candidates if len(candidates) > 1 else []

    def find_player_by_choice(self, query: str, candidates: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
        text = normalize(query)
        if text.isdigit():
            index = int(text) - 1
            if 0 <= index < len(candidates):
                return candidates[index]

        for player in candidates:
            name = normalize(str(player["name"]))
            if text and (text in name or any(token in name.split() for token in text.split())):
                return player
        return None

    def player_info(self, player: dict[str, Any]) -> str:
        return responses.player_info(player)

    def player_records(self, player: dict[str, Any]) -> list[dict[str, Any]]:
        name = normalize(str(player["name"]))
        records = [record for record in self.players if normalize(str(record["name"])) == name]
        return sorted(records, key=lambda item: int(item.get("minutes", 0)), reverse=True)

    def player_teams(self, player: dict[str, Any]) -> str:
        records = self.player_records(player)
        if len(records) == 1:
            return f"{player['name']} plays for {player['team']} in {player['league']}."

        teams = ", ".join(
            f"{record['team']} ({record['league']}, {record['minutes']} minutes)"
            for record in records
        )
        return f"{player['name']} has 2024/25 dataset entries for: {teams}."

    def players_by_nationality(self, nationality: str, limit: int = 15) -> str:
        players = [
            player
            for player in self.best_player_records()
            if str(player.get("nationality", "")).casefold() == nationality.casefold()
        ]
        players.sort(key=lambda item: int(item.get("minutes", 0)), reverse=True)
        if not players:
            return f"I could not find players from {nationality} in the processed dataset."

        shown = ", ".join(f"{player['name']} ({player['team']})" for player in players[:limit])
        suffix = f" and {len(players) - limit} more" if len(players) > limit else ""
        return f"{nationality} players include: {shown}{suffix}."

    def top_scorers(self, league: Optional[str] = None, limit: int = 5) -> str:
        totals: dict[str, dict[str, Any]] = {}
        for player in self.players:
            if league and player.get("league") != league:
                continue
            key = normalize(str(player["name"]))
            item = totals.setdefault(
                key,
                {
                    "name": player["name"],
                    "teams": set(),
                    "goals": 0,
                    "assists": 0,
                    "matches": 0,
                    "minutes": 0,
                },
            )
            item["teams"].add(player["team"])
            item["goals"] += int(player.get("goals", 0))
            item["assists"] += int(player.get("assists", 0))
            item["matches"] += int(player.get("matches", 0))
            item["minutes"] += int(player.get("minutes", 0))

        scorers = sorted(
            totals.values(),
            key=lambda item: (item["goals"], item["assists"], item["minutes"]),
            reverse=True,
        )
        if not scorers:
            return "I could not find scorers for that competition in the processed dataset."

        label = league or "the 2024/25 Top 5 leagues dataset"
        lines = []
        for index, player in enumerate(scorers[:limit], start=1):
            teams = ", ".join(sorted(player["teams"]))
            lines.append(f"{index}. {player['name']} ({teams}) - {player['goals']} goals")
        return f"Top scorers in {label}: " + "; ".join(lines) + "."

    def team_squad(self, team: dict[str, Any], limit: int = 15) -> str:
        squad = list(team.get("squad", []))
        shown = ", ".join(squad[:limit])
        return responses.team_squad(team, shown, max(0, len(squad) - limit))

    def teams_in_league(self, league: str) -> str:
        teams = sorted(
            [team["name"] for team in self.teams if team.get("league") == league],
            key=str.casefold,
        )
        if not teams:
            return f"I could not find teams for {league} in the processed dataset."
        return f"{league} teams in the 2024/25 dataset: {', '.join(teams)}."
