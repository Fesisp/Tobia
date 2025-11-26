"""
Controlador principal do bot
"""
import time
import os
from typing import Optional
from datetime import datetime
import cv2
from loguru import logger
from ..perception.screen_capture import ScreenCapture
from ..perception.game_state_detector import GameStateDetector, GameState
from ..action.input_simulator import InputSimulator
from ..action.battle_controller import BattleController
from ..action.navigation_controller import NavigationController
from ..action.capture_controller import CaptureController
from ..action.quest_controller import QuestController
from ..decision.decision_engine import DecisionEngine
from .state_machine import StateMachine, BotState


class BotController:
    """Classe principal que controla o bot"""
    
    def __init__(self, config: dict):
        """
        Inicializa o bot
        
        Args:
            config: Dicionário com configurações
        """
        self.config = config
        self.running = False
        
        # Inicializar componentes
        region = config.get('screen', {}).get('region')
        self.screen_capture = ScreenCapture(region)
        
        # Configurar OCR
        ocr_config = config.get('ocr', {})
        self.state_detector = GameStateDetector(self.screen_capture, ocr_config=ocr_config)
        
        # Configurar simulador de entrada
        security = config.get('security', {})
        self.input_simulator = InputSimulator(
            human_like=security.get('human_patterns', True),
            min_delay=security.get('min_delay', 0.05),
            max_delay=security.get('max_delay', 0.3)
        )
        
        # Inicializar controladores
        battle_config = config.get('battle', {})
        battle_strategy = battle_config.get('strategy', 'balanced')
        battle_cooldown = battle_config.get('action_cooldown', 3.0)
        self.battle_controller = BattleController(
            self.input_simulator,
            self.state_detector,
            battle_strategy,
            action_cooldown=battle_cooldown
        )
        
        self.navigation_controller = NavigationController(
            self.input_simulator,
            self.state_detector
        )
        
        capture_config = config.get('capture', {})
        self.capture_controller = CaptureController(
            self.input_simulator,
            self.state_detector,
            min_iv_threshold=capture_config.get('min_iv_threshold', 0),
            preferred_pokemon=capture_config.get('preferred_pokemon', [])
        )
        
        # Inicializar controlador de quests
        quest_config = config.get('quests', {})
        quest_check_interval = quest_config.get('check_interval', 5.0)
        self.quest_controller = QuestController(
            self.input_simulator,
            self.state_detector,
            self.screen_capture,
            ocr_config=ocr_config
        )
        self.quest_controller.quest_check_interval = quest_check_interval
        
        # Inicializar motor de decisão
        self.decision_engine = DecisionEngine(battle_strategy)
        
        # Inicializar máquina de estados
        self.state_machine = StateMachine()
        self._setup_state_handlers()

        # Debug options
        debug_cfg = config.get('debug', {}) if isinstance(config, dict) else {}
        self.debug_capture = debug_cfg.get('capture_on_battle', False)
        if self.debug_capture:
            # criar pasta para screenshots de debug
            try:
                os.makedirs('logs/screenshots', exist_ok=True)
            except Exception:
                pass
        
        logger.info("BotController inicializado")
    
    def _setup_state_handlers(self):
        """Configura handlers para cada estado"""
        self.state_machine.register_handler(BotState.EXPLORING, self._handle_exploring)
        self.state_machine.register_handler(BotState.BATTLING, self._handle_battling)
        self.state_machine.register_handler(BotState.CAPTURING, self._handle_capturing)
        self.state_machine.register_handler(BotState.WAITING, self._handle_waiting)
        self.state_machine.register_handler(BotState.IDLE, self._handle_idle)
        self.state_machine.register_handler(BotState.ERROR, self._handle_error)
    
    def start(self):
        """Inicia o bot"""
        if self.running:
            logger.warning("Bot já está em execução")
            return
        
        self.running = True
        logger.info("Bot iniciado")
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("Bot interrompido pelo usuário")
            self.stop()
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}", exc_info=True)
            self.stop()
    
    def stop(self):
        """Para o bot"""
        self.running = False
        logger.info("Bot parado")
    
    def _main_loop(self):
        """Loop principal do bot"""
        fps = self.config.get('screen', {}).get('fps', 10)
        frame_time = 1.0 / fps
        
        logger.info("Iniciando loop principal do bot...")
        logger.info("DICA: Se o bot ficar travado, execute 'python stop_bot.py' em outro terminal")
        
        while self.running:
            start_time = time.time()
            
            try:
                # Capturar e analisar estado
                screenshot = self.screen_capture.capture()
                if screenshot is None:
                    time.sleep(frame_time)
                    continue
                
                state = self.state_detector.detect_state(screenshot)
                state_info = self.state_detector.get_state_info(screenshot)
                
                # Atualizar informações de quest
                self.quest_controller.update_quest(screenshot)
                
                # Atualizar máquina de estados
                self.state_machine.update(state, state_info)

                # Debug: salvar screenshot quando detectar batalha
                try:
                    if self.debug_capture and state == GameState.IN_BATTLE:
                        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                        path = os.path.join('logs', 'screenshots', f'battle_{ts}.png')
                        cv2.imwrite(path, screenshot)
                        logger.info(f"Debug: screenshot salva em {path}")
                except Exception:
                    logger.exception("Erro ao salvar screenshot de debug")
                
            except KeyboardInterrupt:
                logger.info("Interrupção detectada, parando bot...")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}", exc_info=True)
                time.sleep(1.0)
            
            # Controlar FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)
    
    def _handle_exploring(self, state_info: dict):
        """Handler para estado de exploração"""
        # Verificar se deve seguir quests automaticamente
        if self.config.get('quests', {}).get('auto_follow', True):
            # Verificar se há uma quest ativa e seguir seu objetivo
            if self.quest_controller.is_following_quest():
                # Capturar screenshot para análise
                screenshot = self.screen_capture.capture()
                if screenshot is not None:
                    # Tentar seguir objetivo da quest
                    if self.quest_controller.follow_quest_objective(screenshot):
                        logger.info("Seguindo objetivo da quest")
                        return
        
        # Se não há quest ou não conseguiu seguir, fazer exploração normal
        if self.config.get('navigation', {}).get('human_like_movement', True):
            self.navigation_controller.random_exploration(1.0)
    
    def _handle_battling(self, state_info: dict):
        """Handler para estado de batalha"""
        if self.config.get('battle', {}).get('auto_battle', True):
            # Verificar novamente se realmente está em batalha antes de executar
            current_state = self.state_detector.detect_state()
            if current_state == GameState.IN_BATTLE:
                self.battle_controller.execute_battle_turn(state_info)
            else:
                logger.debug("Estado mudou, não está mais em batalha")
    
    def _handle_capturing(self, state_info: dict):
        """Handler para estado de captura"""
        if self.config.get('capture', {}).get('auto_capture', True):
            self.capture_controller.handle_encounter(state_info)
    
    def _handle_waiting(self, state_info: dict):
        """Handler para estado de espera"""
        # Pressionar espaço para avançar diálogos/menus
        self.input_simulator.press_key('space')
        time.sleep(0.5)
    
    def _handle_idle(self, state_info: dict):
        """Handler para estado idle"""
        # Não fazer nada, aguardar mudança de estado
        time.sleep(0.1)
    
    def _handle_error(self, state_info: dict):
        """Handler para estado de erro"""
        logger.error("Bot em estado de erro, tentando recuperar...")
        # Tentar voltar ao estado de exploração
        self.state_machine.transition_to(BotState.IDLE)
        time.sleep(1.0)

