"""
Utilidades para manejar cards de Trello.

Responsabilidad: Operaciones comunes sobre cards como normalización,
chequeo de completado y extracción de info.
"""

from typing import Dict, Optional
from datetime import date, datetime
from dateutil import parser  # Asumiendo python-dateutil instalado


class CardHelper:
    """
    Helper para operaciones comunes con cards de Trello.
    """

    @staticmethod
    def normalize_datetime(value: any) -> Optional[datetime]:
        """
        Normaliza distintos tipos a datetime.
        
        Acepta datetime, date, str o None.
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        try:
            return parser.parse(str(value))
        except Exception:
            return None

    @staticmethod
    def is_completed_on(card: any, date_obj: datetime) -> bool:
        """
        Verifica si la card fue completada en una fecha específica.
        
        Busca en comentarios: 'Completado: DD/MM/YYYY'
        """
        if not card.comments:
            return False

        target_str = date_obj.strftime('%d/%m/%Y')
        for comment in card.comments:
            text = comment.get('data', {}).get('text', '') if isinstance(comment, dict) else str(comment)
            if 'complet' in text.lower() and target_str in text:
                return True
        return False

    @staticmethod
    def get_priority_emoji(card: any) -> str:
        """
        Obtiene emoji de prioridad basado en labels.
        """
        if not card.labels:
            return ""
        colors = [label.color for label in card.labels]
        if 'red' in colors:
            return "🔴"
        if 'yellow' in colors:
            return "🟡"
        if 'green' in colors:
            return "🟢"
        return ""

    @staticmethod
    def extract_card_info(card: any) -> Dict:
        """
        Extrae info relevante de una card.
        
        Returns:
            {'name': str, 'description': str, 'due_date': datetime|None, 
             'priority': str|None, 'comments': list}
        """
        priority = None
        if card.labels:
            colors = [label.color for label in card.labels]
            if 'red' in colors:
                priority = 'alta'
            elif 'yellow' in colors:
                priority = 'media'
            elif 'green' in colors:
                priority = 'baja'

        return {
            'name': card.name,
            'description': card.desc,
            'due_date': CardHelper.normalize_datetime(card.due_date),
            'priority': priority,
            'comments': card.comments or []
        }