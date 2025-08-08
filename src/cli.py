import argparse


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


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        # No action for now; just parse arguments.
        pass


if __name__ == "__main__":
    main()
