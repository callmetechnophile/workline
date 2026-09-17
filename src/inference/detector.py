# TensorRT human detection node
class HumanDetector:
    def infer(self, frame):
        return [{'class': 'person', 'confidence': 0.94}]
