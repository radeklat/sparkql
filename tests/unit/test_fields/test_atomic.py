from datetime import date, datetime
import decimal

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    ByteType,
    IntegerType,
    LongType,
    ShortType,
    DecimalType,
    DoubleType,
    FloatType,
    StringType,
    BinaryType,
    BooleanType,
    DateType,
    TimestampType,
    StructType,
    StructField,
)

from sparkql.exceptions import FieldValueValidationError
from sparkql.fields.base import BaseField
from sparkql.fields.atomic import (
    Byte,
    Integer,
    Long,
    Short,
    Decimal,
    Double,
    Float,
    String,
    Binary,
    Boolean,
    Date,
    Timestamp,
)


@pytest.mark.parametrize(
    "sparkql_field_class, spark_type_class",
    [
        [Byte, ByteType],
        [Integer, IntegerType],
        [Long, LongType],
        [Short, ShortType],
        [Decimal, DecimalType],
        [Double, DoubleType],
        [Float, FloatType],
        [String, StringType],
        [Binary, BinaryType],
        [Boolean, BooleanType],
        [Date, DateType],
        [Timestamp, TimestampType],
    ],
)
def test_atomics_have_correct_spark_type_classes(sparkql_field_class, spark_type_class):
    field_instance = sparkql_field_class()
    assert field_instance._spark_type_class is spark_type_class


class TestValidateOnValue:
    @staticmethod
    @pytest.mark.parametrize(
        "sparkql_field_class, spark_type_class, value",
        [
            [Byte, ByteType, 7],
            [Integer, IntegerType, 7],
            [Long, LongType, 7],
            [Short, ShortType, 7],
            [Decimal, DecimalType, decimal.Decimal(5)],
            [Decimal, DecimalType, decimal.Decimal(5.5)],
            [Double, DoubleType, 5.5],
            [Float, FloatType, 5.5],
            [String, StringType, "abc"],
            [Binary, BinaryType, bytearray(0b0101)],
            [Boolean, BooleanType, True],
            [Date, DateType, date(2000, 1, 1)],
            [Date, DateType, datetime(2000, 1, 1, 12, 0)],
            [Timestamp, TimestampType, datetime(2000, 1, 1, 12, 0)],
        ],
    )
    def test_atomics_should_successfully_receive_value(
        sparkql_field_class, spark_type_class, value, spark_session: SparkSession
    ):
        # check sparkql converter should accept the value
        field_instance: BaseField = sparkql_field_class()
        field_instance._validate_on_value(value)

        # check dataframe can be successfully created with same value
        spark_session.createDataFrame(
            data=[[value]], schema=StructType([StructField("test_field", spark_type_class())])
        )

    @staticmethod
    @pytest.mark.parametrize(
        "sparkql_field_class, spark_type_class, value",
        [
            [Integer, IntegerType, 7.5],
            [Long, LongType, 7.5],
            [Short, ShortType, 7.5],
            [Double, DoubleType, 5],
            [Float, FloatType, 5],
            [Date, DateType, 1234567890],
            [Date, DateType, 1234567890],
            [Timestamp, TimestampType, 1234567890],
        ],
    )
    def test_atomics_should_reject_invalid_value(
        sparkql_field_class, spark_type_class, value, spark_session: SparkSession
    ):
        # check sparkql converter should reject the value
        with pytest.raises(FieldValueValidationError):
            field_instance: BaseField = sparkql_field_class()
            field_instance._validate_on_value(value)

        # check dataframe can be reject the value
        with pytest.raises(TypeError):
            spark_session.createDataFrame(
                data=[[value]], schema=StructType([StructField("test_field", spark_type_class())])
            )
