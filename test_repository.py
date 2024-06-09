import model
import repository


def insert_order_line(session):
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES (:orderid, :sku, :qty)",
        dict(orderid="order1", sku="GENERIC-SOFA", qty=100)
    )
    [[order_line_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="GENERIC-SOFA")
    )
    return order_line_id


def insert_batch(session, batch_id):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES (:batch_id, 'GENERIC-SOFA', 100, null)",
        dict(batch_id=batch_id)
    )
    [[batch_id]] = session.execute(
        "SELECT id FROM batches WHERE reference=:batch_id",
        dict(batch_id=batch_id)
    )
    return batch_id


def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "APPLE", 10, eta=None)
    session.add(batch)
    session.commit()

    rows = list(session.execute(
        "SELECT reference, sku, _purchased_quantity, eta FROM batches"
    ))
    assert rows == [("batch1", "APPLE", 10, None)]


def test_repository_can_retrieve_a_batch_with_allocations(session):
    batch_id = insert_batch(session, "batch1")
    order_line_id = insert_order_line(session)
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id) VALUES (:order_line_id, :batch_id)",
        dict(order_line_id=order_line_id, batch_id=batch_id)
    )

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected
    assert retrieved._allocations == {model.OrderLine("order1", "GENERIC-SOFA", 100)}

