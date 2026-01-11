"""
Parseo de fechas en lenguaje natural para Trello.

Convierte expresiones como "mañana", "el viernes", "en 3 días"
a objetos datetime utilizables.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


class DateParser:
    """Parser de fechas en lenguaje natural para español"""

    DIAS_SEMANA = {
        'lunes': 0,
        'martes': 1,
        'miércoles': 2,
        'miercoles': 2,
        'jueves': 3,
        'viernes': 4,
        'sábado': 5,
        'sabado': 5,
        'domingo': 6
    }

    MESES = {
        'enero': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12
    }

    @staticmethod
    def parse(text: str) -> Optional[datetime]:
        """
        Intenta parsear una fecha en lenguaje natural.
        
        Args:
            text: Texto que contiene la fecha ("mañana", "el viernes", etc.)
            
        Returns:
            datetime object o None si no puede parsear
        """
        if not text:
            return None

        text = text.lower().strip()

        # Intentar diferentes estrategias en orden
        parsers = [
            DateParser._parse_relative_simple,
            DateParser._parse_day_of_week,
            DateParser._parse_in_x_days,
            DateParser._parse_specific_date,
            DateParser._parse_iso_date,
        ]

        for parser in parsers:
            result = parser(text)
            if result:
                return result

        return None

    @staticmethod
    def _parse_relative_simple(text: str) -> Optional[datetime]:
        """Parsea: hoy, mañana, pasado mañana"""
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if text == 'hoy':
            return hoy
        
        if text == 'mañana' or text == 'manana':
            return hoy + timedelta(days=1)
        
        if 'pasado mañana' in text or 'pasado manana' in text:
            return hoy + timedelta(days=2)

        return None

    @staticmethod
    def _parse_day_of_week(text: str) -> Optional[datetime]:
        """
        Parsea: "el lunes", "este viernes", "próximo martes"
        Retorna el próximo día de la semana especificado
        """
        hoy = datetime.now()
        dia_actual = hoy.weekday()

        for nombre, numero in DateParser.DIAS_SEMANA.items():
            if nombre in text:
                # Calcular días hasta ese día de la semana
                dias_hasta = (numero - dia_actual) % 7
                
                # Si es 0 (hoy) y dice "el/este/próximo", ir a la próxima semana
                if dias_hasta == 0:
                    if any(palabra in text for palabra in ['el', 'este', 'próximo', 'proximo']):
                        dias_hasta = 7
                
                # Si dice "próximo/siguiente", siempre ir a la siguiente semana
                if any(palabra in text for palabra in ['próximo', 'proximo', 'siguiente']):
                    if dias_hasta == 0:
                        dias_hasta = 7
                    elif dias_hasta < 7:
                        dias_hasta += 7

                fecha = hoy + timedelta(days=dias_hasta)
                return fecha.replace(hour=0, minute=0, second=0, microsecond=0)

        return None

    @staticmethod
    def _parse_in_x_days(text: str) -> Optional[datetime]:
        """Parsea: "en 3 días", "dentro de 5 días"""
        # Buscar patrón "en X días" o "dentro de X días"
        pattern = r'(?:en|dentro\s+de)\s+(\d+)\s+días?'
        match = re.search(pattern, text)
        
        if match:
            dias = int(match.group(1))
            hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return hoy + timedelta(days=dias)

        return None

    @staticmethod
    def _parse_specific_date(text: str) -> Optional[datetime]:
        """
        Parsea fechas específicas:
        - "15 de marzo"
        - "25 de diciembre"
        - "DD/MM/YYYY"
        - "DD/MM"
        """
        # Patrón: DD de MES
        pattern_mes = r'(\d{1,2})\s+de\s+(\w+)'
        match = re.search(pattern_mes, text)
        
        if match:
            dia = int(match.group(1))
            mes_texto = match.group(2).lower()
            
            if mes_texto in DateParser.MESES:
                mes = DateParser.MESES[mes_texto]
                año_actual = datetime.now().year
                
                try:
                    fecha = datetime(año_actual, mes, dia)
                    # Si la fecha ya pasó este año, usar el próximo año
                    if fecha < datetime.now():
                        fecha = datetime(año_actual + 1, mes, dia)
                    return fecha
                except ValueError:
                    return None

        # Patrón: DD/MM/YYYY o DD/MM
        pattern_slash = r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?'
        match = re.search(pattern_slash, text)
        
        if match:
            dia = int(match.group(1))
            mes = int(match.group(2))
            año = match.group(3)
            
            if año:
                año = int(año)
                if año < 100:  # Convertir 24 -> 2024
                    año += 2000
            else:
                año = datetime.now().year
                # Si la fecha ya pasó, usar próximo año
                try:
                    temp = datetime(año, mes, dia)
                    if temp < datetime.now():
                        año += 1
                except ValueError:
                    pass
            
            try:
                return datetime(año, mes, dia)
            except ValueError:
                return None

        return None

    @staticmethod
    def _parse_iso_date(text: str) -> Optional[datetime]:
        """Parsea fechas ISO: YYYY-MM-DD"""
        pattern = r'(\d{4})-(\d{2})-(\d{2})'
        match = re.search(pattern, text)
        
        if match:
            try:
                año = int(match.group(1))
                mes = int(match.group(2))
                dia = int(match.group(3))
                return datetime(año, mes, dia)
            except ValueError:
                return None

        return None

    @staticmethod
    def to_trello_format(dt: datetime) -> str:
        """Convierte datetime a formato compatible con Trello API"""
        return dt.isoformat()

    @staticmethod
    def to_display_format(dt: datetime) -> str:
        """Convierte datetime a formato legible en español"""
        dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        
        dia_semana = dias[dt.weekday()]
        mes = meses[dt.month - 1]
        
        return f"{dia_semana} {dt.day} de {mes}"


# Función helper para uso rápido
def parse_natural_date(text: str) -> Optional[datetime]:
    """
    Helper function para parsear fechas rápidamente.
    
    Ejemplos:
        >>> parse_natural_date("mañana")
        datetime(2026, 1, 11, 0, 0)
        
        >>> parse_natural_date("el viernes")
        datetime(2026, 1, 16, 0, 0)
    """
    return DateParser.parse(text)