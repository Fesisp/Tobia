import sys
import cv2
import numpy as np

def analyze(path):
    img = cv2.imread(path)
    if img is None:
        print('Erro: não conseguiu ler a imagem', path)
        return 1
    h, w = img.shape[:2]
    region = img[int(h * 0.82):int(h * 0.95), int(w * 0.35):int(w * 0.65)]
    if region.size == 0:
        print('Região vazia')
        return 1
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

    # thresholds usados no detector
    red_lower1 = np.array([0, 120, 80])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([170, 120, 80])
    red_upper2 = np.array([180, 255, 255])
    red_mask = cv2.bitwise_or(cv2.inRange(hsv, red_lower1, red_upper1), cv2.inRange(hsv, red_lower2, red_upper2))

    blue_lower = np.array([100, 120, 80])
    blue_upper = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)

    yellow_lower = np.array([18, 120, 80])
    yellow_upper = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

    green_lower = np.array([40, 80, 80])
    green_upper = np.array([80, 255, 255])
    green_mask = cv2.inRange(hsv, green_lower, green_upper)

    sums = {
        'red': int(np.sum(red_mask)),
        'blue': int(np.sum(blue_mask)),
        'yellow': int(np.sum(yellow_mask)),
        'green': int(np.sum(green_mask)),
    }

    print('Região analisada:', region.shape)
    print('Somas de máscara (pixel-intensity sums):')
    for k, v in sums.items():
        print(f'  {k}: {v}')

    threshold = 1500
    detected = [k for k,v in sums.items() if v > threshold]
    if detected:
        print('Detectado botão(s):', detected)
    else:
        print('Nenhum botão detectado acima do threshold', threshold)
    # Verificar barras de HP nas regiões top-left e bottom-right (como no detector)
    full_h, full_w = img.shape[:2]
    top_left = img[0:int(full_h * 0.15), 0:int(full_w * 0.3)]
    bottom_right = img[int(full_h * 0.75):, int(full_w * 0.65):]
    def sum_green(region):
        if region.size == 0:
            return 0
        hsv_r = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        green_lower = np.array([40, 80, 80])
        green_upper = np.array([80, 255, 255])
        return int(np.sum(cv2.inRange(hsv_r, green_lower, green_upper)))

    green_top = sum_green(top_left)
    green_bottom = sum_green(bottom_right)
    print(f'HP green sums - top_left: {green_top}, bottom_right: {green_bottom}')
    if green_top + green_bottom > 2000:
        print('Detecção de barras de HP: provável batalha (soma > 2000)')
    else:
        print('Barras de HP não detectadas (soma <= 2000)')
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Uso: inspect_battle.py <image_path>')
        sys.exit(1)
    sys.exit(analyze(sys.argv[1]))
