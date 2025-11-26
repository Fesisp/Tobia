"""
Regras e mecânicas de batalha
"""
from typing import List
from loguru import logger


class BattleRules:
    """Classe para regras de batalha"""
    
    def __init__(self):
        """Inicializa as regras de batalha"""
        # Matriz de vantagens de tipo (simplificada)
        self.type_chart = {
            "normal": {"rock": 0.5, "ghost": 0.0},
            "fire": {"water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0, "rock": 0.5, "dragon": 0.5},
            "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "rock": 2.0, "dragon": 0.5},
            "electric": {"water": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0, "flying": 2.0, "dragon": 0.5},
            "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5, "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0, "dragon": 0.5},
            "ice": {"water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0, "flying": 2.0, "dragon": 2.0},
            "fighting": {"normal": 2.0, "ice": 2.0, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2.0, "ghost": 0.0, "dark": 2.0},
            "poison": {"grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5},
            "ground": {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0, "flying": 0.0, "bug": 0.5, "rock": 2.0},
            "flying": {"electric": 0.5, "grass": 2.0, "fighting": 2.0, "bug": 2.0, "rock": 0.5},
            "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0},
            "bug": {"fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0},
            "rock": {"fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5, "flying": 2.0, "bug": 2.0},
            "ghost": {"normal": 0.0, "psychic": 2.0, "ghost": 2.0, "dark": 0.5},
            "dragon": {"dragon": 2.0},
            "dark": {"psychic": 2.0, "ghost": 2.0, "dark": 0.5},
            "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0, "rock": 2.0, "steel": 0.5}
        }
        
        logger.info("BattleRules inicializado")
    
    def calculate_type_advantage(self, attacker_types: List[str], 
                                defender_types: List[str]) -> float:
        """
        Calcula a vantagem de tipo
        
        Args:
            attacker_types: Tipos do atacante
            defender_types: Tipos do defensor
            
        Returns:
            Multiplicador de dano (1.0 = neutro, 2.0 = super efetivo, 0.5 = não muito efetivo, 0.0 = sem efeito)
        """
        if not attacker_types or not defender_types:
            return 1.0
        
        total_multiplier = 1.0
        
        for attacker_type in attacker_types:
            attacker_type = attacker_type.lower()
            type_advantages = self.type_chart.get(attacker_type, {})
            
            for defender_type in defender_types:
                defender_type = defender_type.lower()
                multiplier = type_advantages.get(defender_type, 1.0)
                total_multiplier *= multiplier
        
        return total_multiplier
    
    def is_super_effective(self, attacker_types: List[str],
                          defender_types: List[str]) -> bool:
        """
        Verifica se o ataque é super efetivo
        
        Args:
            attacker_types: Tipos do atacante
            defender_types: Tipos do defensor
            
        Returns:
            True se super efetivo
        """
        return self.calculate_type_advantage(attacker_types, defender_types) > 1.0
    
    def is_not_very_effective(self, attacker_types: List[str],
                             defender_types: List[str]) -> bool:
        """
        Verifica se o ataque não é muito efetivo
        
        Args:
            attacker_types: Tipos do atacante
            defender_types: Tipos do defensor
            
        Returns:
            True se não muito efetivo
        """
        multiplier = self.calculate_type_advantage(attacker_types, defender_types)
        return 0.0 < multiplier < 1.0
    
    def has_no_effect(self, attacker_types: List[str],
                     defender_types: List[str]) -> bool:
        """
        Verifica se o ataque não tem efeito
        
        Args:
            attacker_types: Tipos do atacante
            defender_types: Tipos do defensor
            
        Returns:
            True se sem efeito
        """
        return self.calculate_type_advantage(attacker_types, defender_types) == 0.0

