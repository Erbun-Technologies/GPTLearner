from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QTextEdit, 
                            QFrame, QScrollArea, QSplitter, QProgressBar)
from PyQt5.QtCore import Qt
from services.ai_service import AIService
from .chat_worker import ChatWorker


class LearningSessionTab(QWidget):
    def __init__(self, parent=None, topic="", expertise_level="", curriculum=""):
        super().__init__(parent)
        self.parent = parent
        self.topic = topic
        self.expertise_level = expertise_level
        self.curriculum = curriculum
        self.chat_history = []
        self.ai_service = AIService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Curriculum and Progress
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 10, 0)

        # Topic header
        header = QLabel(f"Learning: {self.topic}")
        header.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
        left_layout.addWidget(header)

        # Curriculum view
        curriculum_container = QFrame()
        curriculum_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        curriculum_layout = QVBoxLayout()
        
        curriculum_label = QLabel("Curriculum")
        curriculum_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
        curriculum_layout.addWidget(curriculum_label)
        
        self.curriculum_view = QTextEdit()
        self.curriculum_view.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.curriculum_view.setPlainText(self.curriculum)
        self.curriculum_view.setReadOnly(True)
        curriculum_layout.addWidget(self.curriculum_view)
        
        curriculum_container.setLayout(curriculum_layout)
        left_layout.addWidget(curriculum_container)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right side - Chat Interface
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.chat_display)

        # Progress bar for loading state
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                text-align: center;
                height: 4px;
            }
            QProgressBar::chunk {
                background-color: #2ea043;
            }
        """)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        right_layout.addWidget(self.progress_bar)

        # Chat input area
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.setMinimumHeight(40)
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumHeight(40)
        self.send_button.setMinimumWidth(100)
        
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.send_button)
        right_layout.addLayout(chat_input_layout)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set initial splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        self.setLayout(layout)

        # Connect signals
        self.send_button.clicked.connect(self.handle_send)
        self.chat_input.returnPressed.connect(self.handle_send)

        # Add welcome message
        self.chat_display.append("Assistant: Welcome to your learning session! I'm here to help you learn about "
                               f"{self.topic}. What would you like to know first?\n")

    def _add_user_message(self, message: str):
        """Add a user message to the chat display and history."""
        self.chat_display.append(f"You: {message}\n")
        self.chat_history.append({"role": "user", "content": message})

    def _add_assistant_message(self, message: str):
        """Add an assistant message to the chat display and history."""
        self.chat_display.append(f"Assistant: {message}\n")
        self.chat_history.append({"role": "assistant", "content": message})

    def _show_error(self, error_message: str):
        """Display an error message in the chat."""
        self.chat_display.append(f"Error: {error_message}\n")
        self.progress_bar.hide()
        self._enable_input(True)

    def _enable_input(self, enabled: bool):
        """Enable or disable input controls."""
        self.chat_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

    def handle_send(self):
        """Handle sending a message in the chat."""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Display user message and update history
        self._add_user_message(message)
        
        # Clear input and disable controls
        self.chat_input.clear()
        self._enable_input(False)
        
        # Show progress bar
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.show()

        # Create worker thread for AI response
        self.worker = ChatWorker(self.ai_service, self.chat_history, self.curriculum)
        self.worker.finished.connect(self._handle_ai_response)
        self.worker.error.connect(self._show_error)
        self.worker.start()

    def _handle_ai_response(self, response: str):
        """Handle the AI response."""
        self._add_assistant_message(response)
        self.progress_bar.hide()
        self._enable_input(True)
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
