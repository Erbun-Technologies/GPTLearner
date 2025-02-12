from PyQt5.QtWidgets import (QTabWidget, QWidget)
from .tabs.curriculum_tab import CurriculumTab
from .tabs.learning_session_tab import LearningSessionTab
from .tabs.history_tab import HistoryTab
from .tabs.curriculum_review_tab import CurriculumReviewTab
from .styles import apply_styles


class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agentic Learning Assistant")
        self.learning_sessions = {}  # Keep track of active learning sessions
        self.review_tabs = {}  # Keep track of review tabs
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

    def create_curriculum_review(self, topic: str, expertise_level: str, curriculum: str) -> None:
        """Create a new curriculum review tab."""
        # If a review tab already exists for this topic, remove it
        if topic in self.review_tabs:
            review_tab = self.review_tabs[topic]
            index = self.indexOf(review_tab)
            self.removeTab(index)
            review_tab.deleteLater()
            del self.review_tabs[topic]

        # Create and add the new review tab
        review_tab = CurriculumReviewTab(self, topic, expertise_level)
        self.review_tabs[topic] = review_tab
        index = self.addTab(review_tab, f"Review: {topic}")
        self.setCurrentIndex(index)
        
        # Set the curriculum content
        review_tab.set_curriculum_content(curriculum)

    def create_learning_session(self, topic, expertise_level, curriculum):
        """Create a new learning session tab."""
        if topic in self.learning_sessions:
            # Switch to existing session
            self.setCurrentWidget(self.learning_sessions[topic])
            return

        # Remove the review tab if it exists
        if topic in self.review_tabs:
            review_tab = self.review_tabs[topic]
            index = self.indexOf(review_tab)
            self.removeTab(index)
            review_tab.deleteLater()
            del self.review_tabs[topic]

        session_tab = LearningSessionTab(self, topic, expertise_level, curriculum)
        self.learning_sessions[topic] = session_tab
        index = self.addTab(session_tab, f"Learning: {topic}")
        self.setCurrentIndex(index)
