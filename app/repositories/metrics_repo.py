from sqlalchemy.orm import Session
from app.models.user_interactions import UserInteraction
from abc import ABC, abstractmethod
from app.models.lists import List as ListModel
from typing import Union, List
from sqlalchemy import update, case
from typing import Union, List, Type
from sqlalchemy.ext.declarative import DeclarativeMeta

class IPostInteraction(ABC):
    """Interface for post repository user's intercation operations"""
    
    @abstractmethod
    def update_interactions(self, user_id: int, list_input: ListModel) -> dict:
        pass

    @abstractmethod
    def update_scores(self, model, column_name, record_id, score) -> dict:
        pass

    @abstractmethod
    def update_metrics(self, model, column_name, record_ids, addition, prevent_negative) -> dict:
        pass

class PostInteraction(IPostInteraction):
    def __init__(self, db: Session):
        self.db = db

    def update_interactions(
        self,
        user_id: int,
        entity: str,
        entity_id: int,
        interaction_type: str,
    ) -> dict:
        """
        Update user interactions with a specific entity.
        For 'like' and 'save' interactions, toggles the state.
        For 'click' and 'share', always creates a new record.
        """

        # Handle toggle interactions
        if interaction_type in ["like", "save"]:
            existing = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.entity_type == entity,
                UserInteraction.entity_id == entity_id,
                UserInteraction.interaction_type == interaction_type
            ).first()

            if existing:
                self.db.delete(existing)
                self.db.commit()
                return {"status": "removed", "interaction_type": interaction_type}

            # Add new interaction
            new_interaction = UserInteraction(
                user_id=user_id,
                entity_type=entity,
                entity_id=entity_id,
                interaction_type=interaction_type
            )
            self.db.add(new_interaction)
            self.db.commit()
            return {"status": "added", "interaction_type": interaction_type}

        # Non-toggle interactions (click, share, etc.)
        new_interaction = UserInteraction(
            user_id=user_id,
            entity_type=entity,
            entity_id=entity_id,
            interaction_type=interaction_type
        )
        self.db.add(new_interaction)
        self.db.commit()
        return {"status": "recorded", "interaction_type": interaction_type}
    

    def update_metrics(
        self,
        model: Type[DeclarativeMeta],
        column_name: str = "views",
        record_ids: Union[int, List[int]] = None,
        addition: bool = True,
        prevent_negative: bool = True,
    ) -> dict:
        """
        Increment or decrement a numeric metrics column for one or more records.

        Args:
            model (Type[DeclarativeMeta]): SQLAlchemy model class.
            column_name (str): Column to update.
            record_ids (int or List[int]): Record ID(s).
            addition (bool): Increment if True; decrement if False.
            prevent_negative (bool): Prevent values from going below zero.

        Returns:
            dict: Result status.
        """
        if isinstance(record_ids, int):
            record_ids = [record_ids]
        if not record_ids:
            return {"status": "error", "message": "No record IDs provided"}

        column_attr = getattr(model, column_name, None)
        if column_attr is None:
            return {"status": "error", "message": f"Column '{column_name}' not found in {model.__name__}"}

        delta = 1 if addition else -1

        if prevent_negative:
            value_expr = case(
                (column_attr + delta < 0, 0),
                else_=column_attr + delta
            )
        else:
            value_expr = column_attr + delta

        stmt = (
            update(model)
            .where(model.id.in_(record_ids))
            .values({column_attr: value_expr})
        )

        self.db.execute(stmt)
        self.db.commit()

        return {"status": "success", "message": f"{'Incremented' if addition else 'Decremented'} '{column_name}' for {len(record_ids)} record(s)."}


    def update_scores(
        self,
        model: Type[DeclarativeMeta],
        column_name: str = "score",
        record_id: int = None,
        score: float = 0.0,
    ) -> dict:
        """
        """

        if not record_id:
            return {"status": "error", "message": "No record IDs provided"}

        column_attr = getattr(model, column_name, None)
        if column_attr is None:
            return {"status": "error", "message": f"Column '{column_name}' not found in {model.__name__}"}

        stmt = (
            update(model)
            .where(model.id == record_id)
            .values({column_attr: score})
        )

        self.db.execute(stmt)
        self.db.commit()

        return {"status": "success", "message": "Updated score successfully."}
