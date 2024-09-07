from datetime import date

from src.domain.model import Batch
from src.domain.model import OrderLine


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("BATCH_1", sku, batch_qty, date.today()),
        OrderLine("Order_1", sku, line_qty),
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch_1", "SMALL_TABLE", qty=20, eta=date.today())
    line = OrderLine("order_ref", "SMALL_TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, line = make_batch_and_line("IPHONE", 20, 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_batch_and_line("IPHONE", 2, 20)

    assert batch.can_allocate(line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("IPHONE", 2, 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("Batch_1", "IPHONE", 20, date.today())
    line = OrderLine("Order_1", "IPAD", 2)

    assert batch.can_allocate(line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("IPHONE", 20, 2)
    batch.deallocate(unallocated_line)
    # no change
    assert batch.available_quantity == 20
