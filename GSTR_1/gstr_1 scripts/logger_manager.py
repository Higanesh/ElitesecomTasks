import logging
import platform

class LoggerManager:
    """
    Provides a logger that works across different platforms.
    """
    @staticmethod
    def get_logger(log_file="text.log", logger_name="TcsSalesProcessor"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        # Avoid adding multiple handlers if already created
        if not logger.handlers:
            system_platform = platform.system().lower()

            # File handler
            file_handler = logging.FileHandler(log_file)
            file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)

            # Console handler for Windows/Linux/Mac
            if system_platform in ["windows", "linux", "darwin"]:
                console_handler = logging.StreamHandler()
                console_format = logging.Formatter("%(levelname)s - %(message)s")
                console_handler.setFormatter(console_format)
                logger.addHandler(console_handler)

        return logger
