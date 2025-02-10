from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QTextEdit, 
                            QFrame, QScrollArea, QSplitter)
from PyQt5.QtCore import Qt


class LearningSessionTab(QWidget):
    def __init__(self, parent=None, topic="", expertise_level="", curriculum=""):
        super().__init__(parent)
        self.parent = parent
        self.topic = topic
        self.expertise_level = expertise_level
        self.curriculum = curriculum
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

    def handle_send(self):
        """Handle sending a message in the chat."""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Display user message
        self.chat_display.append(f"You: {message}\n")
        
        # Clear input
        self.chat_input.clear()
        
        # TODO: Integrate with backend for AI responses
        # For now, just echo a placeholder response
        response = f"Assistant: I understand you want to know about '{message}'. "
        response += "Once the backend is integrated, I'll provide a detailed response "
        response += "based on the curriculum and your learning progress.\n"
        self.chat_display.append(response)
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
