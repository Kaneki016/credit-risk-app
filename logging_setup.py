import logging
import logging.handlers
from pathlib import Path


def configure_logging(log_dir: str = "logs", log_level: int = logging.INFO):
    """Configure root logging to write to console and a rotating file in `log_dir`.

    Call this once at application startup (before other modules create loggers).
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    log_file = log_path / "app.log"

    # Remove existing handlers if re-configuring
    root = logging.getLogger()
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)

    # Rotating file handler
    fh = logging.handlers.RotatingFileHandler(str(log_file), maxBytes=5_000_000, backupCount=5)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)

    root.setLevel(log_level)
    root.addHandler(ch)
    root.addHandler(fh)

    root.info("Logging configured. Logs will be written to %s", log_file)
