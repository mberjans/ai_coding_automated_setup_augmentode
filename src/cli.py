import argparse
import logging

from src.logging.json_logger import get_logger
from src.logging.handlers import get_console_handler


def build_parser():
    parser = argparse.ArgumentParser(
        prog="src.cli",
        description="Automated LLM-Based Project Planning & Documentation Generation System",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="{run,process-docs,generate,evaluate,combine}")

    subparsers.add_parser("run", help="Execute full pipeline")
    subparsers.add_parser("process-docs", help="Process input documents")
    subparsers.add_parser("generate", help="Generate plans and tickets")
    subparsers.add_parser("evaluate", help="Evaluate attempts")
    subparsers.add_parser("combine", help="Combine multiple attempts")

    return parser


def _cmd_run(logger):
    logger.info("run selected")
    return 0


def _cmd_process_docs(logger):
    logger.info("process-docs selected")
    return 0


def _cmd_generate(logger):
    logger.info("generate selected")
    return 0


def _cmd_evaluate(logger):
    logger.info("evaluate selected")
    return 0


def _cmd_combine(logger):
    logger.info("combine selected")
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # Configure structured JSON logger with console handler.
    logger = get_logger("cli", level="DEBUG")
    logger.handlers = []
    console_level = "DEBUG" if args.verbose else "INFO"
    ch = get_console_handler(level=console_level)
    logger.addHandler(ch)

    # Emit initialization logs used by tests to assert levels.
    logger.info("cli initialized")
    logger.debug("cli initialized debug")

    if args.command is None:
        # No action for now; just parse arguments.
        return 0

    if args.command == "run":
        return _cmd_run(logger)
    if args.command == "process-docs":
        return _cmd_process_docs(logger)
    if args.command == "generate":
        return _cmd_generate(logger)
    if args.command == "evaluate":
        return _cmd_evaluate(logger)
    if args.command == "combine":
        return _cmd_combine(logger)

    # Unknown command
    logger.error("unknown command")
    return 2


if __name__ == "__main__":
    main()
