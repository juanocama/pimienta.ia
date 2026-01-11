from core.actions.base_action import BaseAction
from typing import Optional, Dict, Any
import logging
from services.trello.utils.date_parser import DateParser
from services.trello.utils.naturals.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

def _get_mock_services():
    """Retorna servicios simulados en caso de fallo de conexión o configuración."""
    class MockService:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                return f"[TRELLO MOCK] {name} ejecutado con {args} {kwargs}"
            return method

    mock = MockService()
    return {k: mock for k in ['task', 'schedule', 'event', 'habit', 'query']}


def _get_trello_services():
    """Inicializa servicios reales de Trello con Lazy Loading y fallback a mocks."""
    try:
        from infrastructure.config.settings import settings
        from services.trello.trello_client import TrelloClient
        from services.trello.list.task_service import TaskService
        from services.trello.basics.schedule_service import ScheduleService
        from services.trello.basics.event_service import EventService
        from services.trello.basics.habit_service import HabitService
        from services.trello.basics.query_service import QueryService

        client = TrelloClient(
            api_key=settings.TRELLO_API_KEY,
            api_token=settings.TRELLO_API_TOKEN,
            board_id=settings.TRELLO_BOARD_ID
        )

        task_service = TaskService(client)
        schedule_service = ScheduleService(client)
        event_service = EventService(client)
        habit_service = HabitService(client)
        query_service = QueryService(
            client=client,
            task_service=task_service,
            schedule_service=schedule_service,
            event_service=event_service,
            habit_service=habit_service
        )

        return {
            'task': task_service, 'schedule': schedule_service,
            'event': event_service, 'habit': habit_service, 'query': query_service
        }

    except Exception as e:
        logger.error(f"No se pudo inicializar Trello: {e}", exc_info=True)
        return _get_mock_services()


class TrelloAction(BaseAction):
    """Acción para integrar operaciones de Trello en el sistema Pimienta."""

    def __init__(self, services: Optional[Dict[str, Any]] = None):
        self.services = services or _get_trello_services()

    def execute(self, params: dict) -> str:
        """
        Punto de entrada principal. 
        params debe incluir 'command' y los argumentos requeridos por dicho comando.
        """
        command = params.get("command")

        if not command:
            return "No se especificó ningún comando para Trello."

        try:
            # Tareas
            if command == "add_task":
                # Support follow-up flow where the user reply is stored in 'query'
                name = params.get("name", "") or params.get("query", "")

                # If the query contains a date, delegate to schedule service
                if params.get("query"):
                    try:
                        dt = DateParser.parse(params.get("query"))
                    except Exception:
                        dt = None

                    if dt:
                        # Remove common date words to extract a cleaner task name
                        raw = params.get("query", "")
                        # Simple removal of weekday/month tokens
                        tokens = list(DateParser.DIAS_SEMANA.keys()) + list(DateParser.MESES.keys())
                        tokens += ["hoy", "mañana", "manana", "pasado mañana", "pasado manana"]
                        cleaned = raw
                        for t in tokens:
                            cleaned = cleaned.replace(t, "")
                        # Also remove connectors
                        cleaned = cleaned.replace("el", "").replace("la", "").replace("para", "").strip()
                        name = name or cleaned
                        # Use schedule service to add with date
                        return self.services['schedule'].add_task_with_date(
                            name=name or params.get("query", ""),
                            date_str=DateParser.to_trello_format(dt),
                            description=params.get("description", ""),
                            priority=params.get("priority")
                        )

                return self.services['task'].add_task(
                    name=name,
                    description=params.get("description", ""),
                    priority=params.get("priority")
                )

            if command == "complete_task":
                return self.services['task'].complete_task(task_name=params.get("name", ""))

            if command == "delete_task":
                return self.services['task'].delete_task(task_name=params.get("name", ""))

            if command == "search_task":
                results = self.services['task'].search_tasks(term=params.get("query", ""))
                if not results:
                    return "No encontré ninguna tarea con ese término."
                return f"Encontré {len(results)} tareas: " + ", ".join(r['name'] for r in results)

            # Agendamiento y Consultas
            if command == "add_task_date":
                return self.services['schedule'].add_task_with_date(
                    name=params.get("name", ""),
                    date_str=params.get("date", ""),
                    description=params.get("description", ""),
                    priority=params.get("priority")
                )

            if command == "summary_today":
                return self.services['query'].get_today_summary()

            if command == "summary_tomorrow":
                return self.services['query'].get_tomorrow_summary()

            if command == "summary_week":
                return self.services['query'].get_week_summary()

            if command == "list_today_tasks":
                tasks = self.services['schedule'].list_tasks_for_date("hoy")
                # tasks is a list of dicts; format for voice
                return ResponseFormatter.format_tasks_list(tasks, "tareas para esa fecha")

            # Hábitos
            if command == "add_habit":
                return self.services['habit'].add_habit(
                    name=params.get("name", ""),
                    description=params.get("description", "")
                )

            if command == "mark_habit":
                return self.services['habit'].mark_habit_today(habit_name=params.get("name", ""))

            if command == "habit_history":
                return self.services['habit'].get_habit_history(habit_name=params.get("name", ""))

            if command == "list_habits":
                habits = self.services['habit'].list_habits()
                return ResponseFormatter.format_tasks_list(habits, "hábitos")

            # Eventos
            if command == "add_event":
                return self.services['event'].add_recurring_event(
                    name=params.get("name", ""),
                    frequency=params.get("frequency", "semanal"),
                    when=params.get("when", ""),
                    notes=params.get("notes", "")
                )

            if command == "list_events":
                events = self.services['event'].list_recurring_events()
                return ResponseFormatter.format_tasks_list(events, "eventos recurrentes")

            if command == "events_today":
                events = self.services['event'].list_events_today()
                return ResponseFormatter.format_tasks_list(events, "eventos para hoy")

            if command == "health_check":
                return self.health_check()

            return f"Comando '{command}' no reconocido."

        except Exception as e:
            logger.error(f"Error en comando Trello '{command}': {e}", exc_info=True)
            return f"Error en la acción de Trello: {str(e)}"

    def health_check(self) -> str:
        """Verifica la salud de la conexión con la API de Trello."""
        try:
            query_service = self.services.get('query')
            if hasattr(query_service, 'client') and query_service.client.validate_connection():
                return "Trello: conexión activa (ok)"
            return "Trello: usando modo simulado (mock)"
        except Exception:
            return "Trello: error al verificar estado"