from PyQt5.QtCore import QThread, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class ChatWorker(QThread):
    """Worker thread for handling AI chat responses."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ai_service, messages, curriculum):
        super().__init__()
        self.ai_service = ai_service
        self.messages = messages
        self.curriculum = curriculum

    def run(self):
        try:
            logger.debug("ChatWorker starting chat request")
            response = self.ai_service.chat(
                self.messages,
                self.curriculum
            )
            logger.debug("ChatWorker received response")
            self.finished.emit(response)
        except Exception as e:
            logger.error(f"ChatWorker error: {str(e)}")
            self.error.emit(str(e))
