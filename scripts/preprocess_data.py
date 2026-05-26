from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Optional


DEFAULT_INPUT = Path("data/raw/players_data-2024_2025.csv")
DEFAULT_OUTPUT = Path("data/processed")


def clean_text(value: Optional[str]) -> str:
    return (value or "").strip()


def parse_float(value: Optional[str]) -> Optional[float]:
    value = clean_text(value)
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: Optional[str]) -> Optional[int]:
    number = parse_float(value)
    if number is None:
        return None
    return int(number)


def normalize_nation(value: Optional[str]) -> str:
    value = clean_text(value)
    if not value:
        return ""
    parts = value.split(maxsplit=1)
    return parts[1] if len(parts) == 2 and len(parts[0]) <= 3 else value


def normalize_competition(value: Optional[str]) -> str:
    value = clean_text(value)
    if not value:
        return ""
    parts = value.split(maxsplit=1)
    return parts[1] if len(parts) == 2 and len(parts[0]) <= 3 else value


def player_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        clean_text(row.get("Player")).casefold(),
        clean_text(row.get("Squad")).casefold(),
        clean_text(row.get("Comp")).casefold(),
    )


def build_player(row: dict[str, str]) -> dict[str, object]:
    return {
        "name": clean_text(row.get("Player")),
        "nationality": normalize_nation(row.get("Nation")),
        "position": clean_text(row.get("Pos")),
        "team": clean_text(row.get("Squad")),
        "league": normalize_competition(row.get("Comp")),
        "age": parse_int(row.get("Age")),
        "born": parse_int(row.get("Born")),
        "matches": parse_int(row.get("MP")) or 0,
        "starts": parse_int(row.get("Starts")) or 0,
        "minutes": parse_int(row.get("Min")) or 0,
        "goals": parse_int(row.get("Gls")) or 0,
        "assists": parse_int(row.get("Ast")) or 0,
        "yellow_cards": parse_int(row.get("CrdY")) or 0,
        "red_cards": parse_int(row.get("CrdR")) or 0,
        "xg": parse_float(row.get("xG")) or 0.0,
        "xag": parse_float(row.get("xAG")) or 0.0,
    }


def process(input_path: Path, output_dir: Path) -> dict[str, int]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    players_by_key: dict[tuple[str, str, str], dict[str, object]] = {}
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = clean_text(row.get("Player"))
            squad = clean_text(row.get("Squad"))
            if not name or not squad:
                continue
            key = player_key(row)
            player = build_player(row)
            current = players_by_key.get(key)
            if current is None or int(player["minutes"]) > int(current["minutes"]):
                players_by_key[key] = player

    players = sorted(
        players_by_key.values(),
        key=lambda item: (str(item["team"]).casefold(), str(item["name"]).casefold()),
    )

    teams_map: dict[str, dict[str, object]] = {}
    squad_names: dict[str, list[str]] = defaultdict(list)
    for player in players:
        team_name = str(player["team"])
        teams_map.setdefault(
            team_name,
            {
                "name": team_name,
                "league": player["league"],
                "country": "",
                "squad": [],
            },
        )
        squad_names[team_name].append(str(player["name"]))

    teams = []
    for team_name, team in teams_map.items():
        team["squad"] = sorted(set(squad_names[team_name]), key=str.casefold)
        teams.append(team)
    teams.sort(key=lambda item: str(item["name"]).casefold())

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "players.json").write_text(
        json.dumps(players, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "teams.json").write_text(
        json.dumps(teams, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {"players": len(players), "teams": len(teams)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Process football CSV data for KickOff Assistant.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    stats = process(args.input, args.output)
    print(f"Processed {stats['players']} player rows into {stats['teams']} teams.")


if __name__ == "__main__":
    main()
