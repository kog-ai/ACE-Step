import contextvars
import json
import logging
import os
import traceback

logger = logging.getLogger(__name__)

correlation_id_var = contextvars.ContextVar("correlation_id", default=None)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "correlation_id": getattr(
                record, "correlation_id", correlation_id_var.get()
            ),  # Ensure correlation_id is present
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        if record.name == __name__ and record.levelname == "DEBUG":
            try:
                perf_data = json.loads(record.getMessage())
                if isinstance(perf_data, dict) and perf_data.get("level") == "PERF":
                    log_record.update(perf_data)
                    del log_record["message"]

            except json.JSONDecodeError:
                pass  # Keep original message if it's not JSON

        return json.dumps(log_record)

    def formatException(self, exc_info):
        return "".join(traceback.format_exception(*exc_info))

    def formatStack(self, stack_info):
        return "".join(traceback.StackSummary.extract(stack_info).format())


def log_perf(event, function, duration=None):
    log_data = {
        "level": "PERF",
        "event": event,
        "function": function,
    }
    if duration is not None:
        log_data["duration"] = duration

    logger.debug(json.dumps(log_data))


###
# logging
###
def setup_logging(root=False):
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level_str, logging.INFO)

    formatter = JsonFormatter()

    if root:
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationIdFilter())
        root_logger.addHandler(handler)

        return root_logger

    module_logger = logging.getLogger("kog_ace_step")
    module_logger.setLevel(numeric_level)

    if module_logger.hasHandlers():
        module_logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter())
    module_logger.addHandler(handler)

    module_logger.propagate = False  # Prevent propagation to the root logger if configured by another module

    return module_logger
