"""
Máquina de estados do bot
"""
from enum import Enum
from typing import Dict, Optional, Callable
from loguru import logger
from ..perception.game_state_detector import GameState


class BotState(Enum):
    """Estados internos do bot"""
    IDLE = "idle"
    EXPLORING = "exploring"
    BATTLING = "battling"
    CAPTURING = "capturing"
    NAVIGATING = "navigating"
    WAITING = "waiting"
    ERROR = "error"


class StateMachine:
    """Máquina de estados para controlar o fluxo do bot"""
    
    def __init__(self):
        """Inicializa a máquina de estados"""
        self.current_state = BotState.IDLE
        self.previous_state = None
        self.state_handlers: Dict[BotState, Callable] = {}
        self.transitions: Dict[BotState, list] = {}
        
        self._setup_transitions()
        logger.info("StateMachine inicializado")
    
    def _setup_transitions(self):
        """Configura transições de estado permitidas"""
        self.transitions = {
            BotState.IDLE: [BotState.EXPLORING, BotState.BATTLING, BotState.CAPTURING, BotState.ERROR],
            BotState.EXPLORING: [BotState.BATTLING, BotState.CAPTURING, BotState.NAVIGATING, BotState.IDLE, BotState.ERROR],
            BotState.BATTLING: [BotState.EXPLORING, BotState.IDLE, BotState.WAITING, BotState.ERROR],
            BotState.CAPTURING: [BotState.EXPLORING, BotState.IDLE, BotState.ERROR],
            BotState.NAVIGATING: [BotState.EXPLORING, BotState.IDLE, BotState.ERROR],
            BotState.WAITING: [BotState.EXPLORING, BotState.BATTLING, BotState.IDLE, BotState.ERROR],
            BotState.ERROR: [BotState.IDLE, BotState.EXPLORING]
        }
    
    def register_handler(self, state: BotState, handler: Callable):
        """
        Registra um handler para um estado
        
        Args:
            state: Estado
            handler: Função handler
        """
        self.state_handlers[state] = handler
        logger.debug(f"Handler registrado para estado: {state}")
    
    def transition_to(self, new_state: BotState) -> bool:
        """
        Transiciona para um novo estado
        
        Args:
            new_state: Novo estado
            
        Returns:
            True se a transição foi bem-sucedida
        """
        if new_state in self.transitions.get(self.current_state, []):
            self.previous_state = self.current_state
            self.current_state = new_state
            logger.info(f"Transição: {self.previous_state.value} -> {self.current_state.value}")
            return True
        else:
            logger.warning(f"Transição inválida: {self.current_state.value} -> {new_state.value}")
            return False
    
    def update(self, game_state: GameState, state_info: Dict):
        """
        Atualiza a máquina de estados baseado no estado do jogo
        
        Args:
            game_state: Estado atual do jogo
            state_info: Informações do estado
        """
        # Mapear estado do jogo para estado do bot
        bot_state = self._map_game_state_to_bot_state(game_state)
        
        if bot_state != self.current_state:
            self.transition_to(bot_state)
        
        # Executar handler do estado atual
        handler = self.state_handlers.get(self.current_state)
        if handler:
            try:
                handler(state_info)
            except Exception as e:
                logger.error(f"Erro no handler do estado {self.current_state.value}: {e}")
                self.transition_to(BotState.ERROR)
    
    def _map_game_state_to_bot_state(self, game_state: GameState) -> BotState:
        """
        Mapeia estado do jogo para estado do bot
        
        Args:
            game_state: Estado do jogo
            
        Returns:
            Estado do bot correspondente
        """
        mapping = {
            GameState.EXPLORING: BotState.EXPLORING,
            GameState.IN_BATTLE: BotState.BATTLING,
            GameState.POKEMON_ENCOUNTER: BotState.CAPTURING,
            GameState.DIALOG: BotState.WAITING,
            GameState.MENU: BotState.WAITING,
            GameState.LOADING: BotState.WAITING,
            GameState.UNKNOWN: BotState.IDLE
        }
        
        return mapping.get(game_state, BotState.IDLE)
    
    def get_current_state(self) -> BotState:
        """Retorna o estado atual"""
        return self.current_state
    
    def reset(self):
        """Reseta a máquina de estados"""
        self.previous_state = None
        self.current_state = BotState.IDLE
        logger.info("StateMachine resetado")

