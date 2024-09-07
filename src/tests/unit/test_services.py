import pytest
import src.service_layer.services as services
from src import domain as model
from src.adapters.repository import FakeRepository
from src.service_layer import unit_of_work


class FakeRepositoryTest:
    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([model.Batch(ref, sku, qty, eta)])


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("BATCH1", "APPLE", 100, None, repo, session)
    result = services.allocate("ASD", "APPLE", 10, repo, session)
    assert result == "BATCH1"


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("BATCH1", "APPLE", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku"):
        services.allocate("ASD", "ORANGE", 10, repo, session)


def test_commits():
    line = model.OrderLine("ASD", "APPLE", 10)
    batch = model.Batch("BATCH1", "APPLE", 100, None)
    repo = FakeRepository([batch])

    session = FakeSession()

    services.allocate(line, repo, session)

    assert session.commited is True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("BATCH1", "APPLE", 100, None, repo, session)
    assert repo.get("BATCH1") is not None
    assert session.commited is True


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch_uow():
    uow = FakeUnitOfWork()
    services.add_batch("BATCH1", "APPLE", 100, None, uow)
    assert uow.batches.get("BATCH1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("BATCH1", "APPLE", 100, None, uow)
    result = services.allocate("ASD", "APPLE", 10, uow)
    assert result == "BATCH1"
