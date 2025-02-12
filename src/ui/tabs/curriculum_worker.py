from PyQt5.QtCore import QThread, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class CurriculumWorker(QThread):
    """Worker thread for generating curriculums."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ai_service, topic, expertise_level):
        super().__init__()
        self.ai_service = ai_service
        self.topic = topic
        self.expertise_level = expertise_level
        logger.debug(f"Initializing CurriculumWorker for topic='{topic}', level='{expertise_level}'")

    def run(self):
        """Generate curriculum in a background thread."""
        try:
            logger.debug(f"Starting curriculum generation for topic='{self.topic}'")
            curriculum = self.ai_service.generate_curriculum(
                self.topic, 
                self.expertise_level
            )
            logger.debug("Curriculum generation completed successfully")
            self.finished.emit(curriculum)
        except Exception as e:
            logger.error(f"Error generating curriculum: {str(e)}", exc_info=True)
            self.error.emit(str(e))
        finally:
            logger.debug("CurriculumWorker thread finishing")
