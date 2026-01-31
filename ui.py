import cv2

def draw_ui(frame, detected_cards, odds):
    # Draw detected cards
    for card in detected_cards:
        x1, y1, x2, y2 = card['bbox']
        label = card['label']
        conf = card['conf']
        
        # Color: Green for Hero (bottom likely), Blue for Board
        # Using a simple heuristic for color based on Y position (similar to poker.py logic but just for UI)
        # Actually poker.py already classified them internally, but detected_cards here is raw.
        # Let's just use Cyan for all cards for now
        color = (255, 255, 0) 
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Draw Odds Box
    panel_color = (0, 0, 0)
    cv2.rectangle(frame, (0, 0), (300, 150), panel_color, -1)
    
    # Generic text color
    text_color = (255, 255, 255)
    
    cv2.putText(frame, f"Stage: {odds.get('stage', 'Unknown')}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
    
    win_rate = odds.get('win_rate', 0.0)
    tie_rate = odds.get('tie_rate', 0.0)
    
    cv2.putText(frame, f"Win: {win_rate:.1f}%", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Tie: {tie_rate:.1f}%", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
    # Recommendation
    rec = "Wait"
    if win_rate > 60:
        rec = "Strong - Bet/Raise"
    elif win_rate > 40:
        rec = "Check/Call"
    elif win_rate > 20:
        rec = "Caution"
    else:
        rec = "Fold"
        
    cv2.putText(frame, f"Action: {rec}", (10, 120), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return frame
