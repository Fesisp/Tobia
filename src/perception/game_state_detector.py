"""
Módulo para detectar o estado atual do jogo
"""
import cv2
import numpy as np
from typing import Dict, Optional
from enum import Enum
from loguru import logger
from .image_processing import ImageProcessor
from .screen_capture import ScreenCapture
from .ocr_engine import OCREngine


class GameState(Enum):
    """Estados possíveis do jogo"""
    UNKNOWN = "unknown"
    MENU = "menu"
    EXPLORING = "exploring"
    IN_BATTLE = "in_battle"
    POKEMON_ENCOUNTER = "pokemon_encounter"
    DIALOG = "dialog"
    INVENTORY = "inventory"
    POKEMON_CENTER = "pokemon_center"
    SHOP = "shop"
    LOADING = "loading"


class GameStateDetector:
    """Classe para detectar o estado atual do jogo"""
    
    def __init__(self, screen_capture: ScreenCapture, ocr_config: Optional[dict] = None):
        """
        Inicializa o detector de estado
        
        Args:
            screen_capture: Instância do capturador de tela
            ocr_config: Configurações de OCR (opcional)
        """
        self.screen_capture = screen_capture
        self.image_processor = ImageProcessor()
        
        # Configurar OCR com as configurações fornecidas
        ocr_config = ocr_config or {}
        tesseract_path = ocr_config.get('tesseract_path')
        use_easyocr = ocr_config.get('use_easyocr', False)
        self.ocr_engine = OCREngine(use_easyocr=use_easyocr, tesseract_path=tesseract_path)
        
        self.current_state = GameState.UNKNOWN

        # Contadores para confirmação temporal de detecção de batalha
        self._battle_confirmation_counter = 0
        # Número de frames consecutivos necessários para confirmar batalha
        self._battle_confirmation_threshold = 2
        
        # Templates para detecção (carregar de arquivos)
        self.templates = {}
        self._load_templates()
        
        # Cache de estado para evitar detecções repetidas
        self.state_cache = {}
        self.cache_duration = 0.5  # segundos
        
        logger.info("GameStateDetector inicializado")
    
    def _load_templates(self):
        """Carrega templates de imagem para detecção"""
        # TODO: Carregar templates de arquivos
        # Exemplo: 
        # template_path = Path("data/templates/battle_ui.png")
        # if template_path.exists():
        #     self.templates['battle'] = cv2.imread(str(template_path))
        pass
    
    def detect_state(self, image: Optional[np.ndarray] = None) -> GameState:
        """
        Detecta o estado atual do jogo
        
        Args:
            image: Imagem para analisar (se None, captura nova)
            
        Returns:
            Estado detectado do jogo
        """
        if image is None:
            image = self.screen_capture.capture()
        
        if image is None:
            return GameState.UNKNOWN
        
        # Detectar estado de batalha (com confirmação temporal)
        in_battle_now = self._is_in_battle(image)
        if in_battle_now:
            self._battle_confirmation_counter += 1
        else:
            self._battle_confirmation_counter = 0

        if self._battle_confirmation_counter >= self._battle_confirmation_threshold:
            self.current_state = GameState.IN_BATTLE
            return GameState.IN_BATTLE
        
        # Detectar encontro com Pokémon
        if self._is_pokemon_encounter(image):
            self.current_state = GameState.POKEMON_ENCOUNTER
            return GameState.POKEMON_ENCOUNTER
        
        # Detectar diálogo
        if self._is_dialog(image):
            self.current_state = GameState.DIALOG
            return GameState.DIALOG
        
        # Detectar menu
        if self._is_menu(image):
            self.current_state = GameState.MENU
            return GameState.MENU
        
        # Detectar inventário
        if self._is_inventory(image):
            self.current_state = GameState.INVENTORY
            return GameState.INVENTORY
        
        # Estado padrão: explorando
        # (Se chegou aqui, não detectou nenhum dos estados específicos acima)
        self.current_state = GameState.EXPLORING
        return GameState.EXPLORING
    
    def _is_in_battle(self, image: np.ndarray) -> bool:
        """
        Verifica se está em batalha
        
        Características da tela de batalha:
        - Botão vermelho grande "Fight" no centro inferior
        - Botões de ação: "Pokémon" (azul), "Items" (amarelo), "Run" (verde)
        - Barras de HP no topo esquerdo e canto inferior direito
        - Texto "Lv." indicando níveis dos Pokémon
        - Dois Pokémon visíveis na tela
        """
        height, width = image.shape[:2]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Método 1: Detectar botão vermelho "Fight" grande na parte inferior central
        # Região do botão Fight (centro inferior)
        bottom_center_region = image[int(height * 0.75):int(height * 0.9), 
                                     int(width * 0.4):int(width * 0.6)]
        
        if bottom_center_region.size > 0:
            bottom_hsv = cv2.cvtColor(bottom_center_region, cv2.COLOR_BGR2HSV)
            
            # Procurar por vermelho (botão Fight)
            red_lower1 = np.array([0, 100, 100])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 100, 100])
            red_upper2 = np.array([180, 255, 255])
            red_mask1 = cv2.inRange(bottom_hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(bottom_hsv, red_lower2, red_upper2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            
            # Se encontrar muito vermelho na região do botão Fight, provavelmente está em batalha
            red_pixels = np.sum(red_mask)
            if red_pixels > 5000:  # Threshold para botão grande
                logger.debug("Botão Fight detectado - em batalha")
                return True
        
        # Método 2 (REMOVIDO como critério autônomo): Detectar múltiplas barras de HP (verde)
        # Observação: barras de HP podem aparecer também no HUD do jogador fora de batalha,
        # então não consideramos HP sozinho como prova suficiente. Mantemos a lógica
        # apenas para diagnóstico (log) e futuras combinações, mas não retornamos True aqui.
        top_left_region = image[0:int(height * 0.15), 0:int(width * 0.3)]
        bottom_right_region = image[int(height * 0.75):, int(width * 0.65):]
        green_lower = np.array([40, 80, 80])
        green_upper = np.array([80, 255, 255])
        hp_detections = 0
        if top_left_region.size > 0:
            top_hsv = cv2.cvtColor(top_left_region, cv2.COLOR_BGR2HSV)
            green_mask_top = cv2.inRange(top_hsv, green_lower, green_upper)
            if np.sum(green_mask_top) > 2000:
                hp_detections += 1
        if bottom_right_region.size > 0:
            bottom_hsv = cv2.cvtColor(bottom_right_region, cv2.COLOR_BGR2HSV)
            green_mask_bottom = cv2.inRange(bottom_hsv, green_lower, green_upper)
            if np.sum(green_mask_bottom) > 2000:
                hp_detections += 1
        if hp_detections >= 1:
            logger.debug(f"HP detections (diagnóstico) = {hp_detections} — não suficiente sozinho para batalha")
        
        # Método 3 (simplificado): Detectar presença de AO MENOS UM botão de ação na parte inferior
        # Botões: "Fight" (vermelho), "Pokémon" (azul), "Items" (amarelo), "Run" (verde)
        # Usar região mais restrita (centro inferior) para reduzir falsos positivos
        bottom_buttons_region = image[int(height * 0.82):int(height * 0.95), int(width * 0.35):int(width * 0.65)]

        if bottom_buttons_region.size > 0:
            buttons_hsv = cv2.cvtColor(bottom_buttons_region, cv2.COLOR_BGR2HSV)

            # Máscaras de cor para cada botão
            # Vermelho (Fight) pode ter dois intervalos no HSV
            red_lower1 = np.array([0, 120, 80])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 120, 80])
            red_upper2 = np.array([180, 255, 255])
            red_mask1 = cv2.inRange(buttons_hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(buttons_hsv, red_lower2, red_upper2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)

            # Azul (Pokémon)
            blue_lower = np.array([100, 120, 80])
            blue_upper = np.array([130, 255, 255])
            blue_mask = cv2.inRange(buttons_hsv, blue_lower, blue_upper)

            # Amarelo (Items)
            yellow_lower = np.array([18, 120, 80])
            yellow_upper = np.array([35, 255, 255])
            yellow_mask = cv2.inRange(buttons_hsv, yellow_lower, yellow_upper)

            # Verde (Run)
            green_mask_buttons = cv2.inRange(buttons_hsv, green_lower, green_upper)

            # Thresholds menores, queremos detectar ao menos UM botão
            if np.sum(red_mask) > 1500:
                logger.debug("Botão vermelho detectado (Fight) - em batalha")
                return True
            if np.sum(blue_mask) > 1500:
                logger.debug("Botão azul detectado (Pokémon) - em batalha")
                return True
            if np.sum(yellow_mask) > 1500:
                logger.debug("Botão amarelo detectado (Items) - em batalha")
                return True
            if np.sum(green_mask_buttons) > 1500:
                logger.debug("Botão verde detectado (Run) - em batalha")
                return True
        
        # Método 4: Detectar texto "Lv." usando OCR (indicador de níveis)
        # Regiões onde aparecem níveis: topo esquerdo e canto inferior direito
        level_regions = [
            (0, int(height * 0.1), int(width * 0.3), int(height * 0.05)),  # Topo esquerdo
            (int(width * 0.65), int(height * 0.75), int(width * 0.3), int(height * 0.1))  # Inferior direito
        ]
        
        level_detections = 0
        for x, y, w, h in level_regions:
            if x + w <= width and y + h <= height:
                level_roi = image[y:y+h, x:x+w]
                level_text = self.ocr_engine.extract_text(level_roi)
                if 'lv' in level_text.lower() or 'level' in level_text.lower():
                    level_detections += 1
        
        # Se encontrar níveis em múltiplas regiões, está em batalha
        if level_detections >= 1 and hp_detections >= 1:
            logger.debug("Níveis e HP detectados - em batalha")
            return True
        
        # Método 5: Detectar texto dos botões de batalha usando OCR
        # Região dos botões de ação (parte inferior central)
        buttons_text_region = image[int(height * 0.8):, int(width * 0.2):int(width * 0.8)]
        
        if buttons_text_region.size > 0:
            buttons_text = self.ocr_engine.extract_text(buttons_text_region)
            buttons_text_lower = buttons_text.lower()
            
            # Procurar por palavras-chave dos botões de batalha
            battle_keywords = ['fight', 'pokemon', 'items', 'run', 'pokémon']
            keyword_count = sum(1 for keyword in battle_keywords if keyword in buttons_text_lower)
            
            # Se encontrar pelo menos 2 palavras-chave de botões, está em batalha
            if keyword_count >= 2:
                logger.debug(f"Palavras-chave de batalha detectadas ({keyword_count}): {buttons_text_lower[:50]}")
                return True
        
        return False
    
    def _is_pokemon_encounter(self, image: np.ndarray) -> bool:
        """Verifica se encontrou um Pokémon selvagem"""
        # Detectar tela de encontro com Pokémon
        # Geralmente tem uma animação ou UI específica
        # Por enquanto, retorna False - precisa ser implementado com templates
        return False
    
    def _is_dialog(self, image: np.ndarray) -> bool:
        """Verifica se há um diálogo na tela"""
        # Detectar caixa de diálogo na parte inferior da tela
        height, width = image.shape[:2]
        bottom_region = image[int(height * 0.7):, :]
        
        # Caixas de diálogo geralmente têm fundo escuro/claro
        gray = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
        
        # Procurar por região com muito texto (muitas bordas)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Se houver muitas bordas na parte inferior, pode ser diálogo
        if edge_density > 0.1:
            return True
        
        return False
    
    def _is_menu(self, image: np.ndarray) -> bool:
        """Verifica se está em um menu"""
        # Detectar elementos de menu
        # Menus geralmente têm bordas ou elementos retangulares
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Procurar por retângulos grandes (menus)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:  # Threshold ajustável
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                # Menus geralmente têm aspect ratio próximo de 1
                if 0.5 < aspect_ratio < 2.0:
                    return True
        
        return False
    
    def _is_inventory(self, image: np.ndarray) -> bool:
        """Verifica se está no inventário"""
        # Similar ao menu, mas com elementos específicos
        # Por enquanto, usa detecção de menu
        return self._is_menu(image)
    
    def get_state_info(self, image: Optional[np.ndarray] = None) -> Dict:
        """
        Retorna informações detalhadas sobre o estado atual
        
        Args:
            image: Imagem para analisar
            
        Returns:
            Dicionário com informações do estado
        """
        state = self.detect_state(image)
        
        if image is None:
            image = self.screen_capture.capture()
        
        info = {
            "state": state.value,
            "timestamp": cv2.getTickCount() / cv2.getTickFrequency()
        }
        
        # Adicionar informações específicas por estado
        if state == GameState.IN_BATTLE:
            info.update(self._get_battle_info(image))
        elif state == GameState.POKEMON_ENCOUNTER:
            info.update(self._get_encounter_info(image))
        
        return info
    
    def _get_battle_info(self, image: np.ndarray) -> Dict:
        """Extrai informações da batalha"""
        # Tentar extrair HP usando OCR
        # As posições precisam ser ajustadas conforme a UI do jogo
        height, width = image.shape[:2]
        
        # Regiões aproximadas para barras de HP (ajustar conforme necessário)
        my_hp_region = (int(width * 0.1), int(height * 0.7), int(width * 0.3), int(height * 0.1))
        enemy_hp_region = (int(width * 0.6), int(height * 0.1), int(width * 0.3), int(height * 0.1))
        
        my_hp_info = self.ocr_engine.extract_hp_info(image, my_hp_region)
        enemy_hp_info = self.ocr_engine.extract_hp_info(image, enemy_hp_region)
        
        return {
            "my_hp": my_hp_info.get('current', 0),
            "my_max_hp": my_hp_info.get('max', 0),
            "enemy_hp": enemy_hp_info.get('current', 0),
            "enemy_max_hp": enemy_hp_info.get('max', 0),
            "my_pokemon": None,  # TODO: Identificar Pokémon
            "enemy_pokemon": None,  # TODO: Identificar Pokémon inimigo
        }
    
    def _get_encounter_info(self, image: np.ndarray) -> Dict:
        """Extrai informações do encontro com Pokémon"""
        # Tentar extrair nome e nível usando OCR
        height, width = image.shape[:2]
        
        # Regiões aproximadas (ajustar conforme necessário)
        name_region = (int(width * 0.3), int(height * 0.3), int(width * 0.4), int(height * 0.1))
        level_region = (int(width * 0.6), int(height * 0.3), int(width * 0.2), int(height * 0.1))
        
        pokemon_name = self.ocr_engine.extract_text(image, name_region)
        level = self.ocr_engine.extract_numbers(image, level_region)
        
        return {
            "pokemon_name": pokemon_name.strip() if pokemon_name else None,
            "level": level if level else 0,
            "hp": 0,  # TODO: Extrair HP
        }

