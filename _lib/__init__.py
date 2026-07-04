"""CC shared library — stdlib-only helpers shared across the home-automation projects.

The projects under ``~/Github/CC`` each live in their own git repo but always sit
side-by-side on disk, so consumers reach this package with a 3-line sibling-path
bootstrap at the top of the script::

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from _lib import secrets, ha, mail

That works identically for cron (absolute-path invocation) and the status-site
container (the repo root is bind-mounted at ``/app``, so ``/app/_lib`` is present).
Everything here is stdlib-only so scripts keep running under bare ``/usr/bin/python3``.
"""
from . import ha, local_llm, mail, report, secrets  # noqa: F401

__all__ = ["secrets", "ha", "mail", "local_llm", "report"]
