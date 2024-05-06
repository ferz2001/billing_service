import logging
import asgi_correlation_id

from core.config import cfg


class LoggerSetup:
    def __init__(self):
        self.logger = logging.getLogger('movies_api')
        self.setup_logger()

    def setup_logger(self):
        self.logger.setLevel(cfg.log_level)
        
        format_ = ('{"time": "%(asctime)s",'
                   '"name": "%(name)s",'
                   '"request_id": "%(correlation_id)s",'
                   '"levelname": "%(levelname)s",'
                   '"message": "%(message)s"}')

        file = logging.FileHandler('logs/app.log')
        console = logging.StreamHandler()
        
        file.addFilter(asgi_correlation_id.CorrelationIdFilter())
        console.addFilter(asgi_correlation_id.CorrelationIdFilter())

        formatter = logging.Formatter(format_)

        file.setFormatter(formatter)
        console.setFormatter(formatter)

        self.logger.addHandler(file)
        self.logger.addHandler(console)
