"""
Servicio para consultas agregadas y resúmenes.

Responsabilidad: Combinar datos de otros servicios para resúmenes.
"""

from typing import Dict
from datetime import datetime, timedelta
from services.trello.trello_client import TrelloClient
from services.trello.utils.naturals.response_formatter import ResponseFormatter
from services.trello.list.task_service import TaskService
from .schedule_service import ScheduleService
from .event_service import EventService
from .habit_service import HabitService


class QueryService:
    """
    Servicio para queries agregadas.
    
    Depende de otros services para composición.
    """

    def __init__(self, client: TrelloClient, task_service: TaskService, 
                 schedule_service: ScheduleService, event_service: EventService, 
                 habit_service: HabitService):
        self.client = client
        self.task_service = task_service
        self.schedule_service = schedule_service
        self.event_service = event_service
        self.habit_service = habit_service

    def get_today_summary(self) -> str:
        hoy = datetime.now().strftime('%Y-%m-%d')  # Formato para list_tasks_for_date
        data = {
            'tasks': self.task_service.list_tasks('todo') + self.schedule_service.list_tasks_for_date(hoy),
            'habits': self.habit_service.list_habits(),
            'events': self.event_service.list_events_today()
        }
        return ResponseFormatter.format_summary_today(data)

    def get_tomorrow_summary(self) -> str:
        mañana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        data = {
            'tasks': self.schedule_service.list_tasks_for_date(mañana),
            'habits': self.habit_service.list_habits(),  # Hábitos son diarios, asumir pendientes
            'events': []  # Eventos para mañana requerirían lógica adicional
        }
        return ResponseFormatter.format_summary_today(data)  # Reusar formatter

    def get_week_summary(self) -> str:
        return self.schedule_service.list_tasks_this_week()

    def search_all(self, term: str) -> str:
        results = []
        results.extend(self.task_service.search_tasks(term))
        # Agregar búsquedas en otros services si necesario
        if results:
            return ResponseFormatter.format_tasks_list(results, "resultados")
        return ResponseFormatter.format_not_found("nada")