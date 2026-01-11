"""
Servicio para tareas con fechas específicas.

Responsabilidad: Gestión de tareas programadas en 'todo' o 'semana'.
"""

from typing import List
from datetime import datetime, timedelta
from services.trello.trello_client import TrelloClient
from services.trello.utils.date_parser import DateParser
from services.trello.utils.naturals.response_formatter import ResponseFormatter
from services.trello.utils.naturals.card_helper import CardHelper


class ScheduleService:
    """
    Servicio para tareas con fecha.
    """

    def __init__(self, client: TrelloClient):
        self.client = client

    def add_task_with_date(self, name: str, date_str: str, description: str = "", priority: str = None) -> str:
        try:
            date_obj = DateParser.parse(date_str)
            if not date_obj:
                return ResponseFormatter.format_error("Fecha inválida.")

            hoy = datetime.now()
            list_name = 'semana' if (date_obj - hoy).days <= 7 else 'todo'
            task_list = self.client.get_list(list_name)
            if not task_list:
                return ResponseFormatter.format_error(f"No encontré la lista '{list_name}'.")

            card = task_list.add_card(name=name, desc=description)
            # py-trello expects an ISO string for due dates; convert explicitly
            try:
                iso = DateParser.to_trello_format(date_obj)
                card.set_due(iso)
            except Exception:
                # fallback: try passing datetime directly
                card.set_due(date_obj)

            if priority:
                color_map = {'alta': 'red', 'media': 'yellow', 'baja': 'green'}
                color = color_map.get(priority.lower(), 'yellow')
                label = self._get_or_create_label(color)
                card.add_label(label)

            return ResponseFormatter.format_task_added(name, date_obj)
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def _get_or_create_label(self, color: str):
        # Similar a TaskService
        labels = self.client.board.get_labels()
        for label in labels:
            if label.color == color:
                return label
        return self.client.board.add_label(name=color.capitalize(), color=color)

    def list_tasks_for_date(self, date_str: str) -> str:
        try:
            date_obj = DateParser.parse(date_str)
            if not date_obj:
                return ResponseFormatter.format_error("Fecha inválida.")
            tasks = []
            for list_name in ['todo', 'semana']:
                task_list = self.client.get_list(list_name)
                if task_list:
                    cards = task_list.list_cards()
                    for card in cards:
                        due = CardHelper.normalize_datetime(card.due_date)
                        if due and due.date() == date_obj.date() and not CardHelper.is_completed_on(card, date_obj):
                            tasks.append(CardHelper.extract_card_info(card))

            # Return raw list of task dicts; formatting is responsibility of caller
            return tasks
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def list_tasks_this_week(self) -> str:
        hoy = datetime.now()
        fin_semana = hoy + timedelta(days=7)
        return self._list_tasks_in_range(hoy, fin_semana, "esta semana")

    def list_tasks_next_week(self) -> str:
        inicio_proxima = datetime.now() + timedelta(days=7)
        fin_proxima = inicio_proxima + timedelta(days=7)
        return self._list_tasks_in_range(inicio_proxima, fin_proxima, "próxima semana")

    def _list_tasks_in_range(self, start: datetime, end: datetime, period: str) -> str:
        tasks = []
        for list_name in ['todo', 'semana']:
            task_list = self.client.get_list(list_name)
            if task_list:
                cards = task_list.list_cards()
                for card in cards:
                    due = CardHelper.normalize_datetime(card.due_date)
                    if due and start <= due <= end and not CardHelper.is_completed_on(card, due):
                        tasks.append(CardHelper.extract_card_info(card))
        return tasks