"""
Módulo para processamento de imagens do jogo
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
from loguru import logger


class ImageProcessor:
    """Classe para processar imagens do jogo"""
    
    def __init__(self):
        """Inicializa o processador de imagens"""
        logger.info("ImageProcessor inicializado")
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Pré-processa a imagem para melhor análise
        
        Args:
            image: Imagem de entrada
            
        Returns:
            Imagem processada
        """
        # Converter para escala de cinza se necessário
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Aplicar filtro gaussiano para reduzir ruído
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return blurred
    
    def detect_objects(self, image: np.ndarray, 
                      template: np.ndarray, 
                      threshold: float = 0.8) -> List[Tuple[int, int]]:
        """
        Detecta objetos na imagem usando template matching
        
        Args:
            image: Imagem onde procurar
            template: Template para buscar
            threshold: Limiar de confiança (0-1)
            
        Returns:
            Lista de posições (x, y) onde o objeto foi encontrado
        """
        try:
            # Converter para escala de cinza
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
            
            # Template matching
            result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            positions = []
            for pt in zip(*locations[::-1]):
                positions.append(pt)
            
            return positions
        except Exception as e:
            logger.error(f"Erro ao detectar objetos: {e}")
            return []
    
    def extract_text_region(self, image: np.ndarray, 
                           region: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extrai uma região específica da imagem
        
        Args:
            image: Imagem completa
            region: (x, y, width, height)
            
        Returns:
            Região extraída
        """
        x, y, w, h = region
        return image[y:y+h, x:x+w]
    
    def detect_color(self, image: np.ndarray, 
                    color_range: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
        """
        Detecta uma cor específica na imagem
        
        Args:
            image: Imagem de entrada (HSV)
            color_range: Tupla (lower_bound, upper_bound) em HSV
            
        Returns:
            Máscara binária
        """
        lower, upper = color_range
        mask = cv2.inRange(image, lower, upper)
        return mask
    
    def find_contours(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Encontra contornos na imagem
        
        Args:
            image: Imagem binária
            
        Returns:
            Lista de contornos
        """
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def resize_image(self, image: np.ndarray, 
                    scale: float = 1.0) -> np.ndarray:
        """
        Redimensiona a imagem
        
        Args:
            image: Imagem de entrada
            scale: Fator de escala
            
        Returns:
            Imagem redimensionada
        """
        if scale == 1.0:
            return image
        
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    
    def enhance_text(self, image: np.ndarray) -> np.ndarray:
        """
        Melhora a imagem para melhor leitura de texto (OCR)
        
        Args:
            image: Imagem de entrada
            
        Returns:
            Imagem melhorada
        """
        # Converter para escala de cinza
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Aplicar morfologia para limpar
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned

