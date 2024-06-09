from datetime import date
from datetime import timedelta
from model import Batch, OrderLine, allocate, OutOfStock
import pytest


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("IN_STOCK", "IPHONE", 10, eta=None)
    shipment_batch = Batch("SHIPMENT", "IPHONE", 10, eta=date.today() + timedelta(days=1))
    line = OrderLine("1_REF", "IPHONE", 5)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 5
    assert shipment_batch.available_quantity == 10
    assert allocation == in_stock_batch.reference


def test_prefers_eariler_batches():
    earliest = Batch("TEST_1", "IPHONE", 10, date.today())
    tomorrow = Batch("TEST_2", "IPHONE", 10, date.today() + timedelta(days=1))
    later = Batch("TEST_3", "IPHONE", 10, date.today() + timedelta(days=2))
    line = OrderLine('ORDER_1', "IPHONE", 5)

    allocate(line, [earliest, tomorrow, later])

    assert earliest.available_quantity == 5
    assert tomorrow.available_quantity == 10
    assert later.available_quantity == 10


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("BATCH_1", "SMALL_TABLE", 10, eta=date.today())
    allocate(OrderLine("ORDER_1", "SMALL_TABLE", 20), [batch])

    with pytest.raises(OutOfStock, match="SMALL_TABLE"):
        allocate(OrderLine("ORDER_2", "SMALL_TABLE", 1), [batch])
