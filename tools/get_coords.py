import cv2
import sys

# Função que será chamada quando você clicar na imagem
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"🎯 Clique registrado: x={x}, y={y}")

# Verifica se passou a imagem
if len(sys.argv) < 2:
    print("Uso: python tools/get_coords.py <caminho_da_imagem>")
    sys.exit(1)

# Carrega e mostra a imagem
img = cv2.imread(sys.argv[1])
if img is None:
    print("Erro ao abrir imagem.")
    sys.exit(1)

print("🔍 Ferramenta de Mapeamento iniciada!")
print("1. Clique no canto SUPERIOR ESQUERDO da área que você quer.")
print("2. Clique no canto INFERIOR DIREITO da área.")
print("3. Anote os valores.")
print("Pressione qualquer tecla na imagem para fechar.")

cv2.imshow('Mapeamento', img)
cv2.setMouseCallback('Mapeamento', click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()