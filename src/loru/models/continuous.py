import collections

class SlidingWindowRecognizer:
    def __init__(self, window_size=30, debounce_frames=5, confidence_threshold=0.7):
        self.window_size = window_size
        self.debounce_frames = debounce_frames
        self.confidence_threshold = confidence_threshold
        self.buffer = collections.deque(maxlen=window_size)
        self.last_emitted = None
        self.debounce_counter = 0

    def process_frame(self, frame_landmarks):
        self.buffer.append(frame_landmarks)
        if len(self.buffer) < self.window_size:
            return None
        
        # Mock prediction logic
        prediction, confidence = self._mock_predict(list(self.buffer))
        
        if confidence >= self.confidence_threshold:
            if prediction != self.last_emitted:
                if self.debounce_counter >= self.debounce_frames:
                    self.last_emitted = prediction
                    self.debounce_counter = 0
                    return prediction
                else:
                    self.debounce_counter += 1
            else:
                self.debounce_counter = 0
        else:
            self.debounce_counter = 0
            
        return None

    def _mock_predict(self, frames):
        # In a real model, run frames through sequence model
        # Return dummy values for now
        return ("hello", 0.8)

if __name__ == "__main__":
    recognizer = SlidingWindowRecognizer()
    print("Initialized sliding window recognizer with debounce.")