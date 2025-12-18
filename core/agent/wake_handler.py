import time


class WakeHandler:
    """Maneja la activación/desactivación del agente mediante wake word"""
    
    WAKE_WORD = "pimienta"
    ACTIVE_WINDOW = 30  # segundos
    SLEEP_COMMANDS = ("duerme", "descansa", "modo pasivo")

    def __init__(self):
        self.active = False
        self.active_until: float | None = None

    def process_input(self, user_input: str) -> tuple[bool, str, str | None]:
        """
        Procesa el input del usuario y maneja la activación.
        
        Returns:
            tuple: (should_continue, processed_input, response)
            - should_continue: False si debe ignorarse el input
            - processed_input: input sin wake word
            - response: respuesta inmediata o None
        """
        lowered = user_input.lower().strip()
        now = time.time()

        # Detectar wake word
        if lowered.startswith(self.WAKE_WORD):
            self.active = True
            self.active_until = now + self.ACTIVE_WINDOW

            processed = lowered.replace(self.WAKE_WORD, "", 1).strip()

            if not processed:
                return False, "", "¿Sí? Te escucho 👂"
            
            return True, processed, None

        # Verificar si está activo
        if not self.active:
            return False, "", None

        # Verificar expiración
        if self.active_until and time.time() > self.active_until:
            self.active = False
            self.active_until = None
            return False, "", None

        # Comandos de dormir
        if lowered in self.SLEEP_COMMANDS:
            self.active = False
            self.active_until = None
            return False, "", "Ok, me quedo en modo pasivo 😴"

        return True, user_input, None

    def refresh_window(self):
        """Refresca la ventana de actividad"""
        if self.active:
            self.active_until = time.time() + self.ACTIVE_WINDOW