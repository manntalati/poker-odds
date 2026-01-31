from treys import Card, Evaluator

def debug_treys():
    try:
        # Construct the failing hand
        # Hero: Ah, Kh
        # Board: Th, Jh, Qh + 2 randoms
        
        hero = [Card.new('Ah'), Card.new('Kh')]
        board = [Card.new('Th'), Card.new('Jh'), Card.new('Qh')]
        
        # Add 2 placeholders to make 5 card board (total 7 cards)
        # Let's try to add cards that DON'T make a flush first to see if it works
        board_safe = board + [Card.new('2c'), Card.new('3d')]
        
        evaluator = Evaluator()
        print("Evaluating safe board (Flush exists: Ah Kh Th Jh Qh)...")
        score = evaluator.evaluate(board_safe, hero)
        print(f"Score: {score}, Rank: {evaluator.class_to_string(evaluator.get_rank_class(score))}")
        
        # Now try the case where we might have issues.
        # Actually the above case IS the Royal Flush case.
        
        # Let's try pure Royal Flush on board
        board_royal = [Card.new('Ah'), Card.new('Kh'), Card.new('Th'), Card.new('Jh'), Card.new('Qh')]
        hand_dummy = [Card.new('2c'), Card.new('3d')]
        print("Evaluating Royal Flush on board...")
        score = evaluator.evaluate(board_royal, hand_dummy)
        print(f"Score: {score}, Rank: {evaluator.class_to_string(evaluator.get_rank_class(score))}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_treys()
