import winsound # Apenas Windows
# ... imports ...

class GameStateDetector:
    # ... init ...

    def detect_state(self, image) -> GameState:
        # 1. Verifica os 4 Botões de Ação
        # Você precisará definir as coordenadas exatas (ROI) desses botões no settings.yaml
        has_fight = self._check_button(image, 'fight_button_roi')
        has_bag = self._check_button(image, 'bag_button_roi')
        has_pokemon = self._check_button(image, 'pokemon_button_roi')
        has_run = self._check_button(image, 'run_button_roi')

        # Se TODOS os 4 estiverem presentes, é combate
        if has_fight and has_bag and has_pokemon and has_run:
            
            # Verificação de SHINY (Crítica)
            if self._check_shiny(image):
                self._trigger_shiny_alarm()
                # Retorna um estado especial ou pausa o bot
                return GameState.PAUSED_SHINY 

            return GameState.IN_BATTLE
        
        # Se não, assumimos exploração
        return GameState.EXPLORING

    def _check_shiny(self, image):
        """
        Procura pelo 'S' dourado ou ícone de estrela perto da barra de vida do oponente.
        Recomendo usar Template Matching aqui com uma imagem pequena do ícone Shiny.
        """
        # Exemplo hipotético usando template
        shiny_template = cv2.imread('images/shiny_icon.png')
        return self.image_processor.detect_objects(image, shiny_template, threshold=0.9)
        return False # Placeholder

    def _trigger_shiny_alarm(self):
        logger.critical("!!! SHINY DETECTADO !!! PAUSANDO BOT E TOCANDO ALARME")
        # Loop de alarme sonoro
        for _ in range(5):
            winsound.Beep(1000, 500) # Frequência 1000Hz, 500ms
            winsound.Beep(1500, 500)