from enum import Enum


class Status(str, Enum):
    """TRACE event outcome status.

    Status is intentionally distinct from severity.
    """

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    PARTIAL = "PARTIAL"
