import domain.model as model
import unit_of_work
from datetime import date
from typing import Optional


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(
        ref: str, sku: str, qty: int,
        eta: Optional[date], uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(
        orderid: str, sku: str,
        qty: int, uow: unit_of_work.AbstractUnitOfWork):

    line = model.OrderLine(orderid, sku, qty)

    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(sku, batches):
            raise InvalidSku(f"Invalid sku {sku}")

        batchref = model.allocate(line, batches)
        uow.commit()
    return batchref
