"""
Módulo para controlar navegação no jogo
"""
import random
import time
from typing import List, Tuple, Optional
from loguru import logger
from .input_simulator import InputSimulator
from ..perception.game_state_detector import GameStateDetector


class NavigationController:
    """Classe para controlar navegação"""
    
    def __init__(self, input_simulator: InputSimulator,
                 state_detector: GameStateDetector):
        """
        Inicializa o controlador de navegação
        
        Args:
            input_simulator: Instância do simulador de entrada
            state_detector: Instância do detector de estado
        """
        self.input_simulator = input_simulator
        self.state_detector = state_detector
        self.current_path: List[Tuple[int, int]] = []
        self.last_direction = None
        self.direction_change_time = 0
        self.min_direction_duration = 1.0  # Mínimo de tempo na mesma direção
        
        logger.info("NavigationController inicializado")
    
    def move_to_position(self, target: Tuple[int, int], 
                        current: Optional[Tuple[int, int]] = None):
        """
        Move para uma posição específica
        
        Args:
            target: Posição alvo (x, y)
            current: Posição atual (se conhecida)
        """
        # TODO: Implementar pathfinding
        # Por enquanto, movimento aleatório
        self.random_exploration()
    
    def random_exploration(self, duration: float = 2.0):
        """
        Exploração aleatória
        
        Args:
            duration: Duração da exploração em segundos
        """
        current_time = time.time()
        
        # Mudar direção apenas se passou tempo suficiente
        if (current_time - self.direction_change_time) < self.min_direction_duration:
            # Continuar na mesma direção
            if self.last_direction:
                self.input_simulator.move(self.last_direction, duration)
            return
        
        directions = ['up', 'down', 'left', 'right']
        
        # Evitar mudança brusca de direção (virar 180 graus)
        if self.last_direction:
            opposite = {
                'up': 'down',
                'down': 'up',
                'left': 'right',
                'right': 'left'
            }
            directions = [d for d in directions if d != opposite.get(self.last_direction)]
        
        direction = random.choice(directions)
        self.last_direction = direction
        self.direction_change_time = current_time
        
        self.input_simulator.move(direction, duration)
        logger.debug(f"Movimento aleatório: {direction}")
    
    def follow_path(self, path: List[Tuple[int, int]]):
        """
        Segue um caminho pré-definido
        
        Args:
            path: Lista de posições (x, y)
        """
        self.current_path = path
        # TODO: Implementar seguimento de caminho
        logger.info(f"Seguindo caminho com {len(path)} pontos")
    
    def avoid_obstacle(self):
        """Evita um obstáculo detectado"""
        # Mudar direção aleatoriamente, mas não voltar
        directions = ['up', 'down', 'left', 'right']
        if self.last_direction:
            opposite = {
                'up': 'down',
                'down': 'up',
                'left': 'right',
                'right': 'left'
            }
            directions = [d for d in directions if d != opposite.get(self.last_direction)]
        
        direction = random.choice(directions)
        self.last_direction = direction
        self.input_simulator.move(direction, 0.5)
        logger.debug("Evitando obstáculo")
    
    def move_in_direction(self, direction: str, duration: float = 1.0):
        """
        Move em uma direção específica
        
        Args:
            direction: Direção ('up', 'down', 'left', 'right')
            duration: Duração do movimento
        """
        self.last_direction = direction
        self.direction_change_time = time.time()
        self.input_simulator.move(direction, duration)
        logger.debug(f"Movimento direcionado: {direction}")

