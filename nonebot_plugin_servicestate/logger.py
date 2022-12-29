class Logger:
    def __init__(self) -> None:
        pass

    def debug(self, desc: str):
        print("[DEBUG]" + desc)

    def info(self, desc: str):
        print("[INFO]" + desc)

    def warning(self, desc: str):
        print("[WARNING]" + desc)

    def error(self, desc: str):
        print("[ERROR]" + desc)


def set_logger(logger_module):
    global logger
    logger = logger_module


logger = Logger()
