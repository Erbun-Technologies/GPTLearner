def apply_styles(widget):
    """Apply the application-wide styles to the widget."""
    widget.setStyleSheet("""
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
