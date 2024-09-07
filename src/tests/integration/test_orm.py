from src import domain as model


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES " "('order1', 'APPLE', 10)"
    )
    expected = model.OrderLine("order1", "APPLE", 10)
    assert session.query(model.OrderLine).one() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine("order1", "APPLE", 10)
    session.add(new_line)
    session.commit()

    rows = list(session.execute("SELECT orderid, sku, qty FROM order_lines"))
    assert rows == [("order1", "APPLE", 10)]
