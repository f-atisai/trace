from enum import Enum


class Operation(str, Enum):
    """Canonical TRACE operation and reserved lifecycle categories."""

    READ = "READ"
    CHECK = "CHECK"
    FILTER = "FILTER"
    SORT = "SORT"
    DERIVE = "DERIVE"
    TRANSFORM = "TRANSFORM"
    MERGE = "MERGE"
    AGGREGATE = "AGGREGATE"
    ANALYZE = "ANALYZE"
    VALIDATE = "VALIDATE"
    OUTPUT = "OUTPUT"

    START = "START"
    END = "END"
    STEP = "STEP"
