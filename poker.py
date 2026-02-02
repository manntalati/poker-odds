from treys import Card, Evaluator, Deck

class PokerEngine:
    def __init__(self):
        self.evaluator = Evaluator()
        self.deck = Deck()
        self.hero_hand = []
        self.community_cards = []
        self.num_players = 2 
        self.hero_hand_locked = False
        self.community_locked_count = 0 

    def lock_hero_hand(self):
        if len(self.hero_hand) == 2:
            self.hero_hand_locked = True
            return True
        return False

    def lock_community(self):
        """Locks the currently detected community cards (max 5)"""
        if len(self.community_cards) >= 3:
            self.community_locked_count = len(self.community_cards)
            return True
        return False

    def set_manual_card(self, card_type, index, label):
        """
        Manually set a card. 
        card_type: 'hero' or 'community'
        index: 0 or 1 for hero, 0..4 for community
        label: e.g. 'Ah'
        """
        try:
            card_obj = Card.new(label)
            if card_type == 'hero':
                while len(self.hero_hand) <= index:
                    self.hero_hand.append(None)
                self.hero_hand[index] = card_obj
                # Filter out any Nones if multiple manual sets happened
                self.hero_hand = [c for c in self.hero_hand if c is not None][:2]
            else:
                while len(self.community_cards) <= index:
                    self.community_cards.append(None)
                self.community_cards[index] = card_obj
                self.community_cards = [c for c in self.community_cards if c is not None][:5]
            return True
        except:
            return False

    def reset_hand(self):
        self.hero_hand = []
        self.community_cards = []
        self.hero_hand_locked = False
        self.community_locked_count = 0

    def update_state(self, detected_cards):
        if not detected_cards and not self.hero_hand_locked:
            self.hero_hand = []
            self.community_cards = []
            return
        
        # Sort by x coordinate for community cards (left to right)
        sorted_x = sorted(detected_cards, key=lambda x: x['bbox'][0])
        # Sort by y coordinate for hero (closer to bottom)
        sorted_y = sorted(detected_cards, key=lambda x: x['bbox'][3], reverse=True)
        
        hero_strs = [Card.int_to_str(c) for c in self.hero_hand if c]
        community_strs = [Card.int_to_str(c) for c in self.community_cards if c]

        # 1. Handle Hero Hand
        if not self.hero_hand_locked:
            if len(sorted_y) >= 2:
                try:
                    self.hero_hand = [Card.new(c['label']) for c in sorted_y[:2]]
                except: pass
        
        # 2. Handle Community Cards
        if self.hero_hand_locked:
            # Filter out detections that are already in our hero hand
            candidates = [c['label'] for c in sorted_x if c['label'] not in hero_strs]
            
            if self.community_locked_count == 0:
                # Looking for Flop (3 cards)
                if len(candidates) >= 3:
                    try:
                        self.community_cards = [Card.new(c) for c in candidates[:3]]
                    except: pass
            
            elif self.community_locked_count == 3:
                # Flop is locked. Looking for 1 more (Turn)
                # Keep first 3 from locked, add 1 new one that isn't already in community
                new_candidates = [c for c in candidates if c not in community_strs[:3]]
                if len(new_candidates) >= 1:
                    try:
                        self.community_cards = [Card.new(c) for c in (community_strs[:3] + [new_candidates[0]])]
                    except: pass
                    
            elif self.community_locked_count == 4:
                # Turn is locked. Looking for 1 more (River)
                new_candidates = [c for c in candidates if c not in community_strs[:4]]
                if len(new_candidates) >= 1:
                    try:
                        self.community_cards = [Card.new(c) for c in (community_strs[:4] + [new_candidates[0]])]
                    except: pass

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
            
        iterations = 1000 
        return self._run_monte_carlo(iterations, stage)

    def set_num_players(self, num):
        # Allow setting number of players dynamically
        if num < 2: 
            num = 2
        if num > 9: 
            num = 9
        self.num_players = num

    def _run_monte_carlo(self, iterations, stage):
        wins = 0
        ties = 0
        
        # Prepare valid deck
        full_deck = Deck()
        known_cards = self.hero_hand + self.community_cards
        
        # Filter only valid cards from deck and exclude known
        available_cards = []
        for c in full_deck.cards:
            if c in known_cards:
                continue
            prime = c & 0xFF
            if prime < 2:
                continue
            available_cards.append(c)
        
        import random
        num_opponents = self.num_players - 1
        
        for _ in range(iterations):
            try:
                random.shuffle(available_cards)
                
                # Check if enough cards for opponents + board fill
                cards_needed_opp = num_opponents * 2
                board_needed = 5 - len(self.community_cards)
                
                if len(available_cards) < cards_needed_opp + board_needed:
                    continue

                # Deal to opponents
                opp_hands = []
                current_idx = 0
                for _ in range(num_opponents):
                    hand = available_cards[current_idx : current_idx+2]
                    opp_hands.append(hand)
                    current_idx += 2
                
                # Deal board fill
                board_fill = available_cards[current_idx : current_idx+board_needed]
                sim_board = self.community_cards + board_fill
                
                # Evaluate Hero
                hero_score = self.evaluator.evaluate(sim_board, self.hero_hand)
                
                # Evaluate Opponents
                opp_scores = [self.evaluator.evaluate(sim_board, h) for h in opp_hands]
                
                # Compare
                best_opp_score = min(opp_scores)
                
                if hero_score < best_opp_score: # Lower is better
                    wins += 1
                elif hero_score == best_opp_score:
                    ties += 1
                    
            except Exception as e:
                continue
                
        if iterations == 0:
            return {"win_rate": 0, "tie_rate": 0, "stage": stage}
            
        win_rate = (wins / iterations) * 100
        tie_rate = (ties / iterations) * 100
        
        return {
            "win_rate": win_rate,
            "tie_rate": tie_rate,
            "stage": stage,
            "num_players": self.num_players
        }
