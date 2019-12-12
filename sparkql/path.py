"""Obtain path to a field within a possibly nested hierarchy."""

from typing import Sequence

from pyspark.sql import Column
from pyspark.sql import functions as sql_funcs

from .fields.base import BaseField


def field_names(field: BaseField) -> Sequence[str]:
    """Items on the path to a field."""
    fields = [field]
    while fields[0]._parent is not None:
        if fields[0].field_name is None:
            raise ValueError("Encountered an unset name while traversing tree")
        fields.insert(0, fields[0]._parent)
    return [f.field_name for f in fields]


def string(field: BaseField) -> str:
    """Return dot-delimited path to field `field`."""
    return ".".join(field_names(field))


def column(field: BaseField) -> Column:
    """Return Spark column pointing to field `field`."""
    fields_seq = field_names(field)
    col: Column = sql_funcs.col(fields_seq[0])
    for field_name in fields_seq[1:]:
        col = col(field_name)
    return col