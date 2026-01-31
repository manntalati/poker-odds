from treys import Card, Evaluator, Deck

class PokerEngine:
    def __init__(self):
        self.evaluator = Evaluator()
        self.deck = Deck()
        self.hero_hand = []
        self.community_cards = []
        self.num_players = 2 # Default to heads up

    def update_state(self, detected_cards):
        # detected_cards is a list of dicts: {'label': 'Ah', 'conf': 0.9, 'bbox': [...]}
        if not detected_cards:
            self.hero_hand = []
            self.community_cards = []
            return

        # Sort cards by Y-coordinate (bbox y2) descending
        # Assuming hero cards are closer to the bottom of the screen
        sorted_cards = sorted(detected_cards, key=lambda x: x['bbox'][3], reverse=True)
        
        # Simple heuristic: 
        # First 2 cards (closest to bottom) are Hero Hand
        # Next 3-5 cards are Community Cards
        
        # Reset simple state
        current_hand_strs = []
        current_board_strs = []
        
        # Check if we have at least 2 cards for a hand
        if len(sorted_cards) >= 2:
            current_hand_strs = [c['label'] for c in sorted_cards[:2]]
        
        # Remaining cards are board
        if len(sorted_cards) > 2:
            # Take up to 5 cards for board
            current_board_strs = [c['label'] for c in sorted_cards[2:7]]

        # Convert to Treys Card objects safely
        try:
            self.hero_hand = [Card.new(c) for c in current_hand_strs]
            self.community_cards = [Card.new(c) for c in current_board_strs]
        except KeyError as e:
            print(f"Error converting cards: {e}")
            self.hero_hand = []
            self.community_cards = []

    def calculate_odds(self):
        if len(self.hero_hand) != 2:
            return {
                "win_rate": 0.0,
                "tie_rate": 0.0,
                "stage": "Waiting for Hand"
            }

        # Determine stage
        stage = "Pre-Flop"
        if len(self.community_cards) == 3:
            stage = "Flop"
        elif len(self.community_cards) == 4:
            stage = "Turn"
        elif len(self.community_cards) == 5:
            stage = "River"
            
        # If pre-flop, we can use a lookup table or just run a quick sim
        # but for now let's just do a Monte Carlo sim for all stages
        iterations = 1000 # Increase for better accuracy, decrease for speed
        
        return self._run_monte_carlo(iterations, stage)

    def _run_monte_carlo(self, iterations, stage):
        wins = 0
        ties = 0
        
        # Prepare valid deck
        full_deck = Deck()
        known_cards = self.hero_hand + self.community_cards
        
        # Filter only valid cards from deck and exclude known
        # Sanity check: prime must be >= 2
        available_cards = []
        for c in full_deck.cards:
            if c in known_cards:
                continue
            # Prime check (bits 0-7)
            prime = c & 0xFF
            if prime < 2:
                # Skip invalid card
                continue
            available_cards.append(c)
        
        # Also validate hero_hand and community_cards?
        # If they are invalid, score calculation will fail anyway. 
        # But let's assume update_state handled them reasonably.
        
        import random
        
        for _ in range(iterations):
            try:
                random.shuffle(available_cards)
                
                # Opponent hand
                opp_hand = available_cards[:2]
                
                # Remaining board
                board_needed = 5 - len(self.community_cards)
                # Ensure we have enough cards
                if len(available_cards) < 2 + board_needed:
                    continue

                board_fill = available_cards[2:2+board_needed]
                
                sim_board = self.community_cards + board_fill
                
                hero_score = self.evaluator.evaluate(sim_board, self.hero_hand)
                opp_score = self.evaluator.evaluate(sim_board, opp_hand)
                
                if hero_score < opp_score:
                    wins += 1
                elif hero_score == opp_score:
                    ties += 1
            except Exception as e:
                # KeyError in Treys is possible for rare hands due to library issues
                # Skip this iteration
                # print(f"Sim error: {e}")
                continue
                
        if iterations == 0:
            return {"win_rate": 0, "tie_rate": 0, "stage": stage}
            
        win_rate = (wins / iterations) * 100
        tie_rate = (ties / iterations) * 100
        
        return {
            "win_rate": win_rate,
            "tie_rate": tie_rate,
            "stage": stage
        }
