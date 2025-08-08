# Structured Logging

This project uses a structured JSON logger that emits one valid JSON object per line.

- Keys: `level`, `message`, `name`, `correlation_id`
- Redaction:
  - Any environment variable names and values found within the message are replaced with `[REDACTED]`.
  - Any substring following `key=` (until next space or end of string) is replaced with `[REDACTED]`.
- Correlation ID: a per-run `correlation_id` is attached to every record to correlate logs across the same execution.

## Usage

### In Code

```python
from src.logging.json_logger import get_logger
from src.logging.handlers import get_console_handler, get_file_handler

logger = get_logger("my.module", level="INFO")
logger.handlers = []
logger.addHandler(get_console_handler(level="INFO"))
logger.addHandler(get_file_handler("logs/app.log"))

logger.info("starting")
logger.debug("debug info not shown at INFO level")
```

### In CLI

`src/cli.py` wires the logger by default and supports `--verbose` to elevate console logging to DEBUG.

```bash
python -m src.cli run
python -m src.cli --verbose run
```

## Notes

- Handlers emit `%(message)s` only; JSON is injected at record creation.
- Avoid including secrets in log messages. Redaction is best-effort but not a license to log secrets.
- Log files are written using a rotating file handler via `get_file_handler()`.
