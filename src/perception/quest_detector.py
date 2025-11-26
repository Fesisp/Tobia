"""
Módulo para detectar e ler informações de quests
"""
import cv2
import numpy as np
from typing import Dict, Optional, Tuple
from loguru import logger
from .image_processing import ImageProcessor
from .ocr_engine import OCREngine
from .screen_capture import ScreenCapture


class QuestDetector:
    """Classe para detectar e extrair informações de quests"""
    
    def __init__(self, screen_capture: ScreenCapture, ocr_config: Optional[dict] = None):
        """
        Inicializa o detector de quests
        
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
        
        # Região aproximada da UI de Quests (canto superior direito)
        # Ajustar conforme necessário baseado na resolução
        self.quest_ui_region = None  # Será calculado dinamicamente
        
        logger.info("QuestDetector inicializado")
    
    def detect_quest_ui(self, image: np.ndarray) -> bool:
        """
        Detecta se a UI de Quests está visível
        
        Args:
            image: Imagem da tela
            
        Returns:
            True se a UI de Quests está visível
        """
        height, width = image.shape[:2]
        
        # Região do canto superior direito onde geralmente fica a UI de Quests
        # Aproximadamente 20-30% da largura e 10-20% da altura
        quest_region_x = int(width * 0.7)
        quest_region_y = int(height * 0.05)
        quest_region_w = int(width * 0.28)
        quest_region_h = int(height * 0.25)
        
        self.quest_ui_region = (quest_region_x, quest_region_y, quest_region_w, quest_region_h)
        
        # Extrair região de quests
        quest_roi = self.image_processor.extract_text_region(image, self.quest_ui_region)
        
        # Procurar por texto "Quest" ou "Quests"
        text = self.ocr_engine.extract_text(quest_roi)
        if "quest" in text.lower():
            return True
        
        # Alternativa: procurar por botão "Quests" visualmente
        # (pode usar template matching se tiver template)
        
        return False
    
    def extract_active_quest(self, image: np.ndarray) -> Optional[Dict]:
        """
        Extrai informações da quest ativa
        
        Args:
            image: Imagem da tela
            
        Returns:
            Dicionário com informações da quest ou None
        """
        if not self.detect_quest_ui(image):
            return None
        
        if self.quest_ui_region is None:
            return None
        
        x, y, w, h = self.quest_ui_region
        quest_roi = image[y:y+h, x:x+w]
        
        # Melhorar imagem para OCR
        enhanced = self.image_processor.enhance_text(quest_roi)
        
        # Extrair texto completo da região
        full_text = self.ocr_engine.extract_text(enhanced)
        
        # Tentar extrair informações estruturadas
        quest_info = self._parse_quest_text(full_text)
        
        if quest_info:
            logger.info(f"Quest detectada: {quest_info.get('title', 'Unknown')}")
            logger.debug(f"Objetivo: {quest_info.get('objective', 'Unknown')}")
        
        return quest_info
    
    def _parse_quest_text(self, text: str) -> Optional[Dict]:
        """
        Analisa o texto extraído para obter informações da quest
        
        Args:
            text: Texto extraído da região de quests
            
        Returns:
            Dicionário com informações da quest
        """
        if not text or len(text.strip()) < 5:
            return None
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        quest_info = {
            'title': None,
            'objective': None,
            'has_goto_button': False
        }
        
        # Procurar por título da quest (geralmente primeira linha significativa)
        for i, line in enumerate(lines):
            if len(line) > 3 and not line.isdigit():
                # Remover caracteres especiais comuns em OCR
                clean_line = line.replace('|', '').replace('_', '').strip()
                if len(clean_line) > 3:
                    quest_info['title'] = clean_line
                    break
        
        # Procurar por objetivo (geralmente contém palavras-chave)
        objective_keywords = ['challenge', 'defeat', 'go to', 'find', 'collect', 'talk to', 'visit']
        for line in lines:
            line_lower = line.lower()
            for keyword in objective_keywords:
                if keyword in line_lower:
                    quest_info['objective'] = line
                    break
        
        # Procurar por botão "Goto"
        full_text_lower = text.lower()
        if 'goto' in full_text_lower or 'go to' in full_text_lower:
            quest_info['has_goto_button'] = True
        
        # Se não encontrou objetivo específico, usar segunda linha como objetivo
        if not quest_info['objective'] and len(lines) > 1:
            quest_info['objective'] = lines[1] if len(lines[1]) > 5 else None
        
        return quest_info if quest_info['title'] or quest_info['objective'] else None
    
    def find_goto_button(self, image: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Encontra a posição do botão "Goto" na UI de quests
        
        Args:
            image: Imagem da tela
            
        Returns:
            Posição (x, y) do botão ou None
        """
        if self.quest_ui_region is None:
            return None
        
        x, y, w, h = self.quest_ui_region
        quest_roi = image[y:y+h, x:x+w]
        
        # Método 1: Procurar por texto "Goto" usando OCR
        enhanced = self.image_processor.enhance_text(quest_roi)
        text = self.ocr_engine.extract_text(enhanced)
        
        if 'goto' in text.lower():
            # Se encontrou texto "Goto", procurar por botão próximo
            # O botão geralmente está abaixo ou ao lado do texto do objetivo
            
            # Converter para HSV para melhor detecção de cores
            hsv = cv2.cvtColor(quest_roi, cv2.COLOR_BGR2HSV)
            
            # Procurar por botão (geralmente tem cor específica)
            # Cores comuns de botões: azul, verde, laranja
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            lower_green = np.array([40, 50, 50])
            upper_green = np.array([80, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Laranja/amarelo (comum em botões de ação)
            lower_orange = np.array([10, 100, 100])
            upper_orange = np.array([25, 255, 255])
            orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
            
            # Combinar máscaras
            button_mask = cv2.bitwise_or(cv2.bitwise_or(blue_mask, green_mask), orange_mask)
            
            # Aplicar morfologia para limpar
            kernel = np.ones((3, 3), np.uint8)
            button_mask = cv2.morphologyEx(button_mask, cv2.MORPH_CLOSE, kernel)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(button_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Procurar por contorno retangular (botão)
            buttons = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 10000:  # Tamanho típico de botão
                    x_btn, y_btn, w_btn, h_btn = cv2.boundingRect(contour)
                    aspect_ratio = w_btn / h_btn if h_btn > 0 else 0
                    # Botões geralmente são mais largos que altos
                    if 1.2 < aspect_ratio < 6.0:
                        center_x = x + x_btn + w_btn // 2
                        center_y = y + y_btn + h_btn // 2
                        buttons.append((center_x, center_y, area))
            
            # Retornar o botão maior (mais provável de ser o botão Goto)
            if buttons:
                buttons.sort(key=lambda b: b[2], reverse=True)
                logger.debug(f"Botão Goto encontrado em: ({buttons[0][0]}, {buttons[0][1]})")
                return (buttons[0][0], buttons[0][1])
        
        # Método 2: Procurar por região de botão na parte inferior da UI de quests
        # O botão geralmente está na parte inferior da região de quests
        button_region_y = int(h * 0.6)  # Últimos 40% da altura
        button_region = quest_roi[button_region_y:, :]
        
        if button_region.size > 0:
            hsv_button = cv2.cvtColor(button_region, cv2.COLOR_BGR2HSV)
            
            # Procurar por cores de botão
            lower_button = np.array([0, 0, 150])  # Cores claras
            upper_button = np.array([180, 50, 255])
            button_mask = cv2.inRange(hsv_button, lower_button, upper_button)
            
            contours, _ = cv2.findContours(button_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 300 < area < 8000:
                    x_btn, y_btn, w_btn, h_btn = cv2.boundingRect(contour)
                    center_x = x + x_btn + w_btn // 2
                    center_y = y + button_region_y + y_btn + h_btn // 2
                    return (center_x, center_y)
        
        return None

