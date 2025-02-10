from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, QFrame)


class CurriculumReviewTab(QWidget):
    def __init__(self, parent=None, topic="", expertise_level=""):
        super().__init__(parent)
        self.parent = parent
        self.topic = topic
        self.expertise_level = expertise_level
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel(f"Review Curriculum: {self.topic}")
        header.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Info section
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout()
        
        level_label = QLabel(f"Level: {self.expertise_level}")
        level_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        info_layout.addWidget(level_label)
        
        info_container.setLayout(info_layout)
        layout.addWidget(info_container)

        # Curriculum content
        content_container = QFrame()
        content_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        content_layout = QVBoxLayout()
        
        self.curriculum_content = QTextEdit()
        self.curriculum_content.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.curriculum_content.setPlaceholderText("Loading curriculum...")
        self.curriculum_content.setReadOnly(False)  # Allow editing
        content_layout.addWidget(self.curriculum_content)
        
        content_container.setLayout(content_layout)
        layout.addWidget(content_container)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.modify_button = QPushButton("Save Changes")
        self.start_button = QPushButton("Start Learning")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ea043;
            }
            QPushButton:hover {
                background-color: #3fb950;
            }
        """)
        
        button_layout.addWidget(self.modify_button)
        button_layout.addWidget(self.start_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

        # Connect signals
        self.start_button.clicked.connect(self.start_learning)
        self.modify_button.clicked.connect(self.save_changes)

    def set_curriculum_content(self, content):
        """Update the curriculum content."""
        self.curriculum_content.setPlainText(content)

    def save_changes(self):
        """Save modifications to the curriculum."""
        content = self.curriculum_content.toPlainText()
        print(f"Saving changes to curriculum for {self.topic}")
        # TODO: Save changes to backend

    def start_learning(self):
        """Start the learning session with this curriculum."""
        # Create a new learning session tab
        self.parent.create_learning_session(self.topic, self.expertise_level, 
                                         self.curriculum_content.toPlainText())
