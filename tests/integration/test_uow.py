
def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta)
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[order_line_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid=orderid, sku=sku)
    )
    [[batchref]] = session.execute(
        "SELECT batch_id FROM allocations WHERE orderline_id=:order_line_id",
        dict(order_line_id=order_line_id)
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
    batchref = get_allocate_batch_reg(session, "order1", "GENERIC-SOFA")
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