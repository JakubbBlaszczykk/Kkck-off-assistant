from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kickoff_assistant.knowledge_base import KnowledgeBase
from kickoff_assistant import responses


def entity_value(tracker: Tracker, entity_name: str) -> str:
    value = next(tracker.get_latest_entity_values(entity_name), None)
    if value:
        return str(value)
    return tracker.latest_message.get("text", "")


class KnowledgeAction(Action):
    kb: Optional[KnowledgeBase] = None

    @classmethod
    def knowledge_base(cls) -> KnowledgeBase:
        if cls.kb is None:
            cls.kb = KnowledgeBase.load(ROOT / "data" / "processed")
        return cls.kb


class ActionPlayerInfo(KnowledgeAction):
    def name(self) -> str:
        return "action_player_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict[str, Any]]:
        player = self.knowledge_base().find_player(entity_value(tracker, "player_name"))
        if not player:
            dispatcher.utter_message(text=responses.not_found("player"))
            return []

        dispatcher.utter_message(text=self.knowledge_base().player_info(player))
        return []


class ActionTeamSquad(KnowledgeAction):
    def name(self) -> str:
        return "action_team_squad"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict[str, Any]]:
        team = self.knowledge_base().find_team(entity_value(tracker, "team_name"))
        if not team:
            dispatcher.utter_message(text=responses.not_found("team"))
            return []

        dispatcher.utter_message(text=self.knowledge_base().team_squad(team))
        return []


class ActionPlayerPosition(KnowledgeAction):
    def name(self) -> str:
        return "action_player_position"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict[str, Any]]:
        player = self.knowledge_base().find_player(entity_value(tracker, "player_name"))
        if not player:
            dispatcher.utter_message(text=responses.not_found("player"))
            return []

        dispatcher.utter_message(text=responses.player_position(player))
        return []


class ActionPlayerNationality(KnowledgeAction):
    def name(self) -> str:
        return "action_player_nationality"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict[str, Any]]:
        player = self.knowledge_base().find_player(entity_value(tracker, "player_name"))
        if not player:
            dispatcher.utter_message(text=responses.not_found("player"))
            return []

        dispatcher.utter_message(text=responses.player_nationality(player))
        return []


class ActionPlayerStats(KnowledgeAction):
    def name(self) -> str:
        return "action_player_stats"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict[str, Any]]:
        player = self.knowledge_base().find_player(entity_value(tracker, "player_name"))
        if not player:
            dispatcher.utter_message(text=responses.not_found("player"))
            return []

        dispatcher.utter_message(text=responses.player_stats(player))
        return []
