"""
Formateador de respuestas para salida de voz (TTS).

Responsabilidad: Generar strings optimizados para síntesis de voz,
manteniendo brevedad, claridad y naturalidad en español.
"""

from typing import List, Dict, Optional
from datetime import datetime

from services.trello.utils.date_parser import DateParser


class ResponseFormatter:
    """
    Clase para formatear respuestas de Trello para voz.
    
    Principios:
    - Brevedad: Máximo 3-5 items detallados por lista
    - Naturalidad: Lenguaje conversacional
    - Estructura: Emojis auditivos (descritos si es necesario)
    - Resúmenes: Conteos para listas largas
    """

    @staticmethod
    def format_task_added(name: str, date: Optional[datetime] = None) -> str:
        """
        Formatea mensaje de tarea agregada.
        
        Ejemplo:
            "He agregado la tarea 'Comprar leche' para mañana."
        """
        base = f"He agregado la tarea '{name}'"
        if date:
            date_str = DateParser.to_display_format(date)  # Asumiendo DateParser importado
            base += f" para {date_str}."
        else:
            base += "."
        return base

    @staticmethod
    def format_tasks_list(tasks: List[Dict], category: str = "tareas") -> str:
        """
        Formatea lista de tareas/ítems.
        
        Args:
            tasks: Lista de dicts con 'name', 'priority' (opcional), 'date' (opcional)
            category: "tareas", "hábitos", "eventos"
        
        Ejemplo:
            "Tienes 3 tareas: reunión a las 10, llamar al doctor y terminar el reporte."
        """
        if not tasks:
            return f"No hay {category} pendientes."

        if len(tasks) > 3:
            summary = f"Tienes {len(tasks)} {category}. Las primeras son: "
            items = [ResponseFormatter._format_task_item(task) for task in tasks[:3]]
            return summary + ", ".join(items) + " y más."

        items = [ResponseFormatter._format_task_item(task) for task in tasks]
        return f"Tienes {len(tasks)} {category}: " + ", ".join(items) + "."

    @staticmethod
    def _format_task_item(task: Dict) -> str:
        """Formatea un ítem individual."""
        name = task.get('name', 'sin nombre')
        priority = task.get('priority')
        date = task.get('date')

        item = name
        if priority:
            priorities = {'alta': 'de alta prioridad', 'media': 'de prioridad media', 'baja': ''}
            item += f" ({priorities.get(priority, '')})" if priorities.get(priority) else ""
        if date:
            date_str = DateParser.to_display_format(date)
            item += f" para {date_str}"
        return item.strip()

    @staticmethod
    def format_summary_today(data: Dict) -> str:
        """
        Formatea resumen diario.
        
        Args:
            data: {'tasks': list, 'habits': list, 'events': list}
        
        Ejemplo:
            "Hoy tienes 2 tareas pendientes y 3 hábitos por completar."
        """
        parts = []
        
        if data.get('tasks'):
            parts.append(ResponseFormatter.format_tasks_list(data['tasks'], "tareas"))
        
        if data.get('habits'):
            parts.append(ResponseFormatter.format_tasks_list(data['habits'], "hábitos"))
        
        if data.get('events'):
            parts.append(ResponseFormatter.format_tasks_list(data['events'], "eventos"))
        
        if not parts:
            return "No tienes nada pendiente hoy. ¡Bien hecho!"
        
        return " ".join(parts)

    @staticmethod
    def format_task_completed(name: str) -> str:
        """Formatea mensaje de tarea completada."""
        return f"He marcado como completada la tarea '{name}'."

    @staticmethod
    def format_not_found(item: str) -> str:
        """Formatea mensaje de no encontrado."""
        return f"No encontré ninguna {item}."

    @staticmethod
    def format_error(message: str) -> str:
        """Formatea mensajes de error genéricos."""
        return f"Hubo un problema: {message}. Intenta de nuevo."

    @staticmethod
    def format_habit_marked(name: str) -> str:
        """Formatea marcado de hábito."""
        return f"He marcado el hábito '{name}' para hoy."

    @staticmethod
    def format_habit_history(history: List[str]) -> str:
        """Formatea historial de hábito."""
        if not history:
            return "No hay registros para este hábito."
        return f"Historial: " + ", ".join(history[-5:])  # Últimos 5 para brevedad

    @staticmethod
    def format_event_added(name: str) -> str:
        """Formatea evento agregado."""
        return f"He agregado el evento recurrente '{name}'."