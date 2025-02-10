import sys
from PyQt5.QtWidgets import (QApplication, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QComboBox, QListWidget, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor


class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agentic Learning Assistant")
        self.resize(1000, 700)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Chat Tab
        self.chat_tab = QWidget()
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
        self.chat_tab.setLayout(chat_layout)

        # New Curriculum Tab
        self.curriculum_tab = QWidget()
        curriculum_layout = QVBoxLayout()
        curriculum_layout.setContentsMargins(20, 20, 20, 20)
        curriculum_layout.setSpacing(20)
        
        # Create a form-like container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        self.topic_label = QLabel("Enter topic for new curriculum:")
        self.topic_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.topic_input = QLineEdit()
        self.topic_input.setMinimumHeight(40)
        self.topic_input.setPlaceholderText("e.g., Python Programming, Machine Learning, Web Development...")
        
        self.expertise_label = QLabel("Select your expertise level:")
        self.expertise_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.expertise_combo = QComboBox()
        self.expertise_combo.setMinimumHeight(40)
        self.expertise_combo.addItems(["Beginner", "Intermediate", "Advanced"])
        
        self.start_curriculum_button = QPushButton("Start Curriculum")
        self.start_curriculum_button.setMinimumHeight(40)
        
        form_layout.addWidget(self.topic_label)
        form_layout.addWidget(self.topic_input)
        form_layout.addWidget(self.expertise_label)
        form_layout.addWidget(self.expertise_combo)
        form_layout.addWidget(self.start_curriculum_button)
        form_container.setLayout(form_layout)
        
        curriculum_layout.addWidget(form_container)
        curriculum_layout.addStretch()
        self.curriculum_tab.setLayout(curriculum_layout)

        # History Tab
        self.history_tab = QWidget()
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(20, 20, 20, 20)
        history_layout.setSpacing(10)
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #3d3d3d;
            }
        """)
        history_layout.addWidget(self.history_list)
        self.history_tab.setLayout(history_layout)

        # Add tabs to QTabWidget
        self.addTab(self.curriculum_tab, "New Curriculum")
        self.addTab(self.chat_tab, "Chat")
        self.addTab(self.history_tab, "History")

        # Connect signals
        self.send_button.clicked.connect(self.handle_send)
        self.chat_input.returnPressed.connect(self.handle_send)
        self.start_curriculum_button.clicked.connect(self.handle_new_curriculum)

    def apply_styles(self):
        # Set the base style for the entire application
        self.setStyleSheet("""
            QTabWidget {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #808080;
                padding: 8px 20px;
                border: none;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1984d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QComboBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 10px;
            }
        """)

    def handle_send(self):
        message = self.chat_input.text()
        if message:
            self.chat_display.append(f"You: {message}")
            self.chat_input.clear()
            # Placeholder for agent response
            self.chat_display.append(f"\nAssistant: I'm sorry, but I'm not connected to the backend yet. Once implemented, I'll be able to help you learn about your topics!\n")

    def handle_new_curriculum(self):
        topic = self.topic_input.text()
        expertise = self.expertise_combo.currentText()
        if topic:
            self.history_list.addItem(f"📚 {topic} - {expertise} Level")
            print(f"New curriculum started: {topic}, Level: {expertise}")
            self.topic_input.clear()
            self.setCurrentIndex(1)  # Switch to chat tab


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style as base
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
