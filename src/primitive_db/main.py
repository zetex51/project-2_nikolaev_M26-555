#!/usr/bin/env python3
"""Entry point for the primitive database application."""

import prompt


def main() -> None:
    """Ask the user for their name and greet them."""
    name = prompt.string("May I have your name? ")
    print(f"Hello, {name}!")


if __name__ == "__main__":
    main()
