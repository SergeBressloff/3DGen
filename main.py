from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QHBoxLayout, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from webex_integration import WebexLoginWidget
import webbrowser
from whisper_runner import transcribe_whisper
from audio_recorder import AudioRecorder
from model_viewer import ModelViewer
from model_selector import ModelSelector
from utils import resource_path
import os, sys, multiprocessing


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speak and See 3D")
        self.setGeometry(600, 600, 600, 500)

        # Title
        self.title = QLabel("Speak and See 3D")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setAlignment(Qt.AlignCenter)

        # Speech
        self.transcription_label = QLabel("Press Speak to See in 3D")
        self.record_btn = QPushButton("Speak")
        self.is_recording = False
        self.audio_recorder = AudioRecorder()
        self.record_btn.clicked.connect(self.toggle_recording)

        # Text
        self.text_label = QLabel("Type Description of Model")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("3D model of a dinosaur")
        self.search_btn = QPushButton("Search Model")
        self.search_btn.clicked.connect(self.handle_text_input)

        self.text_input_layout = QHBoxLayout()
        self.text_input_layout.addWidget(self.text_input)
        self.text_input_layout.addWidget(self.search_btn)

        # Add a stretch or spacer after the button to push everything left
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.text_input_layout.addItem(spacer)

        self.search_result = QLabel("")

        model_path = resource_path("viewer_assets/model.glb")
        self.viewer = ModelViewer(model_path)
        self.selector = ModelSelector()

        # Webex Login
        self.webex_widget = WebexLoginWidget()
        self.webex_widget.access_token_received.connect(self.handle_webex_token)

        self.record_btn.setFixedWidth(120)
        self.search_btn.setFixedWidth(120)
        self.text_input.setMinimumWidth(300)
        self.text_input.setMaximumWidth(480)
        self.text_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # --- Layout Refactor ---
        # Controls/top area (title, buttons, etc.)
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.title)
        controls_layout.addWidget(self.transcription_label)
        controls_layout.addWidget(self.record_btn)
        controls_layout.addWidget(self.text_label)
        controls_layout.addLayout(self.text_input_layout)
        controls_layout.addWidget(self.search_result)
        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)

        # Bottom area: Webex (left) and Model Viewer (right)
        bottom_layout = QHBoxLayout()
        self.webex_widget.setMaximumWidth(350)  # Adjust as needed
        bottom_layout.addWidget(self.webex_widget)
        bottom_layout.addWidget(self.viewer)
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(controls_widget)
        main_layout.addWidget(bottom_widget)
        main_layout.setStretch(0, 0)  # controls
        main_layout.setStretch(1, 1)  # bottom area expands

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.transcription_label.setText("Recording... Click again to stop.")
            self.record_btn.setText("Stop")
            self.audio_recorder.start()
        else:
            self.is_recording = False
            self.transcription_label.setText("Press Speak to See in 3D")
            self.record_btn.setText("Speak")
            self.search_result.setText("Transcribing...")
            self.audio_recorder.stop()
            text = transcribe_whisper()
            self.search_result.setText(text or "Transcription failed")

            if text:
                self.load_model_from_text(text)

    def handle_text_input(self):
        text = self.text_input.text().strip()
        if text:
            self.load_model_from_text(text)
        else:
            self.search_result.setText("Please type something first.")

    def load_model_from_text(self, text):
        model_file, score = self.selector.get_best_match(text)
        if model_file:
            # self.search_result.setText(f"{text} (matched: {model_file}, score={score:.2f})")
            self.viewer.load_model(model_file)
        else:
            self.search_result.setText(f"{text} (no model match)")

    def handle_webex_token(self, token):
        print("Webex access token:", token)
        meeting_url = "https://meet1427.webex.com/meet/pr23652216204"
        self.webex_widget.load_meeting(meeting_url)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
