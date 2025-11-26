"""
Módulo principal de tomada de decisão
"""
from typing import Dict, Optional
from loguru import logger
from .battle_strategy import BattleStrategy
from .navigation_planner import NavigationPlanner
from ..perception.game_state_detector import GameState, GameStateDetector


class DecisionEngine:
    """Classe principal para tomada de decisões"""
    
    def __init__(self, strategy_type: str = "balanced"):
        """
        Inicializa o motor de decisão
        
        Args:
            strategy_type: Tipo de estratégia
        """
        self.battle_strategy = BattleStrategy(strategy_type)
        self.navigation_planner = NavigationPlanner()
        
        logger.info("DecisionEngine inicializado")
    
    def make_decision(self, state: GameState, state_info: Dict) -> Optional[str]:
        """
        Toma uma decisão baseada no estado atual
        
        Args:
            state: Estado atual do jogo
            state_info: Informações do estado
            
        Returns:
            Ação a ser executada ou None
        """
        if state == GameState.IN_BATTLE:
            return self._decide_battle_action(state_info)
        elif state == GameState.EXPLORING:
            return self._decide_exploration_action(state_info)
        elif state == GameState.POKEMON_ENCOUNTER:
            return self._decide_capture_action(state_info)
        elif state == GameState.DIALOG:
            return 'skip_dialog'
        elif state == GameState.MENU:
            return 'close_menu'
        
        return None
    
    def _decide_battle_action(self, state_info: Dict) -> str:
        """Decide ação em batalha"""
        action = self.battle_strategy.choose_action(state_info)
        logger.debug(f"Ação de batalha decidida: {action}")
        return action
    
    def _decide_exploration_action(self, state_info: Dict) -> str:
        """Decide ação de exploração"""
        # Por enquanto, exploração aleatória
        # TODO: Implementar planejamento de rota
        return 'explore'
    
    def _decide_capture_action(self, state_info: Dict) -> str:
        """Decide ação de captura"""
        # Sempre tenta capturar por enquanto
        # TODO: Implementar lógica baseada em IV, nível, etc.
        return 'capture'

