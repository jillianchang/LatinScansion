import pkg_resources

from .scansion import scan_document
from .scansion import scan_verse
from .scansion_pb2 import Document
from .scansion_pb2 import Foot
from .scansion_pb2 import Syllable
from .scansion_pb2 import Verse
from .scansion_pb2 import Verse
from .textproto import read_document
from .textproto import write_document


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
