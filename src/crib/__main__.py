"""
Entrypoint module, in case you use `python -mcrib`.
"""
import click_log
from crib.cli import main, logger

if __name__ == "__main__":
    main()
