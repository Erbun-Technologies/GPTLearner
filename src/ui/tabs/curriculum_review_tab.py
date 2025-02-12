from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextBrowser, QFrame, QComboBox)
from PyQt5.QtCore import Qt
import markdown
import logging
from .curriculum_worker import CurriculumWorker

logger = logging.getLogger(__name__)

class CurriculumReviewTab(QWidget):
    def __init__(self, parent=None, topic="", expertise_level=""):
        super().__init__(parent)
        self.parent = parent
        self.topic = topic
        self.expertise_level = expertise_level
        self.worker = None
        logger.debug(f"Initializing CurriculumReviewTab for topic='{topic}', level='{expertise_level}'")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel(f"Review Curriculum: {self.topic}")
        header.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

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
        
        self.curriculum_content = QTextBrowser()
        self.curriculum_content.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
            }
            QTextBrowser a {
                color: #58a6ff;
            }
        """)
        self.curriculum_content.setOpenExternalLinks(True)
        self.curriculum_content.setPlaceholderText("Loading curriculum...")
        self.curriculum_content.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
        )
        content_layout.addWidget(self.curriculum_content)
        
        content_container.setLayout(content_layout)
        layout.addWidget(content_container)

        # Info section with expertise level
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(10)
        
        # Level selection group
        level_group = QHBoxLayout()
        level_group.setSpacing(8)
        
        level_header = QLabel("Expertise Level:")
        level_header.setStyleSheet("color: #58a6ff; font-size: 13px; font-weight: bold;")
        level_group.addWidget(level_header)
        
        self.expertise_combo = QComboBox()
        self.expertise_combo.addItems(["Beginner", "Intermediate", "Advanced"])
        self.expertise_combo.setCurrentText(self.expertise_level)
        self.expertise_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 120px;
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
        level_group.addWidget(self.expertise_combo)
        
        self.regenerate_button = QPushButton("Regenerate")
        self.regenerate_button.setStyleSheet("""
            QPushButton {
                background-color: #2ea043;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #3fb950;
            }
        """)
        self.regenerate_button.clicked.connect(self.regenerate_curriculum)
        level_group.addWidget(self.regenerate_button)
        
        info_layout.addLayout(level_group)
        
        # Level description
        level_descriptions = {
            "Beginner": "Suitable for those new to the subject with no prior knowledge.",
            "Intermediate": "For learners with basic understanding seeking to deepen their knowledge.",
            "Advanced": "Designed for experienced learners ready for complex concepts and applications."
        }
        self.level_description = QLabel(level_descriptions[self.expertise_level])
        self.level_description.setStyleSheet("color: #808080; font-size: 12px; font-style: italic;")
        self.level_description.setWordWrap(True)
        info_layout.addWidget(self.level_description, 1)  # Give description more space
        
        # Connect combo box change to update description
        self.expertise_combo.currentTextChanged.connect(
            lambda text: self.level_description.setText(level_descriptions[text])
        )
        
        info_container.setLayout(info_layout)
        layout.addWidget(info_container)

        # Bottom buttons
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
        """Update the curriculum content with markdown rendering."""
        try:
            # Convert markdown to HTML with extensions
            html = markdown.markdown(
                content,
                extensions=[
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.tables',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.sane_lists'
                ]
            )
            
            # Add comprehensive styling
            styled_html = f"""
            <style>
                body {{
                    line-height: 1.6;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }}
                h1 {{ 
                    color: #58a6ff;
                    font-size: 24px;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    padding-bottom: 5px;
                    border-bottom: 1px solid #3d3d3d;
                }}
                h2 {{ 
                    color: #58a6ff;
                    font-size: 20px;
                    margin-top: 15px;
                    margin-bottom: 8px;
                }}
                h3 {{ 
                    color: #58a6ff;
                    font-size: 16px;
                    margin-top: 12px;
                    margin-bottom: 6px;
                }}
                p {{
                    margin: 8px 0;
                }}
                ul, ol {{
                    margin: 8px 0 8px 25px;
                    padding: 0;
                }}
                li {{
                    margin: 4px 0;
                }}
                li > ul, li > ol {{
                    margin: 4px 0 4px 20px;
                }}
                code {{
                    background-color: #2d2d2d;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: Monaco, "Courier New", monospace;
                }}
                pre {{
                    background-color: #2d2d2d;
                    padding: 12px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                pre code {{
                    padding: 0;
                    background-color: transparent;
                }}
            </style>
            {html}
            """
            self.curriculum_content.setHtml(styled_html)
        except Exception as e:
            self.curriculum_content.setHtml(
                f"""
                <div style='color: #ff6b6b; padding: 20px;'>
                    <h3>Error Displaying Curriculum</h3>
                    <p>There was an error processing the curriculum content: {str(e)}</p>
                </div>
                """
            )

    def save_changes(self):
        """Save modifications to the curriculum."""
        try:
            content = self.curriculum_content.toPlainText()
            if not content.strip():
                raise ValueError("Curriculum content cannot be empty")
                
            print(f"Saving changes to curriculum for {self.topic}")
            # TODO: Save changes to backend
            
            # Show success message
            self.curriculum_content.setHtml(
                f"""
                <div style='color: #2ea043; padding: 20px;'>
                    <p>Changes saved successfully!</p>
                </div>
                {self.curriculum_content.toHtml()}
                """
            )
        except Exception as e:
            self.curriculum_content.setHtml(
                f"""
                <div style='color: #ff6b6b; padding: 20px;'>
                    <h3>Error Saving Changes</h3>
                    <p>{str(e)}</p>
                </div>
                {self.curriculum_content.toHtml()}
                """
            )

    def start_learning(self):
        """Start the learning session with this curriculum."""
        # Create a new learning session tab with the current curriculum content
        self.parent.create_learning_session(
            self.topic, 
            self.expertise_level,
            self.curriculum_content.toPlainText()
        )

    def regenerate_curriculum(self):
        """Regenerate the curriculum with the new expertise level."""
        new_level = self.expertise_combo.currentText()
        if new_level != self.expertise_level:
            logger.info(f"Regenerating curriculum for topic='{self.topic}' with new level='{new_level}'")
            self.expertise_level = new_level
            
            # Clean up previous worker if it exists
            self._cleanup_worker()
            
            # Create new worker
            self.worker = CurriculumWorker(self.parent.curriculum_tab.ai_service, self.topic, new_level)
            self.worker.finished.connect(self.handle_regenerated_curriculum)
            self.worker.error.connect(self.handle_regeneration_error)
            self.worker.start()
            
            # Show loading state
            self.curriculum_content.setPlaceholderText("Regenerating curriculum...")
            self._set_buttons_enabled(False)

    def _cleanup_worker(self):
        """Clean up the worker thread safely."""
        if self.worker is not None:
            logger.debug("Cleaning up previous worker")
            try:
                self.worker.finished.disconnect()
                self.worker.error.disconnect()
                self.worker.deleteLater()
            except Exception as e:
                logger.error(f"Error cleaning up worker: {e}")
            self.worker = None

    def _set_buttons_enabled(self, enabled: bool):
        """Enable or disable all buttons."""
        self.regenerate_button.setEnabled(enabled)
        self.start_button.setEnabled(enabled)
        self.modify_button.setEnabled(enabled)

    def handle_regenerated_curriculum(self, new_curriculum: str):
        """Handle the regenerated curriculum."""
        logger.debug("Received regenerated curriculum")
        self.set_curriculum_content(new_curriculum)
        self._set_buttons_enabled(True)

    def handle_regeneration_error(self, error: str):
        """Handle errors during curriculum regeneration."""
        logger.error(f"Error regenerating curriculum: {error}")
        self.curriculum_content.setHtml(
            f"""
            <div style='color: #ff6b6b; padding: 20px;'>
                <h3>Error Regenerating Curriculum</h3>
                <p>{error}</p>
                <p>Please try again or choose a different expertise level.</p>
            </div>
            """
        )
        self._set_buttons_enabled(True)

    def closeEvent(self, event):
        """Handle cleanup when the tab is closed."""
        logger.debug(f"Closing curriculum review tab for topic='{self.topic}'")
        self._cleanup_worker()
        super().closeEvent(event)
