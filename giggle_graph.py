import sys
import queue
import numpy as np
import sounddevice as sd
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import warnings
warnings.filterwarnings("ignore")

from transformers import pipeline

# Map sound classes to emojis
EMOJI_MAP = {
    "Laughter": "😂",
    "Giggle": "🤣",
    "Baby laughter": "👼😂",
    "Snicker": "🤭",
    "Belly laugh": "🤣",
    "Chuckle, chortle": "🤭",
    "Crying, sobbing": "😭",
    "Whimper": "😢",
    "Groan": "😩",
    "Sigh": "😮‍💨",
    "Cheering": "🎉",
    "Applause": "👏",
    "Screaming": "😱",
    "Yell": "🤬"
}

class InferenceThread(QThread):
    emoji_signal = pyqtSignal(str)

    def __init__(self, audio_queue):
        super().__init__()
        self.audio_queue = audio_queue
        print("Loading AST Model (this might take a few seconds)...")
        # We specify device=-1 to run on CPU, which is usually safer for this pipeline unless mps is explicitly supported
        self.classifier = pipeline("audio-classification", model="MIT/ast-finetuned-audioset-10-10-0.4593", device=-1)
        print("Model Loaded!")
        self.running = True

    def run(self):
        while self.running:
            try:
                # Wait for an audio chunk
                chunk = self.audio_queue.get(timeout=1)
                
                # Model expects 16kHz float32 audio
                predictions = self.classifier(chunk)
                
                # Check predictions
                best_pred = predictions[0] # Highest confidence
                label = best_pred["label"]
                score = best_pred["score"]
                
                print(f"Detected: {label} (Score: {score:.2f})")
                
                # If score > 0.10 and label is in our map, trigger emoji
                if score > 0.10 and label in EMOJI_MAP:
                    emoji = EMOJI_MAP[label]
                    self.emoji_signal.emit(emoji)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Inference error: {e}")

    def stop(self):
        self.running = False


class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set window properties for transparent, always-on-top, click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool  # Prevents showing in taskbar/dock sometimes
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Make the window fullscreen
        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())

    def spawn_emoji(self, emoji):
        # Spawn multiple emojis for effect
        num_emojis = random.randint(3, 8)
        for _ in range(num_emojis):
            label = QLabel(emoji, self)
            label.setFont(QFont("Apple Color Emoji", random.randint(40, 80)))
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            label.show()

            # Random starting position at the top
            start_x = random.randint(0, self.width() - 100)
            start_y = -100
            
            # Random ending position at the bottom
            end_x = start_x + random.randint(-200, 200)
            end_y = self.height() + 100
            
            # Duration based on "weight"
            duration = random.randint(2000, 4000)

            anim = QPropertyAnimation(label, b"pos")
            anim.setDuration(duration)
            anim.setStartValue(QPoint(start_x, start_y))
            anim.setEndValue(QPoint(end_x, end_y))
            anim.setEasingCurve(QEasingCurve.Type.InQuad)
            
            # Keep reference to avoid garbage collection
            if not hasattr(self, 'animations'):
                self.animations = []
            self.animations.append(anim)
            
            # Remove label after animation
            anim.finished.connect(label.deleteLater)
            anim.finished.connect(lambda a=anim: self.animations.remove(a) if a in self.animations else None)
            
            anim.start()

# Audio callback to put data into queue
def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"Status: {status}")
    # We take the mono channel and flatten it
    audio_data = indata[:, 0].copy()
    audio_q.put(audio_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Global audio queue
    audio_q = queue.Queue()
    
    # 1. Start the UI
    window = OverlayWindow()
    window.show()
    
    # 2. Start Inference Thread
    inference_thread = InferenceThread(audio_q)
    inference_thread.emoji_signal.connect(window.spawn_emoji)
    inference_thread.start()
    
    # 3. Start Audio Stream
    # AST model requires 16000 Hz sample rate. 
    # Let's record in chunks of 2 seconds
    SAMPLE_RATE = 16000
    CHUNK_DURATION = 2  # seconds
    
    print("Starting audio stream...")
    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            blocksize=int(SAMPLE_RATE * CHUNK_DURATION),
            callback=audio_callback,
            dtype='float32'
        )
        
        with stream:
            sys.exit(app.exec())
    except Exception as e:
        print(f"Failed to start audio stream: {e}")
        inference_thread.stop()
