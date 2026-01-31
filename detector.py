from ultralytics import YOLO

class CardDetector:
    def __init__(self, model_path='yolov8s_playing_cards.pt'):
        try:
            self.model = YOLO(model_path)
            # Ensure model names are loaded
            self.names = self.model.names
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def detect(self, frame):
        """
        Detects cards in the frame.
        Returns a list of tuples: (card_label, confidence, bbox)
        card_label in Treys format: e.g. 'Ah', 'Ks', 'Th', '2c'
        bbox is [x1, y1, x2, y2]
        """
        detected_cards = []
        if self.model is None:
            return detected_cards

        results = self.model(frame, verbose=False)
        
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                label = self.names[cls_id]
                
                # Convert label to Treys format
                treys_label = self._convert_to_treys(label)
                
                if treys_label:
                    # coords
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detected_cards.append({
                        'label': treys_label,
                        'conf': conf,
                        'bbox': (x1, y1, x2, y2)
                    })
        
        return detected_cards

    def _convert_to_treys(self, label):
        """
        Converts YOLO label (e.g., '10C', 'KH') to Treys format ('Th', 'Kh').
        Returns None if invalid.
        """
        if len(label) < 2:
            return None
        
        rank = label[:-1]
        suit = label[-1]
        
        # Mapping ranks
        if rank == '10':
            rank = 'T'
        
        # Mapping suits
        suit = suit.lower()
        
        return f"{rank}{suit}"
