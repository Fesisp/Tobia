"""
Módulo para controlar captura de Pokémon
"""
import time
from typing import Dict, Optional
from loguru import logger
from .input_simulator import InputSimulator
from ..perception.game_state_detector import GameStateDetector, GameState


class CaptureController:
    """Classe para controlar captura de Pokémon"""
    
    def __init__(self, input_simulator: InputSimulator,
                 state_detector: GameStateDetector,
                 min_iv_threshold: int = 0,
                 preferred_pokemon: Optional[list] = None):
        """
        Inicializa o controlador de captura
        
        Args:
            input_simulator: Instância do simulador de entrada
            state_detector: Instância do detector de estado
            min_iv_threshold: IV mínimo para capturar (0-31)
            preferred_pokemon: Lista de Pokémon preferidos para capturar
        """
        self.input_simulator = input_simulator
        self.state_detector = state_detector
        self.min_iv_threshold = min_iv_threshold
        self.preferred_pokemon = preferred_pokemon or []
        self.last_capture_time = 0
        self.capture_cooldown = 2.0
        
        logger.info(f"CaptureController inicializado - IV mínimo: {min_iv_threshold}")
    
    def handle_encounter(self, encounter_info: Dict) -> bool:
        """
        Trata um encontro com Pokémon
        
        Args:
            encounter_info: Informações do encontro
            
        Returns:
            True se deve tentar capturar, False caso contrário
        """
        current_time = time.time()
        
        # Verificar cooldown
        if current_time - self.last_capture_time < self.capture_cooldown:
            return False
        
        pokemon_name = encounter_info.get('pokemon_name', '').lower()
        level = encounter_info.get('level', 0)
        
        # Verificar se é um Pokémon preferido
        if self.preferred_pokemon:
            if pokemon_name not in [p.lower() for p in self.preferred_pokemon]:
                logger.debug(f"Pokémon {pokemon_name} não está na lista de preferidos")
                return False
        
        # Decidir se deve capturar
        should_capture = self._should_capture(encounter_info)
        
        if should_capture:
            self._attempt_capture()
            self.last_capture_time = current_time
            return True
        
        return False
    
    def _should_capture(self, encounter_info: Dict) -> bool:
        """
        Decide se deve tentar capturar o Pokémon
        
        Args:
            encounter_info: Informações do encontro
            
        Returns:
            True se deve capturar
        """
        # Por enquanto, sempre tenta capturar se encontrou
        # TODO: Implementar lógica baseada em IV, nível, etc.
        return True
    
    def _attempt_capture(self):
        """Tenta capturar o Pokémon"""
        logger.info("Tentando capturar Pokémon...")
        
        # Pressionar espaço para iniciar captura
        self.input_simulator.press_key('space')
        time.sleep(0.5)
        
        # Selecionar Pokébola (geralmente a primeira)
        # TODO: Implementar seleção inteligente de bola
        self.input_simulator.press_key('enter')
        
        logger.info("Ação de captura executada")
    
    def use_best_ball(self, pokemon_info: Dict):
        """
        Usa a melhor Pokébola disponível
        
        Args:
            pokemon_info: Informações do Pokémon
        """
        # TODO: Implementar lógica para escolher melhor bola
        # Baseado em: nível do Pokémon, tipo, HP restante, etc.
        logger.debug("Usando melhor Pokébola disponível")
        self.input_simulator.press_key('enter')  # Por enquanto, usa a primeira

