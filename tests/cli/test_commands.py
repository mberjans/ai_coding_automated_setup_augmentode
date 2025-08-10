import pytest

from src.cli import build_parser, main


def test_cli_parses_subcommands_without_error(capsys):
    parser = build_parser()
    # Ensure subcommands are present via parsing each
    for cmd in ["run", "process-docs", "generate", "evaluate", "combine"]:
        args = parser.parse_args([cmd])
        assert args.command == cmd


def test_cli_main_initializes_logger_and_accepts_commands(capsys):
    # Each command should initialize and not raise
    for cmd in ["run", "process-docs", "generate", "evaluate", "combine"]:
        main(["--verbose", cmd])  # global flag must precede subcommand
        out, err = capsys.readouterr()
        # We expect at least the info init line printed to console handler
        assert "cli initialized" in out or "cli initialized" in err
