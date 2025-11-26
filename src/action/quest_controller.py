"""
Módulo para controlar quests e navegação até objetivos
"""
import time
from typing import Dict, Optional, Tuple
from loguru import logger
from .input_simulator import InputSimulator
from ..perception.game_state_detector import GameStateDetector
from ..perception.quest_detector import QuestDetector
from ..perception.screen_capture import ScreenCapture


class QuestController:
    """Classe para gerenciar quests e navegação até objetivos"""
    
    def __init__(self, input_simulator: InputSimulator,
                 state_detector: GameStateDetector,
                 screen_capture: ScreenCapture,
                 ocr_config: Optional[dict] = None):
        """
        Inicializa o controlador de quests
        
        Args:
            input_simulator: Instância do simulador de entrada
            state_detector: Instância do detector de estado
            screen_capture: Instância do capturador de tela
            ocr_config: Configurações de OCR (opcional)
        """
        self.input_simulator = input_simulator
        self.state_detector = state_detector
        self.quest_detector = QuestDetector(screen_capture, ocr_config=ocr_config)
        
        self.current_quest: Optional[Dict] = None
        self.last_quest_check = 0
        self.quest_check_interval = 5.0  # Verificar quests a cada 5 segundos
        self.following_quest = False
        
        logger.info("QuestController inicializado")
    
    def update_quest(self, image) -> bool:
        """
        Atualiza informações da quest atual
        
        Args:
            image: Imagem da tela
            
        Returns:
            True se encontrou uma quest ativa
        """
        current_time = time.time()
        
        # Verificar quest apenas periodicamente para não sobrecarregar
        if current_time - self.last_quest_check < self.quest_check_interval:
            return self.current_quest is not None
        
        quest_info = self.quest_detector.extract_active_quest(image)
        
        if quest_info:
            # Verificar se é uma quest nova
            if not self.current_quest or self.current_quest.get('title') != quest_info.get('title'):
                logger.info(f"Nova quest detectada: {quest_info.get('title', 'Unknown')}")
                self.following_quest = True
            
            self.current_quest = quest_info
            self.last_quest_check = current_time
            return True
        else:
            self.current_quest = None
            self.following_quest = False
            return False
    
    def follow_quest_objective(self, image) -> bool:
        """
        Tenta seguir o objetivo da quest atual
        
        Args:
            image: Imagem da tela
            
        Returns:
            True se executou uma ação para seguir a quest
        """
        if not self.current_quest:
            return False
        
        # Tentar usar o botão "Goto" se disponível
        if self.current_quest.get('has_goto_button', False):
            goto_button_pos = self.quest_detector.find_goto_button(image)
            if goto_button_pos:
                logger.info("Clicando no botão Goto da quest")
                self.input_simulator.click(goto_button_pos[0], goto_button_pos[1])
                time.sleep(1.0)  # Aguardar resposta do jogo
                return True
        
        # Se não tem botão Goto ou não encontrou, tentar navegação manual
        objective = self.current_quest.get('objective', '').lower()
        
        # Extrair localização do objetivo
        location = self._extract_location_from_objective(objective)
        if location:
            logger.info(f"Navegando para: {location}")
            # TODO: Implementar navegação até localização específica
            # Por enquanto, apenas loga
            return True
        
        return False
    
    def _extract_location_from_objective(self, objective: str) -> Optional[str]:
        """
        Extrai localização do objetivo da quest
        
        Args:
            objective: Texto do objetivo
            
        Returns:
            Nome da localização ou None
        """
        # Palavras-chave que indicam localizações
        location_keywords = {
            'pewter city': 'pewter_city',
            'pewter city gym': 'pewter_city_gym',
            'viridian city': 'viridian_city',
            'cerulean city': 'cerulean_city',
            'pallet town': 'pallet_town',
            'gym': 'gym',
            'pokemon center': 'pokemon_center',
            'pokemon center': 'pokemon_center',
        }
        
        objective_lower = objective.lower()
        
        for keyword, location in location_keywords.items():
            if keyword in objective_lower:
                return location
        
        return None
    
    def get_current_quest(self) -> Optional[Dict]:
        """
        Retorna informações da quest atual
        
        Returns:
            Dicionário com informações da quest ou None
        """
        return self.current_quest
    
    def is_following_quest(self) -> bool:
        """
        Verifica se está seguindo uma quest
        
        Returns:
            True se está seguindo uma quest
        """
        return self.following_quest and self.current_quest is not None

