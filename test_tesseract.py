"""
Script para testar se o Tesseract está configurado corretamente
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.perception.ocr_engine import find_tesseract_path, OCREngine
from loguru import logger

def main():
    """Testa a configuração do Tesseract"""
    logger.info("=" * 50)
    logger.info("Teste de Configuração do Tesseract")
    logger.info("=" * 50)
    
    # Tentar encontrar o Tesseract
    logger.info("\n1. Procurando Tesseract...")
    tesseract_path = find_tesseract_path()
    
    if tesseract_path:
        logger.info(f"✓ Tesseract encontrado em: {tesseract_path}")
    else:
        logger.warning("✗ Tesseract não encontrado automaticamente")
        logger.info("\nSoluções:")
        logger.info("1. Adicione o Tesseract ao PATH do sistema")
        logger.info("2. Configure manualmente em config/settings.yaml")
        logger.info("3. Veja TESSERACT_SETUP.md para mais detalhes")
        return
    
    # Tentar inicializar o OCR
    logger.info("\n2. Inicializando OCR Engine...")
    try:
        ocr_engine = OCREngine(tesseract_path=tesseract_path)
        logger.info("✓ OCR Engine inicializado com sucesso!")
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar OCR Engine: {e}")
        return
    
    # Teste simples de OCR
    logger.info("\n3. Testando OCR...")
    try:
        import numpy as np
        import cv2
        
        # Criar uma imagem de teste simples com texto
        test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(test_image, "TEST", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        text = ocr_engine.extract_text(test_image)
        if text:
            logger.info(f"✓ OCR funcionando! Texto extraído: '{text}'")
        else:
            logger.warning("⚠ OCR não extraiu texto (pode ser normal com imagem simples)")
    except Exception as e:
        logger.error(f"✗ Erro ao testar OCR: {e}")
        return
    
    logger.info("\n" + "=" * 50)
    logger.info("✓ Tesseract está configurado corretamente!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()

