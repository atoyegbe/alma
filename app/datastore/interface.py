from abc import ABC, abstractmethod
from typing import Any, List, Dict, Type, TypeVar
from sqlmodel import SQLModel, Session


ModelType = TypeVar("ModelType", bound=SQLModel)

class DataStoreInterface(ABC):
    """
    Abstract base class for a data store interface.
    """

    @abstractmethod
    def add_one(
        self,
        db: Session,
        model: Type[ModelType],
        item: Dict[str, Any]
    ) -> None:
        """
        Add a single item to the datastore.

        :param db: Database session.
        :param model: The model class representing the table.
        :param item: A dictionary representing the item to be added.
        """
        pass

    @abstractmethod
    def add_many(
        self,
        db: Session,
        model: Type[ModelType],
        items: List[Dict[str, Any]]
    ) -> None:
        """
        Add multiple items to the datastore.

        :param db: Database session.
        :param model: The model class representing the table.
        :param items: A list of dictionaries, each representing an item to be added.
        """
        pass

    @abstractmethod
    def upsert_one(
        self,
        db: Session,
        model: Type[ModelType],
        item: Dict[str, Any]
    ) -> None:
        """
        Insert or update a single item in the datastore.

        :param db: Database session.
        :param model: The model class representing the table.
        :param item: A dictionary representing the item to be upserted.
        """
        pass

    @abstractmethod
    def upsert_many(
        self,
        db: Session,
        model: Type[ModelType],
        items: List[Dict[str, Any]]
    ) -> None:
        """
        Insert or update multiple items in the datastore.

        :param db: Database session.
        :param model: The model class representing the table.
        :param items: A list of dictionaries, each representing an item to be upserted.
        """
        pass

    @abstractmethod
    def get_one(
        self,
        db: Session,
        model: Type[ModelType],
        item_id: Any,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a single item from the datastore by its ID.

        :param db: Database session.
        :param model: The model class representing the table.
        :param item_id: The ID of the item to be retrieved.
        :param filters: Optional dictionary of filters to apply.
        :return: A dictionary representing the retrieved item.
        """
        pass

    @abstractmethod
    def get_many(
        self,
        db: Session,
        model: Type[ModelType],
        item_ids: List[Any],
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve multiple items from the datastore by their IDs.

        :param db: Database session.
        :param model: The model class representing the table.
        :param item_ids: A list of IDs of the items to be retrieved.
        :param filters: Optional dictionary of filters to apply.
        :return: A list of dictionaries, each representing a retrieved item.
        """
        pass
