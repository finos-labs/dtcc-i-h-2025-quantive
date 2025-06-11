import logging

class TruncatingFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, max_length=500):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.max_length = max_length

    def format(self, record):
        if isinstance(record.msg, str) and len(record.msg) > self.max_length:
            record.msg = record.msg[:self.max_length] + '...'
        return super().format(record)

formatter = TruncatingFormatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    max_length=500
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("TaxScraper")
logger.setLevel(logging.INFO)
logger.handlers = [handler]
logger.propagate = False