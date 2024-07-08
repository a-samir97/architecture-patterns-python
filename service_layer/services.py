import domain.model as model


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(ref, sku, qty, eta, repo, session):
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(orderid, sku, qty, repo, session):
    batches = repo.list()

    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Invalid sku {sku}")

    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
