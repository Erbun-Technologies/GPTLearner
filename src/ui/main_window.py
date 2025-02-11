from PyQt5.QtWidgets import (QTabWidget, QWidget)
from .tabs.curriculum_tab import CurriculumTab
from .tabs.learning_session_tab import LearningSessionTab
from .tabs.history_tab import HistoryTab
from .styles import apply_styles


class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agentic Learning Assistant")
        self.learning_sessions = {}  # Keep track of active learning sessions
        self.init_ui()
        apply_styles(self)
        self.resize(1200, 900)

    def init_ui(self):
        # Initialize permanent tabs
        self.curriculum_tab = CurriculumTab(self)
        self.history_tab = HistoryTab(self)

        # Add permanent tabs
        self.addTab(self.curriculum_tab, "New Curriculum")
        self.addTab(self.history_tab, "History")

    def create_learning_session(self, topic, expertise_level, curriculum):
        """Create a new learning session tab."""
        if topic in self.learning_sessions:
            # Switch to existing session
            self.setCurrentWidget(self.learning_sessions[topic])
            return

        session_tab = LearningSessionTab(self, topic, expertise_level, curriculum)
        self.learning_sessions[topic] = session_tab
        index = self.addTab(session_tab, f"Learning: {topic}")
        self.setCurrentIndex(index)
