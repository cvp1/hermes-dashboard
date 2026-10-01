"""Stdlib-only shared helpers; consumers add the parent directory to sys.path and import ``_lib``."""
from . import ha, local_llm, mail, report, secrets  # noqa: F401

__all__ = ["secrets", "ha", "mail", "local_llm", "report"]
