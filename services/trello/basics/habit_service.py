"""
Servicio para gestión de hábitos.

Responsabilidad: Tracking de hábitos en lista 'habitos'.
"""

from typing import List
from datetime import datetime
from services.trello.trello_client import TrelloClient
from services.trello.utils.naturals.response_formatter import ResponseFormatter
from services.trello.utils.naturals.card_helper import CardHelper


class HabitService:
    """
    Servicio para hábitos.
    """

    def __init__(self, client: TrelloClient):
        self.client = client

    def add_habit(self, name: str, description: str = "") -> str:
        try:
            habitos_list = self.client.get_list('habitos')
            if not habitos_list:
                return ResponseFormatter.format_error("No encontré la lista de hábitos.")

            card = habitos_list.add_card(name=name, desc=description)
            return ResponseFormatter.format_task_added(name)  # Reusar para hábitos
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def mark_habit_today(self, habit_name: str) -> str:
        try:
            habitos_list = self.client.get_list('habitos')
            if not habitos_list:
                return ResponseFormatter.format_not_found("hábito")

            cards = habitos_list.list_cards()
            for card in cards:
                if habit_name.lower() in card.name.lower():
                    hoy = datetime.now().strftime("%d/%m/%Y")
                    card.comment(f"✅ Completado: {hoy}")
                    return ResponseFormatter.format_habit_marked(card.name)
            return ResponseFormatter.format_not_found("hábito")
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def get_habit_history(self, habit_name: str) -> str:
        try:
            habitos_list = self.client.get_list('habitos')
            if not habitos_list:
                return ResponseFormatter.format_not_found("hábito")

            cards = habitos_list.list_cards()
            for card in cards:
                if habit_name.lower() in card.name.lower():
                    comments = [c.get('data', {}).get('text', '') for c in card.comments]
                    return ResponseFormatter.format_habit_history(comments)
            return ResponseFormatter.format_not_found("hábito")
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def list_habits(self) -> str:
        try:
            habitos_list = self.client.get_list('habitos')
            if not habitos_list:
                return []
            cards = habitos_list.list_cards()
            habits = [CardHelper.extract_card_info(card) for card in cards]
            return habits
        except Exception as e:
            return []