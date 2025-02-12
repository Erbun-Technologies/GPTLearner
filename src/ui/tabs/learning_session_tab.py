from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QTextBrowser,
                            QFrame, QSplitter, QProgressBar, QListWidget,
                            QStyledItemDelegate, QStyle, QListWidgetItem,
                            QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QRectF
from PyQt5.QtGui import QTextDocument, QPalette, QColor, QPainter, QPainterPath, QIcon
import markdown
from datetime import datetime
from services.ai_service import AIService
from .chat_worker import ChatWorker


class CurriculumTreeView(QTreeWidget):
    """Interactive curriculum view with progress tracking."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.progress = {}  # Track progress for each item
        
    def init_ui(self):
        """Initialize the tree view UI."""
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #2d2d2d;
            }
            QTreeWidget::item:selected {
                background-color: #2c4159;
                color: #ffffff;
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: url(none);
                border-image: none;
                padding-top: 2px;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: url(none);
                border-image: none;
                padding-top: 2px;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed::indicator,
            QTreeWidget::branch:closed:has-children:has-siblings::indicator {
                position: absolute;
                content: "+";
                color: #58a6ff;
            }
            QTreeWidget::branch:open:has-children:!has-siblings::indicator,
            QTreeWidget::branch:open:has-children:has-siblings::indicator {
                position: absolute;
                content: "-";
                color: #58a6ff;
            }
            QTreeWidget::branch:has-siblings {
                border-left: 1px solid #3d3d3d;
            }
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
            }
        """)
        
    def parse_curriculum(self, curriculum: str):
        """Parse markdown curriculum into tree structure with progress tracking."""
        print(f"Parsing curriculum content: {curriculum[:200]}...")  # Debug print
        self.clear()
        self.progress.clear()
        
        # Parse markdown to extract structure
        lines = curriculum.split('\n')
        current_items = {}  # Level -> Parent item mapping
        current_level = 0
        current_indent = 0
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Calculate indentation level
            indent = len(line) - len(line.lstrip())
            if indent > current_indent:
                current_level += 1
            elif indent < current_indent:
                current_level = max(1, current_level - 1)
            current_indent = indent
            
            # Clean the line
            line = line.strip()
            
            # Calculate heading level and text
            level = current_level
            text = line.strip()
            
            if line.startswith('#'):
                level = 1  # All headers are top level
                text = line.lstrip('#').strip()
            elif line.startswith('-') or line.startswith('*'):
                text = line.lstrip('-').lstrip('*').strip()
            elif line[0].isdigit() and '.' in line:
                text = line.split('.', 1)[1].strip()
            
            print(f"Processing line: indent={indent}, level={level}, text={text}")  # Debug print
                
            # Create tree item
            item = QTreeWidgetItem()
            item.setText(0, text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            
            # Store in progress tracking
            self.progress[text] = {
                'completed': False,
                'item': item,
                'level': level
            }
            
            # Add to appropriate parent
            if level == 1 or not current_items:
                # Top level item
                print(f"Adding top level item: {text}")  # Debug print
                self.addTopLevelItem(item)
                current_items = {1: item}
            else:
                # Find appropriate parent
                parent_level = level - 1
                while parent_level > 0 and parent_level not in current_items:
                    parent_level -= 1
                
                if parent_level > 0 and parent_level in current_items:
                    print(f"Adding child item: {text} to parent: {current_items[parent_level].text(0)}")  # Debug print
                    current_items[parent_level].addChild(item)
                    current_items[level] = item
                else:
                    # If no parent found, add as top level item
                    print(f"No parent found, adding as top level: {text}")  # Debug print
                    self.addTopLevelItem(item)
                    current_items = {1: item}
            
        print(f"Total items added: {len(self.progress)}")  # Debug print
        self.expandAll()
        self.update_progress()
        
    def update_progress(self):
        """Update progress indicators for all items."""
        total_items = len(self.progress)
        completed_items = sum(1 for info in self.progress.values() if info['completed'])
        overall_progress = (completed_items / total_items) * 100 if total_items > 0 else 0
        
        # Update individual items
        for text, info in self.progress.items():
            item = info['item']
            if info['completed']:
                item.setIcon(0, self.style().standardIcon(QStyle.SP_DialogApplyButton))
                item.setForeground(0, QColor('#2ea043'))
            else:
                item.setIcon(0, QIcon())
                item.setForeground(0, QColor('#ffffff'))
                
        return overall_progress
        
    def mark_completed(self, text: str):
        """Mark a curriculum item as completed."""
        if text in self.progress:
            self.progress[text]['completed'] = True
            self.update_progress()
            
    def get_section_content(self, text: str) -> str:
        """Get the detailed content for a section."""
        if text in self.progress:
            item = self.progress[text]['item']
            content = []
            child_count = item.childCount()
            
            content.append(f"# {text}")
            
            # Add description if it exists
            description = item.data(0, Qt.UserRole)
            if description:
                content.append(description)
            
            # Add child items
            if child_count > 0:
                content.append("\nSubtopics:")
                for i in range(child_count):
                    child = item.child(i)
                    content.append(f"- {child.text(0)}")
                    child_desc = child.data(0, Qt.UserRole)
                    if child_desc:
                        content.append(f"  {child_desc}")
                
            return "\n".join(content)
        return ""


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

        # Curriculum container
        curriculum_container = QFrame()
        curriculum_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        curriculum_layout = QVBoxLayout()
        
        # Header with progress
        header_layout = QHBoxLayout()
        curriculum_label = QLabel("Curriculum")
        curriculum_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(curriculum_label)
        
        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet("color: #58a6ff; font-size: 14px;")
        header_layout.addWidget(self.progress_label)
        header_layout.addStretch()
        curriculum_layout.addLayout(header_layout)
        
        # Progress bar
        self.curriculum_progress = QProgressBar()
        self.curriculum_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                text-align: center;
                height: 4px;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #58a6ff;
            }
        """)
        self.curriculum_progress.setTextVisible(False)
        curriculum_layout.addWidget(self.curriculum_progress)
        
        # Tree view for curriculum
        self.curriculum_tree = CurriculumTreeView()
        self.curriculum_tree.itemClicked.connect(self._handle_section_click)
        curriculum_layout.addWidget(self.curriculum_tree)
        
        # Section content view
        self.section_content = QTextBrowser()
        self.section_content.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
            QTextBrowser a {
                color: #58a6ff;
            }
        """)
        self.section_content.setMaximumHeight(200)
        curriculum_layout.addWidget(self.section_content)
        
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

        # Parse and display curriculum
        self.curriculum_tree.parse_curriculum(self.curriculum)
        self._update_progress(0)

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

    def _handle_section_click(self, item: QTreeWidgetItem, column: int):
        """Handle clicking on a curriculum section."""
        text = item.text(0)
        content = self.curriculum_tree.get_section_content(text)
        if content:
            # Convert to HTML with styling
            html = markdown.markdown(content)
            styled_html = f"""
            <style>
                body {{
                    color: #ffffff;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }}
                h1 {{ 
                    color: #58a6ff;
                    font-size: 18px;
                    margin: 0 0 10px 0;
                }}
                ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                li {{
                    color: #cccccc;
                    margin: 5px 0;
                }}
            </style>
            {html}
            """
            self.section_content.setHtml(styled_html)
            
            # Mark as completed when clicked
            self.curriculum_tree.mark_completed(text)
            progress = self.curriculum_tree.update_progress()
            self._update_progress(progress)
            
    def _update_progress(self, progress: float):
        """Update progress indicators."""
        self.curriculum_progress.setValue(int(progress))
        self.progress_label.setText(f"{int(progress)}%")
