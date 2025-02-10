from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QTextEdit)


class ChatTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(10)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(400)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        chat_layout.addWidget(self.chat_display)
        
        chat_input_layout = QHBoxLayout()
        chat_input_layout.setSpacing(10)
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.setMinimumHeight(40)
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumHeight(40)
        self.send_button.setMinimumWidth(100)
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.send_button)
        chat_layout.addLayout(chat_input_layout)
        self.setLayout(chat_layout)

        # Connect signals
        self.send_button.clicked.connect(self.handle_send)
        self.chat_input.returnPressed.connect(self.handle_send)

    def handle_send(self):
        message = self.chat_input.text()
        if message:
            self.chat_display.append(f"You: {message}")
            self.chat_input.clear()
            # Placeholder for agent response
            self.chat_display.append(f"\nAssistant: I'm sorry, but I'm not connected to the backend yet. Once implemented, I'll be able to help you learn about your topics!\n")
