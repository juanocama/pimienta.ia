"""
Servicio para operaciones básicas de tareas (sin fecha).

Responsabilidad: CRUD de tareas en listas 'todo' y 'completado'.
"""

from typing import List, Dict
from services.trello.trello_client import TrelloClient
from services.trello.utils.naturals.response_formatter import ResponseFormatter
from services.trello.utils.naturals.card_helper import CardHelper


class TaskService:
    """
    Servicio para gestión de tareas básicas.
    """

    def __init__(self, client: TrelloClient):
        self.client = client

    def add_task(self, name: str, description: str = "", priority: str = None) -> str:
        try:
            todo_list = self.client.get_list('todo')
            if not todo_list:
                return ResponseFormatter.format_error("No encontré la lista de tareas pendientes.")

            card = todo_list.add_card(name=name, desc=description)
            
            if priority:
                color_map = {'alta': 'red', 'media': 'yellow', 'baja': 'green'}
                color = color_map.get(priority.lower(), 'yellow')
                label = self._get_or_create_label(color)
                card.add_label(label)

            return ResponseFormatter.format_task_added(name)
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def _get_or_create_label(self, color: str):
        labels = self.client.board.get_labels()
        for label in labels:
            if label.color == color:
                return label
        return self.client.board.add_label(name=color.capitalize(), color=color)

    def list_tasks(self, list_name: str = 'todo') -> List[Dict]:
        try:
            task_list = self.client.get_list(list_name)
            if not task_list:
                return []
            cards = task_list.list_cards()
            return [CardHelper.extract_card_info(card) for card in cards if not card.due_date]  # Solo sin fecha
        except Exception:
            return []

    def complete_task(self, task_name: str) -> str:
        try:
            for list_name in ['todo', 'semana']:
                task_list = self.client.get_list(list_name)
                if task_list:
                    cards = task_list.list_cards()
                    for card in cards:
                        if task_name.lower() in card.name.lower():
                            completado_list = self.client.get_list('completado')
                            if completado_list:
                                card.change_list(completado_list.id)
                                return ResponseFormatter.format_task_completed(card.name)
            return ResponseFormatter.format_not_found("tarea")
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def delete_task(self, task_name: str) -> str:
        try:
            for task_list in self.client.get_all_lists().values():
                cards = task_list.list_cards()
                for card in cards:
                    if task_name.lower() in card.name.lower():
                        card.delete()
                        return f"He eliminado la tarea '{card.name}'."
            return ResponseFormatter.format_not_found("tarea")
        except Exception as e:
            return ResponseFormatter.format_error(str(e))

    def search_tasks(self, term: str) -> List[Dict]:
        results = []
        for list_name in ['todo', 'semana']:
            tasks = self.list_tasks(list_name)
            results.extend([task for task in tasks if term.lower() in task['name'].lower()])
        return results