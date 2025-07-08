from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from whisper_runner import transcribe_whisper
from audio_recorder import record_audio
from model_viewer import ModelViewer
from model_selector import ModelSelector
from utils import resource_path
import os, sys, multiprocessing


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Desktop Prototype")
        self.setGeometry(200, 200, 400, 300)

        self.transcription_label = QLabel("Press record to transcribe...")
        self.record_btn = QPushButton("Record & Transcribe")

        self.record_btn.clicked.connect(self.handle_record)

        model_path = resource_path("viewer_assets/model.glb")
        self.viewer = ModelViewer(model_path)
        self.selector = ModelSelector()

        layout = QVBoxLayout()
        layout.addWidget(self.transcription_label)
        layout.addWidget(self.record_btn)
        layout.addWidget(self.viewer)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_record(self):
        self.transcription_label.setText("Recording...")
        record_audio()
        self.transcription_label.setText("Transcribing...")
        text = transcribe_whisper()
        self.transcription_label.setText(text or "Transcription failed")

        if text:
            model_file, score = self.selector.get_best_match(text)
            if model_file:
                self.transcription_label.setText(f"{text} (matched: {model_file}, score={score:.2f})")
                self.viewer.load_model(model_file)
            else:
                self.transcription_label.setText(f"{text} (no model match)")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
