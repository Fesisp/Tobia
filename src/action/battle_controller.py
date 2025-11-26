"""
Módulo para controlar batalhas
"""
import time
from typing import Dict, Optional
from loguru import logger
from .input_simulator import InputSimulator
from ..perception.game_state_detector import GameStateDetector, GameState


class BattleController:
    """Classe para controlar batalhas"""
    
    def __init__(self, input_simulator: InputSimulator, 
                 state_detector: GameStateDetector,
                 strategy: str = "balanced",
                 action_cooldown: float = 3.0):
        """
        Inicializa o controlador de batalha
        
        Args:
            input_simulator: Instância do simulador de entrada
            state_detector: Instância do detector de estado
            strategy: Estratégia de batalha ('aggressive', 'defensive', 'balanced')
            action_cooldown: Cooldown entre ações em segundos
        """
        self.input_simulator = input_simulator
        self.state_detector = state_detector
        self.strategy = strategy
        self.last_action_time = 0
        self.action_cooldown = action_cooldown
        self.consecutive_actions = 0  # Contador de ações consecutivas
        self.max_consecutive_actions = 10  # Máximo de ações antes de verificar novamente
        
        logger.info(f"BattleController inicializado - Estratégia: {strategy}, Cooldown: {action_cooldown}s")
    
    def execute_battle_turn(self, battle_info: Dict) -> bool:
        """
        Executa um turno de batalha
        
        Args:
            battle_info: Informações da batalha atual
            
        Returns:
            True se a batalha continua, False se terminou
        """
        current_time = time.time()
        
        # Verificar cooldown
        if current_time - self.last_action_time < self.action_cooldown:
            return True
        
        # Verificação dupla: confirmar que realmente está em batalha
        detected_state = self.state_detector.detect_state()
        if detected_state != GameState.IN_BATTLE:
            # Se não está mais em batalha, resetar contador
            self.consecutive_actions = 0
            return False
        
        # Verificação de segurança: se executou muitas ações consecutivas, verificar novamente
        if self.consecutive_actions >= self.max_consecutive_actions:
            logger.warning("Muitas ações consecutivas, verificando estado novamente...")
            # Verificar estado novamente após pequeno delay
            time.sleep(0.5)
            detected_state = self.state_detector.detect_state()
            if detected_state != GameState.IN_BATTLE:
                logger.info("Não está mais em batalha, parando ações")
                self.consecutive_actions = 0
                return False
            self.consecutive_actions = 0  # Resetar contador
        
        # Decidir ação baseado na estratégia
        action = self._decide_action(battle_info)
        
        # Executar ação
        self._execute_action(action)
        
        self.last_action_time = current_time
        self.consecutive_actions += 1
        return True
    
    def _decide_action(self, battle_info: Dict) -> str:
        """
        Decide qual ação tomar na batalha
        
        Args:
            battle_info: Informações da batalha
            
        Returns:
            Ação a ser executada ('attack_1', 'attack_2', 'attack_3', 'attack_4', 'switch', 'item', 'run')
        """
        # Obter valores de HP, tratando None
        my_hp = battle_info.get('my_hp')
        my_max_hp = battle_info.get('my_max_hp')
        enemy_hp = battle_info.get('enemy_hp')
        enemy_max_hp = battle_info.get('enemy_max_hp')
        
        # Se não conseguiu extrair HP, usar valores padrão
        if my_hp is None:
            my_hp = 100
        if my_max_hp is None or my_max_hp == 0:
            my_max_hp = 100
        if enemy_hp is None:
            enemy_hp = 100
        if enemy_max_hp is None or enemy_max_hp == 0:
            enemy_max_hp = 100
        
        # Calcular porcentagem de HP
        my_hp_percent = (my_hp / my_max_hp * 100) if my_max_hp > 0 else 100
        enemy_hp_percent = (enemy_hp / enemy_max_hp * 100) if enemy_max_hp > 0 else 100
        
        # Estratégia agressiva
        if self.strategy == "aggressive":
            # Sempre atacar, usar o ataque mais forte disponível
            if enemy_hp_percent > 50:
                return 'attack_1'  # Ataque mais forte
            else:
                return 'attack_2'  # Ataque secundário
        
        # Estratégia defensiva
        elif self.strategy == "defensive":
            # Trocar se HP muito baixo
            if my_hp_percent < 30:
                return 'switch'
            # Usar item se HP baixo
            elif my_hp_percent < 50:
                return 'item'
            # Atacar normalmente
            else:
                return 'attack_1'
        
        # Estratégia balanceada (padrão)
        else:
            # Trocar se HP muito baixo
            if my_hp_percent < 20:
                return 'switch'
            # Atacar com força baseado no HP do inimigo
            elif enemy_hp_percent > 70:
                return 'attack_1'  # Ataque forte
            elif enemy_hp_percent > 30:
                return 'attack_2'  # Ataque médio
            else:
                return 'attack_3'  # Ataque fraco para economizar PP
    
    def _execute_action(self, action: str):
        """
        Executa uma ação na batalha
        
        Args:
            action: Ação a executar
        """
        action_map = {
            'attack_1': '1',
            'attack_2': '2',
            'attack_3': '3',
            'attack_4': '4',
            'switch': 's',
            'item': 'i',
            'run': 'r'
        }
        
        key = action_map.get(action, '1')
        self.input_simulator.press_key(key)
        logger.info(f"Ação de batalha executada: {action}")
    
    def wait_for_battle_end(self, timeout: float = 30.0) -> bool:
        """
        Aguarda o fim da batalha
        
        Args:
            timeout: Tempo máximo de espera em segundos
            
        Returns:
            True se a batalha terminou, False se timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            state = self.state_detector.detect_state()
            if state != GameState.IN_BATTLE:
                return True
            time.sleep(0.5)
        return False

