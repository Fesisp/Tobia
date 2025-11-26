"""
Módulo para captura de tela do jogo
"""
import time
import numpy as np
from typing import Optional, Tuple
from mss import mss
from PIL import Image
import cv2
from loguru import logger


class ScreenCapture:
    """Classe para capturar e processar telas do jogo"""
    
    def __init__(self, region: Optional[Tuple[int, int, int, int]] = None):
        """
        Inicializa o capturador de tela
        
        Args:
            region: Região da tela para capturar (x, y, width, height)
                    Se None, captura a tela inteira
        """
        self.sct = mss()
        self.region = region
        if region:
            self.monitor = {
                "top": region[1],
                "left": region[0],
                "width": region[2],
                "height": region[3]
            }
        else:
            # Captura a tela principal
            self.monitor = self.sct.monitors[1]
        
        logger.info(f"ScreenCapture inicializado - Região: {self.monitor}")
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Captura uma screenshot da tela
        
        Returns:
            Imagem como array numpy (BGR para OpenCV)
        """
        try:
            screenshot = self.sct.grab(self.monitor)
            img = np.array(screenshot)
            # Converter de BGRA para BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            logger.error(f"Erro ao capturar tela: {e}")
            return None
    
    def capture_rgb(self) -> Optional[np.ndarray]:
        """
        Captura screenshot em formato RGB
        
        Returns:
            Imagem como array numpy (RGB)
        """
        img = self.capture()
        if img is not None:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return None
    
    def save_screenshot(self, filename: str) -> bool:
        """
        Salva uma screenshot
        
        Args:
            filename: Nome do arquivo para salvar
            
        Returns:
            True se salvou com sucesso
        """
        try:
            img = self.capture()
            if img is not None:
                cv2.imwrite(filename, img)
                logger.debug(f"Screenshot salva: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao salvar screenshot: {e}")
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Retorna o tamanho da tela capturada
        
        Returns:
            Tupla (width, height)
        """
        return (self.monitor["width"], self.monitor["height"])

