import pytest

from src.cli import main


def test_main_returns_zero_for_no_command(capsys):
    code = main([])
    out, err = capsys.readouterr()
    assert code == 0
    assert "cli initialized" in out or "cli initialized" in err


def test_main_returns_zero_and_logs_for_each_command(capsys):
    cmds = ["run", "process-docs", "generate", "evaluate", "combine"]
    i = 0
    while i < len(cmds):
        cmd = cmds[i]
        code = main([cmd])
        out, err = capsys.readouterr()
        assert code == 0
        # should include initialized line
        assert "cli initialized" in out or "cli initialized" in err
        # and the command-specific log message
        assert f"{cmd} selected" in out or f"{cmd} selected" in err
        i = i + 1


def test_main_verbose_flag_increases_logging(capsys):
    code = main(["--verbose", "run"])  # global flag before subcommand
    out, err = capsys.readouterr()
    assert code == 0
    # debug line should be present when verbose is set
    assert "cli initialized debug" in out or "cli initialized debug" in err
