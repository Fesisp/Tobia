import time
from typing import List, Dict, Any, Tuple
import cv2
import pytesseract


class SpeakerDetector:
    """Detect player chat, NPC dialog and character nameplates from a game screenshot.

    This is a heuristic, rule-based detector that uses pytesseract's OCR boxes and
    spatial rules (relative ROIs) to classify text as:
      - player_chat: text in the bottom-left chat area
      - npc_dialog: text in a central dialog bubble area
      - nameplates: short text near characters (above sprites)

    The heuristics can be tuned for different resolutions by changing the ROI
    fractions below.
    """

    def __init__(self, ocr_lang: str = 'eng'):
        self.ocr_lang = ocr_lang

    def _ocr_boxes(self, image) -> List[Dict[str, Any]]:
        # Run OCR on multiple variants to improve detection of outlined/low-contrast text
        variants = []
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        variants.append(rgb)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        _, th = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        inv = cv2.bitwise_not(th)
        variants.append(cv2.cvtColor(inv, cv2.COLOR_GRAY2RGB))

        boxes = []
        seen = set()
        for var in variants:
            data = pytesseract.image_to_data(var, lang=self.ocr_lang, output_type=pytesseract.Output.DICT)
            n = len(data['text'])
            for i in range(n):
                text = str(data['text'][i]).strip()
                if not text:
                    continue
                conf_val = data['conf'][i]
                try:
                    conf = int(conf_val)
                except Exception:
                    conf = -1
                x, y, w, h = int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])
                key = (text, x, y, w, h)
                if key in seen:
                    continue
                seen.add(key)
                boxes.append({'text': text, 'conf': conf, 'bbox': (x, y, w, h)})
        return boxes

    def _find_dialog_bubbles(self, image) -> List[Tuple[int,int,int,int]]:
        """Detect candidate dialog/chat bubbles using morphology and contour filtering.

        Returns list of bounding boxes (x,y,w,h) for bubble-like regions.
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # adaptive threshold to get dark-on-light or light-on-dark bubbles
        th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
        # close gaps to merge text into bubble shapes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 7))
        close = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            area = cw * ch
            # filter by reasonable size relative to image
            if area < (w * h) * 0.0008:
                continue
            if ch < 18 or cw < 40:
                continue
            # avoid very large UI panels
            if area > (w * h) * 0.5:
                continue
            candidates.append((x, y, cw, ch))

        # sort left-to-right, top-to-bottom
        candidates.sort(key=lambda b: (b[1], b[0]))
        return candidates

    def detect(self, image) -> Dict[str, Any]:
        h, w = image.shape[:2]
        boxes = self._ocr_boxes(image)

        player_chat_boxes: List[Dict[str, Any]] = []
        npc_dialog_boxes: List[Dict[str, Any]] = []
        nameplate_boxes: List[Dict[str, Any]] = []

        # detect dialog bubbles to attribute enclosed text to NPC dialog
        bubbles = self._find_dialog_bubbles(image)

        def inside(bx, by, bw, bh, rx, ry, rw, rh):
            return bx >= rx and by >= ry and (bx + bw) <= (rx + rw) and (by + bh) <= (ry + rh)

        # precompute character head centers for nameplate proximity mapping
        heads = self._find_character_heads(image)

        for b in boxes:
            x, y, bw, bh = b['bbox']
            cx = x + bw / 2
            cy = y + bh / 2
            txt = b['text']

            attributed = False
            for (rx, ry, rw, rh) in bubbles:
                if rx <= cx <= rx + rw and ry <= cy <= ry + rh:
                    npc_dialog_boxes.append({'text': txt, 'conf': b['conf'], 'bbox': b['bbox']})
                    attributed = True
                    break
            if attributed:
                continue

            # Bottom-left chat window heuristic (player chat)
            if cx < w * 0.33 and cy > h * 0.6:
                player_chat_boxes.append({'text': txt, 'conf': b['conf'], 'bbox': b['bbox']})
                continue

            # nameplate by proximity to detected head centers
            assigned = False
            for (hc_x, hc_y) in heads:
                dist = ((cx - hc_x) ** 2 + (cy - hc_y) ** 2) ** 0.5
                diag = (w ** 2 + h ** 2) ** 0.5
                if dist < diag * 0.08:
                    nameplate_boxes.append({'text': txt, 'conf': b['conf'], 'bbox': b['bbox']})
                    assigned = True
                    break
            if assigned:
                continue

            # fallback nameplate heuristic: short text in mid area
            if 1 < len(txt) <= 24 and h * 0.05 < cy < h * 0.75:
                nameplate_boxes.append({'text': txt, 'conf': b['conf'], 'bbox': b['bbox']})

        # group player chat tokens into lines by y coordinate proximity
        player_chat = []
        if player_chat_boxes:
            rows = {}
            for p in player_chat_boxes:
                x, y, bw, bh = p['bbox']
                row_key = int((y + bh / 2) / 15)  # bucket by 15px rows
                rows.setdefault(row_key, []).append((x, p))
            for k in sorted(rows.keys()):
                items = sorted(rows[k], key=lambda t: t[0])
                line = ' '.join([it[1]['text'] for it in items])
                player_chat.append({'text': line, 'conf': max(it[1]['conf'] for it in items), 'bbox': None})

        # combine NPC dialog tokens into a single string
        npc_dialog = []
        if npc_dialog_boxes:
            items = sorted(npc_dialog_boxes, key=lambda b: (b['bbox'][1], b['bbox'][0]))
            dialog_text = ' '.join([it['text'] for it in items])
            npc_dialog.append({'text': dialog_text, 'conf': max(it['conf'] for it in items), 'bbox': None})

        # nameplates: dedupe and keep as-is
        nameplates = []
        seen_names = set()
        for npb in nameplate_boxes:
            name = npb['text']
            if name not in seen_names:
                seen_names.add(name)
                nameplates.append(npb)

        # if no nameplates found, attempt morph-based detection and head-zoom detection
        if not nameplates:
            morph = self.detect_nameplates_by_morph(image)
            for m in morph:
                if m['text'] not in seen_names:
                    seen_names.add(m['text'])
                    nameplates.append(m)
        if not nameplates:
            heads_detected = self.detect_nameplates_by_heads(image)
            for h in heads_detected:
                if h['text'] not in seen_names:
                    seen_names.add(h['text'])
                    nameplates.append(h)

        return {
            'player_chat': player_chat,
            'npc_dialog': npc_dialog,
            'nameplates': nameplates,
        }

    def _find_choice_buttons(self, image, bubble_bbox=None) -> List[Dict[str, Any]]:
        """Detect small rectangular choice buttons (text inside) near a dialog bubble.

        Returns list of {'text': str, 'bbox': (x,y,w,h)}
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        close = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)

        # restrict search region to bubble_bbox expanded or bottom-center if None
        if bubble_bbox:
            rx, ry, rw, rh = bubble_bbox
            sx = max(0, rx - int(rw * 0.2))
            sy = max(0, ry - int(rh * 0.2))
            ex = min(w, rx + rw + int(rw * 0.2))
            ey = min(h, ry + rh + int(rh * 0.6))
            roi = close[sy:ey, sx:ex]
            roi_off = (sx, sy)
        else:
            sx, sy, ex, ey = int(w * 0.25), int(h * 0.5), int(w * 0.75), int(h * 0.95)
            roi = close[sy:ey, sx:ex]
            roi_off = (sx, sy)

        contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        buttons = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            area = cw * ch
            if area < 400 or ch < 12 or cw < 30:
                continue
            # likely button aspect ratios
            if cw / max(1, ch) < 1.5 and cw / max(1, ch) > 0.6:
                bx = x + roi_off[0]
                by = y + roi_off[1]
                crop = image[by:by + ch, bx:bx + cw]
                # OCR the crop for button label
                label = pytesseract.image_to_string(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), lang=self.ocr_lang).strip()
                if label:
                    buttons.append({'text': label, 'bbox': (bx, by, cw, ch)})
        # sort left-to-right
        buttons.sort(key=lambda b: b['bbox'][0])
        return buttons

    def classify_nameplates(self, detection: Dict[str, Any], image) -> List[Dict[str, Any]]:
        """Classify detected nameplates as 'player', 'npc' or 'unknown'.

        Heuristics used:
          - If a name appears as a prefix in `player_chat` lines, mark as 'player'.
          - If a nameplate is spatially close to npc_dialog bubble center, mark 'npc'.
          - Else 'unknown'.
        """
        nameplates = detection.get('nameplates', [])
        player_chat_texts = [c['text'] for c in detection.get('player_chat', [])]
        npc_bubble_bbox = None
        if detection.get('npc_dialog'):
            # attempt to find bubble by using dialog bounding boxes via _find_dialog_bubbles
            bubbles = self._find_dialog_bubbles(image)
            if bubbles:
                # pick largest
                bubbles.sort(key=lambda b: b[2] * b[3], reverse=True)
                npc_bubble_bbox = bubbles[0]

        classified = []
        for npb in nameplates:
            name = npb['text']
            bbox = npb.get('bbox')
            role = 'unknown'
            # match by token presence in player chat lines
            lname = name.lower()
            for line in player_chat_texts:
                if lname in line.lower():
                    role = 'player'
                    break

            # spatial proximity to npc bubble -> npc
            if role == 'unknown' and npc_bubble_bbox and bbox:
                bx, by, bw, bh = bbox
                npc_x, npc_y, npc_w, npc_h = npc_bubble_bbox
                # distance between centers
                cx1 = bx + bw / 2
                cy1 = by + bh / 2
                cx2 = npc_x + npc_w / 2
                cy2 = npc_y + npc_h / 2
                dist = ((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2) ** 0.5
                diag = (image.shape[0] ** 2 + image.shape[1] ** 2) ** 0.5
                if dist < diag * 0.12:
                    role = 'npc'

            classified.append({'name': name, 'bbox': bbox, 'role': role})
        return classified

    def _find_character_heads(self, image) -> List[Tuple[int,int]]:
        """Find candidate character head centers by detecting small dark circular shadows on the floor.

        Returns list of (cx, cy) pixel coordinates.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # emphasize darker blobs
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # invert so shadows (dark) become foreground
        inv = 255 - th
        # morphology to consolidate round blobs
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        close = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours, _ = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h, w = image.shape[:2]
        centers = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            area = cw * ch
            if area < (w * h) * 0.0004 or area > (w * h) * 0.02:
                continue
            cx = int(x + cw / 2)
            cy = int(y + ch / 2)
            centers.append((cx, cy))
        return centers

    def _ocr_zoom_nameplate(self, image, cx: int, cy: int) -> Tuple[str, Tuple[int,int,int,int]]:
        """Crop a small region above the given head center, upscale and OCR for a single-line nameplate.

        Returns (text, bbox) or (None, None) if nothing found.
        """
        h, w = image.shape[:2]
        # region size relative to image
        rw = int(w * 0.12)
        rh = int(h * 0.06)
        rx = max(0, int(cx - rw / 2))
        ry = max(0, int(cy - int(h * 0.06) - rh))
        if ry < 0:
            ry = 0
        rx = min(max(0, rx), w - rw)
        ry = min(max(0, ry), h - rh)
        crop = image[ry:ry + rh, rx:rx + rw]
        if crop.size == 0:
            return None, None
        # upscale to help OCR
        scale = 3
        big = cv2.resize(crop, (rw * scale, rh * scale), interpolation=cv2.INTER_CUBIC)
        # preprocess
        gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # OCR single line
        config = '--psm 7'
        text = pytesseract.image_to_string(th, lang=self.ocr_lang, config=config).strip()
        # sanitize
        if not text or len(text) > 24:
            return None, None
        # map bbox back to original image coords
        return text, (rx, ry, rw, rh)

    def detect_nameplates_by_heads(self, image) -> List[Dict[str, Any]]:
        centers = self._find_character_heads(image)
        results = []
        seen = set()
        for (cx, cy) in centers:
            text, bbox = self._ocr_zoom_nameplate(image, cx, cy)
            if text and text not in seen:
                seen.add(text)
                results.append({'text': text, 'conf': 80, 'bbox': bbox})
        return results

    def _find_nameplate_boxes_by_morphology(self, image) -> List[Tuple[int,int,int,int]]:
        """Detect small horizontal boxes that likely contain nameplates using morphology."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        # emphasize horizontal rectangular regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
        grad = cv2.morphologyEx(blur, cv2.MORPH_GRADIENT, kernel)
        _, th = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # close to fill
        k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
        close = cv2.morphologyEx(th, cv2.MORPH_CLOSE, k2, iterations=2)
        contours, _ = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h, w = image.shape[:2]
        boxes = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            area = cw * ch
            if area < (w * h) * 0.0002 or area > (w * h) * 0.02:
                continue
            ar = cw / max(1, ch)
            if ar < 2.0:
                continue
            boxes.append((x, y, cw, ch))
        # filter and return
        boxes.sort(key=lambda b: (b[1], b[0]))
        return boxes

    def detect_nameplates_by_morph(self, image) -> List[Dict[str, Any]]:
        candidates = self._find_nameplate_boxes_by_morphology(image)
        results = []
        seen = set()
        for (x, y, w0, h0) in candidates:
            crop = image[y:y + h0, x:x + w0]
            if crop.size == 0:
                continue
            big = cv2.resize(crop, (w0 * 3, h0 * 3), interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
            _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(th, lang=self.ocr_lang, config='--psm 7').strip()
            if text and len(text) <= 24:
                clean = text.replace('\n', ' ').strip()
                # ignore candidate boxes that are too low on the screen (chat area)
                if y > image.shape[0] * 0.85:
                    continue
                if clean and clean not in seen:
                    seen.add(clean)
                    results.append({'text': clean, 'conf': 80, 'bbox': (x, y, w0, h0)})
        return results

    def annotate(self, image, detection: Dict[str, Any]) -> Tuple[Any, str]:
        out = image.copy()
        now = int(time.time() * 1000)
        h, w = out.shape[:2]

        def draw_list(items, color, label_prefix, start_y=10):
            y_offset = start_y
            for it in items:
                text = f"{label_prefix}: {it['text']}"
                bbox = it.get('bbox')
                if bbox:
                    x, y, bw, bh = bbox
                    cv2.rectangle(out, (x, y), (x + bw, y + bh), color, 2)
                    cv2.putText(out, text, (x, max(12, y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
                else:
                    # draw stacked labels on top-left area to indicate grouped text
                    cv2.putText(out, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
                    y_offset += 16

        draw_list(detection.get('player_chat', []), (0, 255, 0), 'Player', start_y=20)
        draw_list(detection.get('npc_dialog', []), (0, 165, 255), 'NPC', start_y=140)
        draw_list(detection.get('nameplates', []), (255, 0, 0), 'Name', start_y=220)

        out_name = f"logs/speaker_inspect_{now}.png"
        cv2.imwrite(out_name, out)
        return out, out_name


def quick_detect_file(path: str) -> Dict[str, Any]:
    img = cv2.imread(path)
    sd = SpeakerDetector()
    det = sd.detect(img)
    return det
