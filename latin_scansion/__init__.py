"""Automated Latin scansion."""

import pkg_resources

from latin_scansion.lib import *

__version__ = pkg_resources.get_distribution("latin_scansion").version
__all__ = [
    "__version__",
    "read_document",
    "scan_document",
    "scan_verse",
    "write_document",
    "Document",
    "Foot",
    "Syllable",
    "Verse",
]
