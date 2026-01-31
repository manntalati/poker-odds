import cv2
import numpy as np
from detector import CardDetector
from poker import PokerEngine
from ui import draw_ui

def main():
    print("Initializing Poker Odds Calculator...")
    
    # Initialize components
    detector = CardDetector()
    poker = PokerEngine()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        # Detect cards
        cards = detector.detect(frame)
        
        # Update poker game state
        poker.update_state(cards)
        
        # Calculate odds
        odds = poker.calculate_odds()
        
        # Draw UI
        frame = draw_ui(frame, cards, odds)

        cv2.imshow('Poker Odds Calculator', frame)
        
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
