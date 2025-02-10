from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget)


class HistoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
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
        self.setLayout(history_layout)

    def add_curriculum(self, topic, expertise):
        """Add a new curriculum to the history list."""
        self.history_list.addItem(f"📚 {topic} - {expertise} Level")
