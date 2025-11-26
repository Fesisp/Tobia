# ... imports ...
from ..perception.game_state_detector import GameState

class QuestController:
    def __init__(self, input_simulator, state_detector, screen_capture, ocr_config=None):
        self.input_simulator = input_simulator
        self.state_detector = state_detector # Precisamos disso para verificar combate
        # ... resto do init ...

    def follow_quest_objective(self, image) -> bool:
        """
        Tenta seguir a quest, MAS APENAS se estiver seguro (fora de combate).
        """
        # 1. Verificação de Segurança Crítica
        current_state = self.state_detector.detect_state(image)
        if current_state == GameState.IN_BATTLE:
            logger.debug("Em batalha! Ignorando botão Goto.")
            return False

        # 2. Busca e Clique no Goto
        goto_button_pos = self.quest_detector.find_goto_button(image)
        
        if goto_button_pos:
            logger.info("Botão Goto disponível e seguro. Clicando...")
            self.input_simulator.click(goto_button_pos[0], goto_button_pos[1])
            time.sleep(1.0)
            return True
            
        return False