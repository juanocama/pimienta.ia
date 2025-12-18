class MemoryService:
    """
    Servicio de memoria simplificado que maneja tanto strings como dicts.
    
    Keys utilizadas:
    - "music_preference": Gustos musicales específicos
    - "fact": Hechos generales
    """
    
    def __init__(self, memory):
        self.memory = memory

    def remember(self, data):
        """
        Guarda información en memoria.
        
        Args:
            data: puede ser str (texto plano) o dict (estructurado)
        
        Ejemplos:
            remember("trabajo en Google")  
            → guarda como fact
            
            remember({"type": "music_preference", "value": "rock"})  
            → guarda como music_preference
        """
        # -------- CASO 1: Dict estructurado --------
        if isinstance(data, dict):
            key = data.get("type", "fact")
            value = data.get("value", str(data))
            
            self.memory.save(key, value)
            return

        # -------- CASO 2: String (legacy/fallback) --------
        text = str(data)
        lowered = text.lower().strip()

        # Detectar preferencias musicales implícitas
        if lowered.startswith("me gusta"):
            preference = text[len("me gusta"):].strip()
            if preference:
                self.memory.save("music_preference", preference)
                return

        # Fallback: hecho genérico
        self.memory.save("fact", text)

    def recall(self, query: str) -> str | None:
        """
        Recupera información relevante de la memoria.
        
        Args:
            query: Texto de búsqueda
            
        Returns:
            String con resultados encontrados o None
        """
        lowered = query.lower()

        # -------- BÚSQUEDA DE PREFERENCIAS MUSICALES --------
        music_keywords = (
            "me gusta", "gustos", "música", "musica",
            "preferencias", "favorito", "favoritos",
            "escucho", "escuchar"
        )
        
        if any(kw in lowered for kw in music_keywords):
            results = self.memory.get_by_key("music_preference")
            
            if results:
                # Formatear respuesta amigable
                if len(results) == 1:
                    return f"Te gusta {results[0]}"
                else:
                    items = ", ".join(results[:-1]) + f" y {results[-1]}"
                    return f"Te gusta {items}"
            
            return None

        # -------- BÚSQUEDA GENERAL --------
        results = self.memory.search(query)
        
        if results:
            return "\n".join(results)
        
        return None

    def get_music_preferences(self) -> list[str]:
        """
        Obtiene todas las preferencias musicales almacenadas.
        
        Returns:
            Lista de preferencias o lista vacía
        """
        return self.memory.get_by_key("music_preference") or []

    def get_all_facts(self) -> list[str]:
        """
        Obtiene todos los hechos generales almacenados.
        
        Returns:
            Lista de hechos o lista vacía
        """
        return self.memory.get_by_key("fact") or []