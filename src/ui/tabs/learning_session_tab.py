from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QTextBrowser,
                            QFrame, QSplitter, QProgressBar, QListWidget,
                            QStyledItemDelegate, QStyle, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QRectF
from PyQt5.QtGui import QTextDocument, QPalette, QColor, QPainter, QPainterPath
import markdown
from datetime import datetime
from services.ai_service import AIService
from .chat_worker import ChatWorker


class MessageDelegate(QStyledItemDelegate):
    """Custom delegate for rendering chat messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QTextDocument()
        self.max_width = 600  # Maximum message width

    def paint(self, painter: QPainter, option, index):
        """Paint the message item."""
        # Get message data
        msg_data = index.data(Qt.UserRole)
        if not msg_data:
            return

        msg_type = msg_data.get('type', '')
        content = msg_data.get('content', '')
        timestamp = msg_data.get('timestamp', '')
        
        # Prepare painter
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate message width
        available_width = int(option.rect.width() * 0.85)  # 85% of available width
        msg_width = int(min(self.max_width, available_width))
        
        # Prepare text document for content
        self.doc.setTextWidth(msg_width - 30)  # Subtract padding
        self.doc.setHtml(f"<span style='color: white;'>{content}</span>")
        
        # Calculate heights
        msg_height = int(self.doc.size().height())
        total_height = int(msg_height + 25)  # Add space for timestamp
        
        # Create message bubble path
        rect = option.rect
        bubble_rect = QRectF(rect)
        if msg_type == 'user':
            bubble_rect.setRight(rect.right() - 10)
            bubble_rect.setLeft(bubble_rect.right() - msg_width)
        else:
            bubble_rect.setLeft(rect.left() + 10)
            bubble_rect.setRight(bubble_rect.left() + msg_width)
        bubble_rect.setHeight(msg_height + 20)
        
        path = QPainterPath()
        if msg_type == 'user':
            path.addRoundedRect(bubble_rect, 15, 15)
            painter.setBrush(QColor("#58a6ff"))
        elif msg_type == 'assistant':
            path.addRoundedRect(bubble_rect, 15, 15)
            painter.setBrush(QColor("#3d3d3d"))
        else:  # system message
            painter.setBrush(Qt.transparent)
        
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)
        
        # Draw message content
        content_rect = QRect(
            int(bubble_rect.left() + 15),
            int(bubble_rect.top() + 10),
            int(bubble_rect.width() - 30),
            int(msg_height)
        )
        painter.translate(content_rect.topLeft())
        self.doc.drawContents(painter)
        painter.translate(-content_rect.topLeft())
        
        # Draw timestamp
        if timestamp and msg_type != 'system':
            painter.setPen(QColor("#808080"))
            timestamp_rect = QRect(
                int(bubble_rect.left()),
                int(bubble_rect.bottom() + 4),
                int(bubble_rect.width()),
                15
            )
            if msg_type == 'user':
                painter.drawText(timestamp_rect, Qt.AlignRight, timestamp)
            else:
                painter.drawText(timestamp_rect, Qt.AlignLeft, timestamp)
        
        painter.restore()

    def sizeHint(self, option, index):
        """Calculate the size needed for the message."""
        msg_data = index.data(Qt.UserRole)
        if not msg_data:
            return QSize()
        
        # Calculate width
        available_width = option.rect.width() * 0.85
        msg_width = min(self.max_width, available_width)
        
        # Calculate height
        self.doc.setTextWidth(msg_width - 30)
        self.doc.setHtml(msg_data.get('content', ''))
        msg_height = self.doc.size().height()
        
        # Add padding and timestamp space and convert to integer
        total_height = int(msg_height + 35)
        
        return QSize(int(option.rect.width()), total_height)


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
        
        self.curriculum_view = QTextBrowser()
        self.curriculum_view.setStyleSheet("""
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
        self.curriculum_view.setOpenExternalLinks(True)
        
        # Convert markdown to HTML with extensions
        html = markdown.markdown(
            self.curriculum,
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
        self.curriculum_view.setHtml(styled_html)
        curriculum_layout.addWidget(self.curriculum_view)
        
        curriculum_container.setLayout(curriculum_layout)
        left_layout.addWidget(curriculum_container)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right side - Chat Interface
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Chat display with modern styling
        self.chat_display = QListWidget()
        self.chat_display.setFrameStyle(QFrame.NoFrame)
        self.chat_display.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setWordWrap(True)
        self.chat_display.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #3d3d3d;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Set custom delegate for message rendering
        self.message_delegate = MessageDelegate(self.chat_display)
        self.chat_display.setItemDelegate(self.message_delegate)
        
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
                background-color: #58a6ff;
            }
        """)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        right_layout.addWidget(self.progress_bar)

        # Chat input area with modern styling
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        chat_input_layout = QHBoxLayout()
        chat_input_layout.setSpacing(10)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.setMinimumHeight(40)
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 20px;
                padding: 0 15px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #58a6ff;
            }
        """)
        
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumHeight(40)
        self.send_button.setMinimumWidth(100)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #58a6ff;
                border-radius: 20px;
                padding: 0 20px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #6cb0ff;
            }
            QPushButton:pressed {
                background-color: #4a8cd9;
            }
            QPushButton:disabled {
                background-color: #2c4159;
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.send_button)
        input_container.setLayout(chat_input_layout)
        right_layout.addWidget(input_container)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set initial splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        self.setLayout(layout)

        # Connect signals
        self.send_button.clicked.connect(self.handle_send)
        self.chat_input.returnPressed.connect(self.handle_send)
        self.chat_input.textChanged.connect(self._handle_input_change)

        # Add welcome messages
        self._add_system_message("Welcome to your learning session!")
        self._add_assistant_message("I'm here to help you learn about " + self.topic + ". What would you like to know first?")

    def _add_message_item(self, content: str, msg_type: str):
        """Add a message item to the chat display."""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Create list item with message data
        item = QListWidgetItem()
        item.setData(Qt.UserRole, {
            'type': msg_type,
            'content': content,
            'timestamp': timestamp
        })
        
        # Add to list widget
        self.chat_display.addItem(item)
        self.chat_display.scrollToBottom()
        
        # Force layout update
        self.chat_display.updateGeometry()

    def _add_user_message(self, message: str):
        """Add a user message to the chat display and history."""
        self._add_message_item(message, 'user')
        self.chat_history.append({"role": "user", "content": message})

    def _add_assistant_message(self, message: str):
        """Add an assistant message to the chat display and history."""
        self._add_message_item(message, 'assistant')
        self.chat_history.append({"role": "assistant", "content": message})

    def _add_system_message(self, message: str):
        """Add a system message to the chat display."""
        self._add_message_item(message, 'system')

    def _show_error(self, error_message: str):
        """Display an error message in the chat."""
        self._add_message_item(f"Error: {error_message}", 'system')
        self.progress_bar.hide()
        self._enable_input(True)

    def _handle_input_change(self, text: str):
        """Handle changes to the input field."""
        # Enable/disable send button based on input
        self.send_button.setEnabled(bool(text.strip()))

    def _enable_input(self, enabled: bool):
        """Enable or disable input controls."""
        self.chat_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled and bool(self.chat_input.text().strip()))

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
