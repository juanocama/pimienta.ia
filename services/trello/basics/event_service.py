"""
Servicio para eventos recurrentes.

Responsabilidad: Gestión de eventos en lista 'eventos'.
"""

from typing import List
from services.trello.trello_client import TrelloClient
from services.trello.utils.naturals.response_formatter import ResponseFormatter
from services.trello.utils.naturals.card_helper import CardHelper
from datetime import datetime


class EventService:
    """
    Servicio para eventos recurrentes.
    """

    def __init__(self, client: TrelloClient):
        self.client = client

    def add_recurring_event(self, name: str, frequency: str, when: str, notes: str = "") -> str:
        try:
            eventos_list = self.client.get_list('eventos')
            if not eventos_list:
                return ResponseFormatter.format_error("No encontré la lista de eventos.")

            desc = f"Frecuencia: {frequency}\nCuándo: {when}\n{notes}"
            card = eventos_list.add_card(name=name, desc=desc)

            color_map = {'semanal': 'blue', 'mensual': 'purple', 'anual': 'orange'}
            color = color_map.get(frequency.lower(), 'blue')
            label = self._get_or_create_label(color)
            card.add_label(label)

            return ResponseFormatter.format_event_added(name)
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def _get_or_create_label(self, color: str):
        # Similar a otros services
        labels = self.client.board.get_labels()
        for label in labels:
            if label.color == color:
                return label
        return self.client.board.add_label(name=color.capitalize(), color=color)

    def list_recurring_events(self) -> str:
        try:
            eventos_list = self.client.get_list('eventos')
            if not eventos_list:
                return []
            cards = eventos_list.list_cards()
            events = [CardHelper.extract_card_info(card) for card in cards]
            return events
        except Exception as e:
            return []

    def list_events_today(self) -> str:
        try:
            hoy = datetime.now()
            dia_semana = hoy.strftime("%A").lower()
            dias_esp = {
                "monday": "lunes", "tuesday": "martes", "wednesday": "miércoles",
                "thursday": "jueves", "friday": "viernes", "saturday": "sábado",
                "sunday": "domingo"
            }
            dia_esp = dias_esp.get(dia_semana, dia_semana)

            eventos_list = self.client.get_list('eventos')
            if not eventos_list:
                return []

            cards = eventos_list.list_cards()
            events_hoy = []
            for card in cards:
                desc_lower = card.desc.lower()
                if dia_esp in desc_lower or dia_semana in desc_lower:
                    events_hoy.append(CardHelper.extract_card_info(card))
            return events_hoy
        except Exception as e:
            return []