from PyQt5.QtCore import QThread, pyqtSignal

class CurriculumWorker(QThread):
    """Worker thread for generating curriculums."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ai_service, topic, expertise_level):
        super().__init__()
        self.ai_service = ai_service
        self.topic = topic
        self.expertise_level = expertise_level

    def run(self):
        try:
            curriculum = self.ai_service.generate_curriculum(
                self.topic, 
                self.expertise_level
            )
            self.finished.emit(curriculum)
        except Exception as e:
            self.error.emit(str(e))
