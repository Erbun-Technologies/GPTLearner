from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextBrowser, QFrame)
from PyQt5.QtCore import Qt
import markdown


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
        """Update the curriculum content with markdown rendering."""
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
