"""CLI to inspect a screenshot and output player/NPC speech and nameplates.

Usage:
  python tools/speaker_inspect.py <image_path>

Saves annotated image to `logs/` and prints a concise JSON-like summary.
"""
import sys
import json
import os
import cv2

# Ensure project root is on sys.path so `src` imports work when running this script
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.perception.speaker_detector import SpeakerDetector


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/speaker_inspect.py <image_path>")
        sys.exit(2)

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print(f"Image not found: {img_path}")
        sys.exit(2)

    img = cv2.imread(img_path)
    sd = SpeakerDetector()
    det = sd.detect(img)

    # debug: raw OCR boxes (sample)
    try:
        raw_boxes = sd._ocr_boxes(img)
        raw_sample = [ {'text': b['text'], 'bbox': b['bbox']} for b in raw_boxes[:40] ]
    except Exception:
        raw_sample = []

    # heuristically find possible name tokens from all OCR boxes
    possible_names = []
    try:
        for b in raw_boxes:
            t = b['text']
            if len(t) >= 3 and any(c.isalpha() for c in t):
                # prefer tokens with mixed case or tokens ending with ':' (chat prefix)
                if any(c.isupper() for c in t) or t.endswith(':') or ':' in t:
                    possible_names.append({'text': t, 'bbox': b['bbox']})
        # dedupe
        seen = set()
        filtered = []
        for p in possible_names:
            if p['text'] not in seen:
                filtered.append(p)
                seen.add(p['text'])
        summary_candidates = filtered[:80]
    except Exception:
        summary_candidates = []

    summary = {
        'player_chat_count': len(det.get('player_chat', [])),
        'npc_dialog_count': len(det.get('npc_dialog', [])),
        'nameplates_count': len(det.get('nameplates', [])),
        'player_chat': [p['text'] for p in det.get('player_chat', [])],
        'npc_dialog': [n['text'] for n in det.get('npc_dialog', [])],
        'nameplates': [n['text'] for n in det.get('nameplates', [])],
    }

    # classify nameplates into player/npc
    classified = sd.classify_nameplates(det, img)
    summary['nameplates_classified'] = classified

    # detect dialog choice buttons
    bubble_bbox = None
    bubbles = sd._find_dialog_bubbles(img)
    if bubbles:
        bubbles.sort(key=lambda b: b[2] * b[3], reverse=True)
        bubble_bbox = bubbles[0]
    choices = sd._find_choice_buttons(img, bubble_bbox)
    summary['dialog_choices'] = choices
    summary['raw_ocr_boxes_sample'] = raw_sample
    summary['possible_name_candidates'] = summary_candidates

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    annotated, out_name = sd.annotate(img, det)
    print(f"Annotated image saved to: {out_name}")
    if choices:
        print(f"Detected {len(choices)} dialog choices:")
        for c in choices:
            print(f" - {c['text']}")


if __name__ == '__main__':
    main()
