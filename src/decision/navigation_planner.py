"""
Módulo para planejamento de navegação
"""
from typing import List, Tuple, Optional
from loguru import logger
from ..knowledge.map_data import MapData


class NavigationPlanner:
    """Classe para planejar rotas de navegação"""
    
    def __init__(self):
        """Inicializa o planejador de navegação"""
        self.map_data = MapData()
        self.current_path: List[Tuple[int, int]] = []
        
        logger.info("NavigationPlanner inicializado")
    
    def plan_route(self, start: Tuple[int, int], 
                   goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Planeja uma rota do ponto inicial ao objetivo
        
        Args:
            start: Posição inicial (x, y)
            goal: Posição objetivo (x, y)
            
        Returns:
            Lista de pontos da rota
        """
        # TODO: Implementar A* ou outro algoritmo de pathfinding
        # Por enquanto, retorna rota simples
        logger.info(f"Planejando rota de {start} para {goal}")
        return [start, goal]
    
    def get_next_direction(self, current_pos: Tuple[int, int],
                          target_pos: Tuple[int, int]) -> Optional[str]:
        """
        Retorna a próxima direção para seguir
        
        Args:
            current_pos: Posição atual (x, y)
            target_pos: Posição alvo (x, y)
            
        Returns:
            Direção ('up', 'down', 'left', 'right') ou None
        """
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        # Priorizar movimento horizontal
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'
    
    def explore_area(self, center: Tuple[int, int], 
                    radius: int = 50) -> List[Tuple[int, int]]:
        """
        Gera pontos para exploração de uma área
        
        Args:
            center: Centro da área (x, y)
            radius: Raio de exploração
            
        Returns:
            Lista de pontos para explorar
        """
        points = []
        # Gerar pontos em espiral
        for r in range(0, radius, 10):
            for angle in range(0, 360, 45):
                import math
                x = center[0] + int(r * math.cos(math.radians(angle)))
                y = center[1] + int(r * math.sin(math.radians(angle)))
                points.append((x, y))
        
        return points

