import logging
import sys
import os

def setup_logger(name: str = "TextHelper"):
    """
    Setup centralized logging configuration
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to avoid duplicates
    if logger.handlers:
        return logger
        
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (Optional - for persistent logs)
    # log_dir = "logs"
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)
    # file_handler = logging.FileHandler(os.path.join(log_dir, "texthelper.log"), encoding='utf-8')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger()
