"""
Módulo para estratégias de batalha
"""
from typing import Dict, List, Optional
from loguru import logger
from ..knowledge.battle_rules import BattleRules
from ..knowledge.pokemon_database import PokemonDatabase


class BattleStrategy:
    """Classe para estratégias de batalha"""
    
    def __init__(self, strategy_type: str = "balanced"):
        """
        Inicializa a estratégia de batalha
        
        Args:
            strategy_type: Tipo de estratégia ('aggressive', 'defensive', 'balanced')
        """
        self.strategy_type = strategy_type
        self.battle_rules = BattleRules()
        self.pokemon_db = PokemonDatabase()
        
        logger.info(f"BattleStrategy inicializado - Tipo: {strategy_type}")
    
    def choose_action(self, battle_state: Dict) -> str:
        """
        Escolhe a melhor ação baseado no estado da batalha
        
        Args:
            battle_state: Estado atual da batalha
            
        Returns:
            Ação escolhida
        """
        my_pokemon = battle_state.get('my_pokemon')
        enemy_pokemon = battle_state.get('enemy_pokemon')
        
        # Obter valores de HP, tratando None
        my_hp = battle_state.get('my_hp')
        my_max_hp = battle_state.get('my_max_hp')
        enemy_hp = battle_state.get('enemy_hp')
        enemy_max_hp = battle_state.get('enemy_max_hp')
        
        # Se não conseguiu extrair HP, usar valores padrão
        if my_hp is None:
            my_hp = 100
        if my_max_hp is None or my_max_hp == 0:
            my_max_hp = 100
        if enemy_hp is None:
            enemy_hp = 100
        if enemy_max_hp is None or enemy_max_hp == 0:
            enemy_max_hp = 100
        
        my_hp_percent = (my_hp / my_max_hp * 100) if my_max_hp > 0 else 100
        enemy_hp_percent = (enemy_hp / enemy_max_hp * 100) if enemy_max_hp > 0 else 100
        
        # Obter informações dos Pokémon
        my_pokemon_info = self.pokemon_db.get_pokemon_info(my_pokemon) if my_pokemon else None
        enemy_pokemon_info = self.pokemon_db.get_pokemon_info(enemy_pokemon) if enemy_pokemon else None
        
        # Calcular vantagem de tipo
        type_advantage = 1.0
        if my_pokemon_info and enemy_pokemon_info:
            type_advantage = self.battle_rules.calculate_type_advantage(
                my_pokemon_info.get('types', []),
                enemy_pokemon_info.get('types', [])
            )
        
        # Aplicar estratégia
        if self.strategy_type == "aggressive":
            return self._aggressive_strategy(my_hp_percent, enemy_hp_percent, type_advantage)
        elif self.strategy_type == "defensive":
            return self._defensive_strategy(my_hp_percent, enemy_hp_percent, type_advantage)
        else:
            return self._balanced_strategy(my_hp_percent, enemy_hp_percent, type_advantage)
    
    def _aggressive_strategy(self, my_hp: float, enemy_hp: float, 
                            type_advantage: float) -> str:
        """Estratégia agressiva"""
        # Trocar apenas se HP muito baixo
        if my_hp < 15:
            return 'switch'
        
        # Usar ataque mais forte se tiver vantagem de tipo
        if type_advantage > 1.5:
            return 'attack_1'
        elif type_advantage > 1.0:
            return 'attack_2'
        else:
            return 'attack_1'
    
    def _defensive_strategy(self, my_hp: float, enemy_hp: float,
                           type_advantage: float) -> str:
        """Estratégia defensiva"""
        # Trocar se HP baixo
        if my_hp < 30:
            return 'switch'
        
        # Usar item se HP médio
        if my_hp < 60:
            return 'item'
        
        # Atacar com cuidado
        return 'attack_2'
    
    def _balanced_strategy(self, my_hp: float, enemy_hp: float,
                         type_advantage: float) -> str:
        """Estratégia balanceada"""
        # Trocar se HP muito baixo
        if my_hp < 20:
            return 'switch'
        
        # Se inimigo está fraco, usar ataque fraco para economizar PP
        if enemy_hp < 20:
            return 'attack_4'
        
        # Se tem vantagem, usar ataque forte
        if type_advantage > 1.2:
            return 'attack_1'
        
        # Caso padrão, usar ataque médio
        return 'attack_2'
    
    def should_switch_pokemon(self, battle_state: Dict) -> bool:
        """
        Decide se deve trocar de Pokémon
        
        Args:
            battle_state: Estado atual da batalha
            
        Returns:
            True se deve trocar
        """
        my_hp = battle_state.get('my_hp', 0)
        my_max_hp = battle_state.get('my_max_hp', 100)
        my_hp_percent = (my_hp / my_max_hp * 100) if my_max_hp > 0 else 100
        
        # Trocar se HP muito baixo
        threshold = 25 if self.strategy_type == "defensive" else 20
        return my_hp_percent < threshold

