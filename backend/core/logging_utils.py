import json
import logging
from datetime import datetime
from typing import Any


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        **{key: value for key, value in fields.items() if value is not None},
    }
    logger.info(json.dumps(payload, default=str))
