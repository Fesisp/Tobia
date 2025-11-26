"""
Módulo para OCR (Optical Character Recognition)
"""
import cv2
import numpy as np
import os
from pathlib import Path
from typing import Optional, Dict
from loguru import logger

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract não disponível. Funcionalidades de OCR limitadas.")


def find_tesseract_path() -> Optional[str]:
    """
    Tenta encontrar o caminho do executável do Tesseract no Windows
    
    Returns:
        Caminho do executável ou None
    """
    # Locais comuns de instalação do Tesseract no Windows
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
        r"C:\Tesseract-OCR\tesseract.exe",
    ]
    
    # Verificar cada caminho
    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"Tesseract encontrado em: {path}")
            return path
    
    # Tentar encontrar via variável de ambiente
    tesseract_cmd = os.getenv('TESSDATA_PREFIX')
    if tesseract_cmd:
        tesseract_exe = os.path.join(os.path.dirname(tesseract_cmd), 'tesseract.exe')
        if os.path.exists(tesseract_exe):
            logger.info(f"Tesseract encontrado via variável de ambiente: {tesseract_exe}")
            return tesseract_exe
    
    logger.warning("Tesseract não encontrado nos locais comuns. Configure manualmente.")
    return None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("easyocr não disponível.")


class OCREngine:
    """Classe para realizar OCR em imagens do jogo"""
    
    def __init__(self, use_easyocr: bool = False, tesseract_path: Optional[str] = None):
        """
        Inicializa o motor de OCR
        
        Args:
            use_easyocr: Se True, usa EasyOCR, senão usa Tesseract
            tesseract_path: Caminho manual para o executável do Tesseract (opcional)
        """
        self.use_easyocr = use_easyocr and EASYOCR_AVAILABLE
        
        if self.use_easyocr:
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
                logger.info("OCREngine inicializado com EasyOCR")
            except Exception as e:
                logger.error(f"Erro ao inicializar EasyOCR: {e}")
                self.use_easyocr = False
        
        # Configurar caminho do Tesseract se disponível
        if TESSERACT_AVAILABLE and not self.use_easyocr:
            tesseract_exe = tesseract_path or find_tesseract_path()
            if tesseract_exe:
                try:
                    pytesseract.pytesseract.tesseract_cmd = tesseract_exe
                    logger.info(f"Tesseract configurado: {tesseract_exe}")
                except Exception as e:
                    logger.error(f"Erro ao configurar Tesseract: {e}")
            else:
                logger.warning("Tesseract não configurado. Configure o caminho manualmente.")
        
        if not self.use_easyocr and not TESSERACT_AVAILABLE:
            logger.warning("Nenhum motor de OCR disponível!")
    
    def extract_text(self, image: np.ndarray, 
                    region: Optional[tuple] = None) -> str:
        """
        Extrai texto de uma imagem
        
        Args:
            image: Imagem de entrada
            region: Região para extrair (x, y, width, height)
            
        Returns:
            Texto extraído
        """
        if region:
            x, y, w, h = region
            roi = image[y:y+h, x:x+w]
        else:
            roi = image
        
        if self.use_easyocr:
            return self._extract_with_easyocr(roi)
        elif TESSERACT_AVAILABLE:
            return self._extract_with_tesseract(roi)
        else:
            return ""
    
    def _extract_with_tesseract(self, image: np.ndarray) -> str:
        """Extrai texto usando Tesseract"""
        try:
            # Pré-processar imagem para melhor OCR
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Configurar Tesseract
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(gray, config=custom_config)
            return text.strip()
        except Exception as e:
            logger.error(f"Erro ao extrair texto com Tesseract: {e}")
            return ""
    
    def _extract_with_easyocr(self, image: np.ndarray) -> str:
        """Extrai texto usando EasyOCR"""
        try:
            results = self.reader.readtext(image)
            text = ' '.join([result[1] for result in results])
            return text.strip()
        except Exception as e:
            logger.error(f"Erro ao extrair texto com EasyOCR: {e}")
            return ""
    
    def extract_numbers(self, image: np.ndarray, 
                       region: Optional[tuple] = None) -> Optional[int]:
        """
        Extrai números de uma imagem
        
        Args:
            image: Imagem de entrada
            region: Região para extrair
            
        Returns:
            Número extraído ou None
        """
        text = self.extract_text(image, region)
        # Remover caracteres não numéricos
        numbers = ''.join(filter(str.isdigit, text))
        try:
            return int(numbers) if numbers else None
        except ValueError:
            return None
    
    def extract_hp_info(self, image: np.ndarray, 
                       hp_bar_region: tuple) -> Dict[str, Optional[int]]:
        """
        Extrai informações de HP de uma barra de HP
        
        Args:
            image: Imagem de entrada
            hp_bar_region: Região da barra de HP (x, y, width, height)
            
        Returns:
            Dicionário com 'current' e 'max' HP
        """
        x, y, w, h = hp_bar_region
        roi = image[y:y+h, x:x+w]
        
        # Tentar extrair números da região
        text = self.extract_text(roi)
        
        # Procurar padrão "HP: X/Y" ou similar
        import re
        pattern = r'(\d+)\s*/\s*(\d+)'
        match = re.search(pattern, text)
        
        if match:
            current = int(match.group(1))
            max_hp = int(match.group(2))
            return {'current': current, 'max': max_hp}
        
        return {'current': None, 'max': None}

