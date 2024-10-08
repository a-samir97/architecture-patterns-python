from abc import ABC
from abc import abstractmethod
from typing import List

from src.domain import model


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: model.Batch) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError

    @abstractmethod
    def list(self):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch) -> None:
        self.session.add(batch)

    def get(self, reference) -> model.Batch:
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch: model.Batch) -> None:
        self._batches.add(batch)

    def get(self, reference) -> model.Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class AbstractProductRepository(ABC):
    @abstractmethod
    def add(self, product):
        ...

    @abstractmethod
    def get(self, sku) -> model.Product:
        ...

    @abstractmethod
    def list_all(self) -> List[model.Product]:
        ...

    @abstractmethod
    def update(self, product: model.Product) -> None:
        ...
