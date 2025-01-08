from typing import List, Dict, Any, Optional, Type

from sqlmodel import Session, select
from app.datastore.interface import DataStoreInterface, ModelType


class DataStore(DataStoreInterface):
    def add_one(
        self,
        db: Session,
        model: Type[ModelType],
        item: Dict[str, Any]
    ) -> None:
        """
        Insert a single item into the datastore.

        :param db: Database session.
        :param model: The model class representing the table.
        :param item: A dictionary representing the item to be inserted.
        """
        pass

    def add_many(
        self,
        db: Session,
        model: Type[ModelType],
        items: List[Dict[str, Any]]
    ) -> None:
        """
        Insert multiple items into the datastore.

        :param db: Database session.
        :param model: The model class representing the table.
        :param items: A list of dictionaries, each representing an item to be inserted.
        """
        pass

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

    def get_one(
        self,
        db: Session,
        model: Type[ModelType],
        **filters
    ) -> Dict[str, Any]:
        """
        Retrieve a single item from the datastore by its ID.

        :param db: Database session.
        :param model: The model class representing the table.
        :param item_id: The ID of the item to be retrieved.
        :param filters: Optional dictionary of filters to apply.
        :return: A dictionary representing the retrieved item.
        """
        statement = select(model).filter_by(**filters)
        return db.exec(statement).first()

    def get_many(
        self,
        db: Session,
        model: Type[ModelType],
        item_ids: List[Any],
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Retrieve multiple items from the datastore by their IDs.

        :param db: Database session.
        :param model: The model class representing the table.
        :param item_ids: A list of IDs of the items to be retrieved.
        :param filters: Optional dictionary of filters to apply.
        :return: A list of dictionaries representing the retrieved items.
        """
        pass
