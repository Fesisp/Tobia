import numpy as np
import cv2

from src.perception.ocr_engine import find_tesseract_path, OCREngine


def test_tesseract_ocr_basic():
    """Verifica que o Tesseract é encontrado e consegue extrair texto simples."""
    tesseract_path = find_tesseract_path()
    assert tesseract_path, "Tesseract não encontrado no sistema"

    ocr = OCREngine(tesseract_path=tesseract_path)

    # Criar imagem simples com texto
    test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
    cv2.putText(test_image, "TEST", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    text = ocr.extract_text(test_image)
    assert text is not None
    assert "TEST" in text.upper()
