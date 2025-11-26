from typing import Dict, List
from loguru import logger
from ..knowledge.battle_rules import BattleRules
from ..knowledge.pokemon_database import PokemonDatabase

class BattleStrategy:
    def __init__(self, config: dict):
        self.battle_rules = BattleRules()
        self.pokemon_db = PokemonDatabase()
        
        # Carrega os golpes do jogador da configuração
        # Exemplo esperado no YAML:
        # battle:
        #   my_moves:
        #     slot_1: "water"
        #     slot_2: "ice"
        #     slot_3: "normal"
        #     slot_4: "psychic"
        self.my_moves = config.get('battle', {}).get('my_moves', {})
        
        logger.info("BattleStrategy Avançada inicializada")

    def choose_action(self, battle_state: Dict) -> str:
        """
        Analisa o inimigo e escolhe o ataque com maior multiplicador de dano.
        """
        enemy_name = battle_state.get('enemy_pokemon')
        
        if not enemy_name:
            logger.warning("Nome do inimigo não identificado! Usando ataque padrão.")
            return 'attack_1'

        # 1. Descobrir Tipos do Inimigo (Via PokeAPI)
        enemy_types = self.pokemon_db.get_pokemon_types(enemy_name)
        logger.debug(f"Inimigo: {enemy_name} | Tipos: {enemy_types}")

        if not enemy_types:
            return 'attack_1'

        # 2. Calcular eficácia de cada um dos MEUS slots
        best_slot = 'attack_1'
        max_effectiveness = -1.0

        # Mapeia slots para nomes de ação
        slots_map = {
            'slot_1': 'attack_1',
            'slot_2': 'attack_2',
            'slot_3': 'attack_3',
            'slot_4': 'attack_4'
        }

        for slot_key, move_type in self.my_moves.items():
            if not move_type: continue
            
            # Calcula o multiplicador (ex: Água vs Fogo = 2.0)
            effectiveness = self.battle_rules.calculate_type_advantage([move_type], enemy_types)
            
            logger.debug(f"Slot {slot_key} ({move_type}) vs {enemy_name}: {effectiveness}x")
            
            if effectiveness > max_effectiveness:
                max_effectiveness = effectiveness
                best_slot = slots_map.get(slot_key, 'attack_1')

        # Lógica de decisão final
        if max_effectiveness == 0.0:
            logger.warning("Todos os ataques são imunes! Trocando Pokémon.")
            return 'switch'
            
        logger.info(f"Melhor ação calculada: {best_slot} (Eficácia: {max_effectiveness}x)")
        return best_slot