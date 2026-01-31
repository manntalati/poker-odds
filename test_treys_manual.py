from treys import Card, Evaluator, Deck

def verify_treys():
    try:
        # Create a deck
        deck = Deck()
        
        # Draw a hand
        hand = deck.draw(2)
        print(f"Hand: {[Card.int_to_str(c) for c in hand]}")
        
        # Draw a board
        board = deck.draw(5)
        print(f"Board: {[Card.int_to_str(c) for c in board]}")
        
        # Evaluate hand
        evaluator = Evaluator()
        score = evaluator.evaluate(board, hand)
        rank_class = evaluator.get_rank_class(score)
        print(f"Rank class: {rank_class}")
        print(f"Hand rank: {evaluator.class_to_string(rank_class)}")
        
        # Test specific card creation
        try:
            ah = Card.new('Ah')
            print(f"Ah created successfully: {Card.int_to_str(ah)}")
        except Exception as e:
            print(f"Error creating 'Ah': {e}")
            
        try:
            th = Card.new('Th')
            print(f"Th created successfully: {Card.int_to_str(th)}")
        except Exception as e:
            print(f"Error creating 'Th': {e}")
            
    except Exception as e:
        print(f"Overall Error: {e}")

if __name__ == "__main__":
    verify_treys()
