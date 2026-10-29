from abc import ABC, abstractmethod


class AbstractRepository(ABC):

    @abstractmethod
    def get_all(self) -> list:
        pass

    @abstractmethod
    def get_by_field(self, field: str, value: str) -> list:
        pass

    @abstractmethod
    def add(self, item_dict: dict) -> dict:
        pass

    @abstractmethod
    def update(self, identifier, update_data: dict) -> dict:
        pass
