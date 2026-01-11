"""
Cliente para conectarse a la API de Trello.

Maneja la conexión, autenticación y mapeo de listas del tablero.
"""

from typing import Dict, Optional
import logging

try:
    from trello import TrelloClient as PyTrelloClient
except ImportError:
    PyTrelloClient = None


logger = logging.getLogger(__name__)


class TrelloClient:
    """
    Cliente para gestionar la conexión con Trello.
    
    Responsabilidad única: establecer conexión y proveer acceso
    a las listas del tablero configurado.
    """

    def __init__(self, api_key: str, api_token: str, board_id: str):
        """
        Inicializa el cliente de Trello.
        
        Args:
            api_key: API Key de Trello
            api_token: Token de autenticación
            board_id: ID del tablero principal
            
        Raises:
            ImportError: Si py-trello no está instalado
            ConnectionError: Si no puede conectarse a Trello
            ValueError: Si las credenciales son inválidas
        """
        if PyTrelloClient is None:
            raise ImportError(
                "El paquete 'py-trello' no está instalado. "
                "Instálalo con: pip install py-trello"
            )

        if not api_key or not api_token or not board_id:
            raise ValueError(
                "Faltan credenciales de Trello. "
                "Verifica TRELLO_API_KEY, TRELLO_API_TOKEN y TRELLO_BOARD_ID en .env"
            )

        try:
            self.client = PyTrelloClient(
                api_key=api_key,
                token=api_token
            )
            
            self.board = self.client.get_board(board_id)
            self.lists = self._map_lists()
            
            logger.info(f"Conectado a Trello - Tablero: {self.board.name}")
            logger.info(f"Listas encontradas: {list(self.lists.keys())}")
            
        except Exception as e:
            logger.error(f"Error al conectar con Trello: {e}")
            raise ConnectionError(f"No pude conectarme a Trello: {e}")

    def _map_lists(self) -> Dict[str, any]:
        """
        Mapea las listas del tablero a nombres estándar.
        
        Busca listas con nombres que contengan:
        - 'to-do' o 'todo' -> 'todo'
        - 'semana' o 'week' -> 'semana'
        - 'recurrent' o 'eventos' -> 'eventos'
        - 'hábito' o 'habit' -> 'habitos'
        - 'completado' o 'done' -> 'completado'
        
        Returns:
            Diccionario con nombres estándar como keys y objetos List como valores
        """
        all_lists = self.board.list_lists()
        mapped_lists = {}

        for trello_list in all_lists:
            name_lower = trello_list.name.lower()

            # Mapeo flexible por palabras clave
            if any(keyword in name_lower for keyword in ['to-do', 'todo', 'pendientes']):
                mapped_lists['todo'] = trello_list
                
            elif any(keyword in name_lower for keyword in ['semana', 'week', 'esta semana']):
                mapped_lists['semana'] = trello_list
                
            elif any(keyword in name_lower for keyword in ['recurrent', 'eventos', 'event']):
                mapped_lists['eventos'] = trello_list
                
            elif any(keyword in name_lower for keyword in ['hábito', 'habito', 'habit']):
                mapped_lists['habitos'] = trello_list
                
            elif any(keyword in name_lower for keyword in ['completado', 'done', 'terminado']):
                mapped_lists['completado'] = trello_list

        # Validar que existan las listas esenciales
        required_lists = ['todo', 'completado']
        missing = [name for name in required_lists if name not in mapped_lists]
        
        if missing:
            logger.warning(f"Listas faltantes en Trello: {missing}")
            logger.warning("Se recomienda crear estas listas en tu tablero")

        return mapped_lists

    def get_list(self, list_name: str) -> Optional[any]:
        """
        Obtiene una lista específica del tablero.
        
        Args:
            list_name: Nombre de la lista ('todo', 'semana', etc.)
            
        Returns:
            Objeto List de Trello o None si no existe
        """
        return self.lists.get(list_name)

    def get_all_lists(self) -> Dict[str, any]:
        """Retorna todas las listas mapeadas"""
        return self.lists

    def refresh_lists(self):
        """Recarga el mapeo de listas (útil si se crean/eliminan listas)"""
        self.lists = self._map_lists()
        logger.info("Listas recargadas")

    def get_board_name(self) -> str:
        """Retorna el nombre del tablero"""
        return self.board.name

    def validate_connection(self) -> bool:
        """
        Valida que la conexión con Trello esté activa.
        
        Returns:
            True si la conexión es válida, False en caso contrario
        """
        try:
            # Intentar obtener el nombre del tablero
            _ = self.board.name
            return True
        except Exception as e:
            logger.error(f"Conexión con Trello inválida: {e}")
            return False


class TrelloConnectionError(Exception):
    """Excepción personalizada para errores de conexión con Trello"""
    pass


class TrelloAuthError(Exception):
    """Excepción personalizada para errores de autenticación"""
    pass


# Factory function para crear clientes con manejo de errores
def create_trello_client(api_key: str, api_token: str, board_id: str) -> Optional[TrelloClient]:
    """
    Factory function para crear un cliente de Trello con manejo de errores.
    
    Args:
        api_key: API Key de Trello
        api_token: Token de autenticación
        board_id: ID del tablero
        
    Returns:
        TrelloClient si la conexión es exitosa, None en caso contrario
    """
    try:
        return TrelloClient(api_key, api_token, board_id)
    except ImportError as e:
        logger.error(f"Dependencia faltante: {e}")
        return None
    except ValueError as e:
        logger.error(f"Credenciales inválidas: {e}")
        raise TrelloAuthError(str(e))
    except ConnectionError as e:
        logger.error(f"Error de conexión: {e}")
        raise TrelloConnectionError(str(e))
    except Exception as e:
        logger.error(f"Error inesperado al crear cliente Trello: {e}")
        return None