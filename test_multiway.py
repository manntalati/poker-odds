from poker import PokerEngine
from treys import Card

def verify_multiway():
    try:
        poker = PokerEngine()
        
        # Scenario: Pocket Aces (Ah As)
        # Pre-flop
        poker.hero_hand = [Card.new('Ah'), Card.new('As')]
        poker.community_cards = []
        
        # Test 1: Heads Up (2 players)
        poker.set_num_players(2)
        odds_hu = poker.calculate_odds()
        print(f"Heads Up (2 players) Win%: {odds_hu['win_rate']:.2f}%")
        
        # Test 2: 3-Way (3 players)
        poker.set_num_players(3)
        odds_3way = poker.calculate_odds()
        print(f"3-Way (3 players) Win%: {odds_3way['win_rate']:.2f}%")
        
        # Test 3: 6-Max (6 players)
        poker.set_num_players(6)
        odds_6max = poker.calculate_odds()
        print(f"6-Max (6 players) Win%: {odds_6max['win_rate']:.2f}%")
        
        # Verification Logic
        if odds_hu['win_rate'] > odds_3way['win_rate'] > odds_6max['win_rate']:
            print("SUCCESS: Win rate decreases as players increase.")
        else:
            print("FAILURE: Win rate trend is incorrect.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_multiway()
