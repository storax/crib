"""
Entrypoint module, in case you use `python -mcrib`.
"""
import click_log

from crib.cli import logger, main

if __name__ == "__main__":
    main()
