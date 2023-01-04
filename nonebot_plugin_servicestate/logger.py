class logger:
    @staticmethod
    def debug(desc: str):
        print("[DEBUG]" + desc)

    @staticmethod
    def info(desc: str):
        print("[INFO]" + desc)

    @staticmethod
    def warning(desc: str):
        print("[WARNING]" + desc)

    @staticmethod
    def error(desc: str):
        print("[ERROR]" + desc)


def set_logger(logger_module):
    global logger
    logger = logger_module
