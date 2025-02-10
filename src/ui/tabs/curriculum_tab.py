from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QComboBox, 
                            QFrame, QProgressBar)
from services.ai_service import AIService
from .curriculum_worker import CurriculumWorker


class CurriculumTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ai_service = AIService()
        self.init_ui()

    def init_ui(self):
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
        
        self.start_curriculum_button = QPushButton("Start Learning")
        self.start_curriculum_button.setMinimumHeight(40)
        
        form_layout.addWidget(self.topic_label)
        form_layout.addWidget(self.topic_input)
        form_layout.addWidget(self.expertise_label)
        form_layout.addWidget(self.expertise_combo)
        # Progress bar
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
        form_layout.addWidget(self.progress_bar)
        
        form_layout.addWidget(self.start_curriculum_button)
        form_container.setLayout(form_layout)
        
        curriculum_layout.addWidget(form_container)
        curriculum_layout.addStretch()
        self.setLayout(curriculum_layout)

        # Connect signals
        self.start_curriculum_button.clicked.connect(self.handle_new_curriculum)
        self.topic_input.returnPressed.connect(self.handle_new_curriculum)  # Add Enter key support

    def _enable_input(self, enabled: bool):
        """Enable or disable input controls."""
        self.topic_input.setEnabled(enabled)
        self.expertise_combo.setEnabled(enabled)
        self.start_curriculum_button.setEnabled(enabled)

    def _show_error(self, error_message: str):
        """Display an error in the UI."""
        # TODO: Add proper error display
        print(f"Error: {error_message}")
        self.progress_bar.hide()
        self._enable_input(True)

    def _handle_curriculum_generated(self, curriculum: str):
        """Handle the generated curriculum."""
        topic = self.topic_input.text()
        expertise = self.expertise_combo.currentText()

        # Create learning session
        self.parent.create_learning_session(topic, expertise, curriculum)
        
        # Add to history
        self.parent.history_tab.add_curriculum(topic, expertise)
        
        # Reset UI
        self.topic_input.clear()
        self.progress_bar.hide()
        self._enable_input(True)

    def handle_new_curriculum(self):
        topic = self.topic_input.text()
        expertise = self.expertise_combo.currentText()
        if not topic:
            return

        # Disable input and show progress
        self._enable_input(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()

        # Generate curriculum in background
        self.worker = CurriculumWorker(self.ai_service, topic, expertise)
        self.worker.finished.connect(self._handle_curriculum_generated)
        self.worker.error.connect(self._show_error)
        self.worker.start()
    
    def generate_placeholder_curriculum(self, topic, expertise):
        """Generate a placeholder curriculum until backend is implemented."""
        return f"""# Learning Plan: {topic}
Level: {expertise}

## Objectives
1. Understand core concepts of {topic}
2. Apply knowledge in practical scenarios
3. Master advanced techniques

## Topics to Cover
1. Introduction to {topic}
   - Basic concepts
   - Fundamental principles
   - Getting started

2. Core Concepts
   - Key components
   - Best practices
   - Common patterns

3. Advanced Topics
   - Advanced techniques
   - Real-world applications
   - Expert-level concepts

4. Practical Applications
   - Hands-on projects
   - Case studies
   - Problem-solving exercises

Let's begin with the introduction. What would you like to know first?"""
