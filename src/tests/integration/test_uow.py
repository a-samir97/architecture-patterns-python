import threading
import time
import traceback

import pytest
from src.domain import model
from src.service_layer import unit_of_work
from src.tests.random_refs import random_batchref
from src.tests.random_refs import random_orderid
from src.tests.random_refs import random_sku


def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[order_line_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = session.execute(
        "SELECT batch_id FROM allocations WHERE orderline_id=:order_line_id",
        dict(order_line_id=order_line_id),
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    # to inialized batches
    session = session_factory()
    insert_batch(session, "batch1", "GENERIC-SOFA", 100, None)
    session.commit()

    uow = unit_of_work.SQLAlchemyUnitOfWork(session_factory)

    with uow:
        batch = uow.batches.get(reference="batch1")
        line = model.OrderLine("order1", "GENERIC-SOFA", 10)
        batch.allocate(line)
        uow.commit()

    # check the batch has been allocated
    batchref = get_allocated_batch_ref(session, "order1", "GENERIC-SOFA")
    assert batchref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SQLAlchemyUnitOfWork(session_factory)

    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SQLAlchemyUnitOfWork(session_factory)

    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-DINING-TABLE", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def try_to_allocate(orderid, sku, exceptions):
    line = model.OrderLine(orderid, sku, 10)
    try:
        with unit_of_work.SqlAlchemyUnitOfWork() as uow:
            product = uow.products.get(sku=sku)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed(posgtes_session_factory):
    sku, batch = random_sku(), random_batchref()

    session = posgtes_session_factory()

    insert_batch(session, batch, sku, 100, eta=None, product_version=1)

    session.commit()

    order1, order2 = random_orderid(1), random_orderid(2)

    exceptions = []
    try_to_allocate_order_1 = lambda: try_to_allocate(order1, sku, exceptions)
    try_to_allocate_order_2 = lambda: try_to_allocate(order2, sku, exceptions)

    thread1 = threading.Thread(target=try_to_allocate_order_1)
    thread2 = threading.Thread(target=try_to_allocate_order_2)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    [[version]] = session.execute(
        "SELECT version_number FROM products WHERE sku=:sku",
        dict(sku=sku),
    )
    assert version == 2

    [exception] = exceptions
    assert "could not serialize access due to concurrent update" in str(exception)

    orders = list(
        session.execute(
            "SELECT orderid FROM allocations"
            " JOIN batches ON allocations.batch_id = batches.id"
            " JOIN order_lines ON allocations.orderline_id = order_lines.id"
            " WHERE order_lines.sku=:sku",
            dict(sku=sku),
        )
    )
    assert len(orders) == 1

    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        uow.session.execute("select 1")
