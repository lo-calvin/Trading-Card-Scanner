from ultralytics import YOLO


class Detector:
    def __init__(self, weights_path) -> None:
        self.model = YOLO(weights_path)
        self.model.task = "segment"

    def detect_cards(self, source):
        results = self.model(source)
        return results

    
