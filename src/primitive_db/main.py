#!/usr/bin/env python3
"""Entry point for the primitive database application."""

from primitive_db.engine import welcome


def main() -> None:
    """Run the application."""
    welcome()


if __name__ == "__main__":
    main()
