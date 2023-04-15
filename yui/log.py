import logging


class GetLoggerMixin:
    def get_logger(self, name: str | None = None) -> logging.Logger:
        names = [self.__class__.__module__, self.__class__.__name__]
        if name:
            names.append(name)
        return logging.getLogger(".".join(names))
