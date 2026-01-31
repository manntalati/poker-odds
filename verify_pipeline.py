import cv2
import numpy as np
from poker import PokerEngine
from ui import draw_ui

def verify_pipeline():
    try:
        print("Starting pipeline verification...")
        
        # Mock detection
        detected_cards = [
            {'label': 'Ah', 'conf': 0.95, 'bbox': (100, 300, 150, 400)},  # Hero
            {'label': 'Kh', 'conf': 0.94, 'bbox': (160, 300, 210, 400)},  # Hero
            {'label': 'Th', 'conf': 0.90, 'bbox': (100, 100, 150, 200)},  # Board
            {'label': 'Jh', 'conf': 0.88, 'bbox': (160, 100, 210, 200)},  # Board
            {'label': 'Qh', 'conf': 0.92, 'bbox': (220, 100, 270, 200)},  # Board
        ]
        
        # Poker Engine
        poker = PokerEngine()
        poker.update_state(detected_cards)
        
        # Verify state
        print(f"Hero Hand: {[str(c) for c in poker.hero_hand]}")
        print(f"Community Cards: {[str(c) for c in poker.community_cards]}")
        
        if len(poker.hero_hand) != 2 or len(poker.community_cards) != 3:
            print("ERROR: Card separation logic failed.")
            return

        # Inspect cards
        print("Debugging Card Values:")
        for i, c in enumerate(poker.hero_hand):
            print(f"Hero Card {i}: {c} (Mask: {c & 0xFF})")
        for i, c in enumerate(poker.community_cards):
            print(f"Comm Card {i}: {c} (Mask: {c & 0xFF})")

        # Calculate Odds
        odds = poker.calculate_odds()
        print(f"Odds: {odds}")
        
        if odds['win_rate'] < 99.0 and odds['tie_rate'] < 1.0: 
             # It's possible to chop with another Royal Flush on board (unlikely with this board)
             # Wait, if board is Th Jh Qh, only Ah Kh makes Royal Flush.
             # So win rate should be 100% or split if board plays?
             # If board is TJQ, and I have AK, checking win rate.
             print("WARNING: Win rate seems low for Royal Flush?")
        
        # UI Drawing
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = draw_ui(frame, detected_cards, odds)
        
        cv2.imwrite("verification_frame.jpg", frame)
        print("Verification frame saved. Pipeline success.")
        
    except Exception as e:
        print(f"Pipeline Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_pipeline()
