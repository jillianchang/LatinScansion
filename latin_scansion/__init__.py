"""Automated Latin scansion."""

import pkg_resources

from latin_scansion.lib import read_document  # noqa: F401
from latin_scansion.lib import write_document  # noqa: F401
from latin_scansion.lib import scan_document  # noqa: F401
from latin_scansion.lib import scan_verse  # noqa: F401
from latin_scansion.lib import Document  # noqa: F401
from latin_scansion.lib import Foot  # noqa: F401
from latin_scansion.lib import Syllable  # noqa: F401
from latin_scansion.lib import Verse  # noqa: F401

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
