import domain.model as model
import service_layer.services as services
from adapters.repository import FakeRepository


class FakeSession():
    commited = False

    def commit(self):
        self.commited = True


def test_returns_allocation():
    line = model.OrderLine("ASD", "APPLE", 10)
    batch = model.Batch("BATCH1", "APPLE", 100, None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())

    assert result == "BATCH1"


def test_error_for_invalid_sku():
    line = model.OrderLine("ASD", "APPLE", 10)
    batch = model.Batch("BATCH1", "ORANGE", 100, None)

    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("ASD", "APPLE", 10)
    batch = model.Batch("BATCH1", "APPLE", 100, None)
    repo = FakeRepository([batch])

    session = FakeSession()

    services.allocate(line, repo, session)

    assert session.commited is True
