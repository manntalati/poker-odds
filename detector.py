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
        
        # Detection settings
        self.confidence_threshold = 0.5  # Only accept high-confidence detections
        self.iou_threshold = 0.5  # For removing overlapping boxes

    def detect(self, frame):
        """
        Detects cards in the frame.
        Returns a list of dicts: {'label': 'Ah', 'conf': 0.9, 'bbox': (x1,y1,x2,y2)}
        """
        detected_cards = []
        if self.model is None:
            return detected_cards

        # Run inference with built-in NMS
        results = self.model(frame, verbose=False, conf=self.confidence_threshold, iou=self.iou_threshold)
        
        raw_detections = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                label = self.names[cls_id]
                
                # Convert label to Treys format
                treys_label = self._convert_to_treys(label)
                
                if treys_label:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    raw_detections.append({
                        'label': treys_label,
                        'conf': conf,
                        'bbox': (x1, y1, x2, y2)
                    })
        
        # Deduplicate: If the same card label appears multiple times, keep only highest confidence
        seen_labels = {}
        for det in raw_detections:
            label = det['label']
            if label not in seen_labels or det['conf'] > seen_labels[label]['conf']:
                seen_labels[label] = det
        
        detected_cards = list(seen_labels.values())
        
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
