from sqlalchemy.orm import Session, joinedload, aliased
import sqlalchemy as sa
from sqlalchemy import or_, and_, select, insert, delete, func, update, case, desc
from app.models.lists import List as ListModel
from app.schemas.post import (
    ListKPIs, 
    ListBasicRead, 
    SiteKPIs, 
    SiteBasicRead, 
    HashtagBasicRead,
    HashtagWithCount
    )
from app.models.site import Site
from app.models.user import User
from app.models.image import Image
from app.models.associations import list_site_association
from app.models.associations import site_hashtag_association
from app.models.hashtag import Hashtag
from abc import ABC, abstractmethod
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, List, Optional
from sqlalchemy.exc import IntegrityError
import os
from sqlalchemy.ext.declarative import DeclarativeMeta
from typing import Union, List, Type
from app.utils.date_time import DateUtils
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "users", "images")

class IPostRepository(ABC):
    """Interface for post repository operations"""
    
    @abstractmethod
    def add_list(self, user_id: int, list_input: ListModel) -> User:
        pass
    
    @abstractmethod
    def update_list(self, list_id: int, new_site_ids: list[int]) -> bool:
        pass
    
    @abstractmethod
    def delete_list(self, list_id: Union[int, List[int]]) -> dict:
        pass
    
    @abstractmethod
    def get_list_by_name(self, user_id: int, list_name: str) -> ListModel | None:
        pass
    
    @abstractmethod
    def get_list_by_list_id(self, list_id: Union[int, List[int]]) -> ListModel | None:
        pass

    @abstractmethod
    def get_lists_from_owner_id(self, list_id: Union[int, List[int]]) -> ListModel | None:
        pass
    
    @abstractmethod
    def get_list_by_user_id(self, user_id: int, list_id: Union[int, List[int]]) -> Union[ListModel, List[ListModel], None]:
        pass
    
    @abstractmethod
    def check_sites_id(self, sites_id: list[int]) -> bool | None:
        pass
    
class PostRepository(IPostRepository):
    """Repository for post-related database operations."""

    def __init__(self, db: Session):
        self.db = db
        
    def add_list(self, user_id: int, list_input: ListModel) -> ListModel:
        """Create a new list."""
        new_list = ListModel(
            name=list_input.name,
            description=list_input.description,
            owner=user_id,
            accepts_contributions=list_input.accepts_contributions,
            is_public=list_input.is_public,
        )

        try:
            self.db.add(new_list)
            self.db.commit()
            self.db.refresh(new_list)
            print("List created successfully with ID %d", new_list.id)
            return {"status": "success", "message": new_list}
        except IntegrityError as exc:
            self.db.rollback()
            print("Failed to create list: %s", exc)
            return {"status": "error", "message": f"Failed to create list"}
        except Exception as exc:
            self.db.rollback()
            print("Unexpected error during user creation: %s", exc)
            return {"status": "error", "message": "Unexpected error during user creation"}
    
    def get_list_by_name(self, user_id: int, list_name: str) -> ListModel | None:
        """Fetch an active list by user_id."""
        return (
            self.db.query(ListModel)
            .filter(and_(User.id == user_id, ListModel.name == list_name, ListModel.is_banned == False))  # noqa: E712
            .first()
        )
    
    def get_list_by_list_id(self, list_id: Union[int, List[int]]) -> ListModel | None:
        """Fetch an active list(s) by list_id."""
        if isinstance(list_id, list):
            return (
                self.db.query(ListModel)
                .filter(ListModel.id.in_(list_id), ListModel.is_banned == False)  # noqa: E712
                .all()
            )
        return (
            self.db.query(ListModel)
            .filter(ListModel.id == list_id, ListModel.is_banned == False)  # noqa: E712
            .first()
        )
    
    def get_site_by_site_id(self, site_id: Union[int, List[int]]) -> Site | None:
        """Fetch a site(s) by site_id."""
        if isinstance(site_id, list):
            return (
                self.db.query(Site)
                .filter(Site.id.in_(site_id))  # noqa: E712
                .all()
            )
        return (
            self.db.query(Site)
            .filter(Site.id == site_id)  # noqa: E712
            .first()
        )
    
    def get_top_lists_by_hashtag_score(self, hashtag_ids: list[int], limit: int = 5):
        SiteAlias = aliased(Site)

        query = (
            self.db.query(
                ListModel,
                func.sum(site_hashtag_association.c.score).label("total_hashtag_score")
            )
            .join(list_site_association, list_site_association.c.list_id == ListModel.id)
            .join(SiteAlias, SiteAlias.id == list_site_association.c.site_id)
            .join(site_hashtag_association, site_hashtag_association.c.site_id == SiteAlias.id)
            .filter(ListModel.is_banned == False)
            .filter(site_hashtag_association.c.hashtag_id.in_(hashtag_ids))
            .group_by(ListModel.id)
            .order_by(func.sum(site_hashtag_association.c.score).desc())
            .limit(limit)
        )
        return query.all()
    
    def get_top_lists(self, limit: int = 5):
        return (
            self.db.query(ListModel)
            .options(joinedload(ListModel.image_file))  # Eager load the image_file relationship
            .filter(ListModel.is_banned == False)  # noqa: E712
            .order_by(ListModel.score.desc())
            .limit(limit)
            .all()
        )

    def get_top_sites(self, limit: int = 5, location: dict = None) -> List[Site]:
        if not location:
            # Globally
            return (
                self.db.query(Site)
                .options(joinedload(Site.image))  # Eager load the image relationship
                .order_by(Site.score.desc())
                .limit(limit)
                .all()
            )
        # Locally
        return (
                self.db.query(Site)
                .options(joinedload(Site.image))  # Eager load the image relationship
                .filter(Site.city == location.get("city"))
                .order_by(Site.score.desc())
                .limit(limit)
                .all()
            )
    
    def get_top_sites_by_hashtag(self, limit: int, hashtag_ids: list[int]):
        return (
            self.db.query(Site, site_hashtag_association.c.hashtag_id)
            .join(site_hashtag_association, site_hashtag_association.c.sites_id == Site.id)
            .filter(site_hashtag_association.c.hashtag_id.in_(hashtag_ids))
            .order_by(Site.score.desc())
            .distinct()
            .limit(limit)
            .all()
        )
    
    def get_top_hashtags_last_days(self, limit: int, days: int = 7):
        since = datetime.now(timezone.utc) - timedelta(days=days)
        count_subquery = (
            self.db.query(
                site_hashtag_association.c.hashtag_id.label("hashtag_id"),
                func.count().label("count")
            )
            .join(Site, Site.id == site_hashtag_association.c.sites_id)
            .filter(Site.created_at >= since)
            .group_by(site_hashtag_association.c.hashtag_id)
            .subquery()
        )
        return (
            self.db.query(Hashtag, count_subquery.c.count)
            .join(count_subquery, Hashtag.id == count_subquery.c.hashtag_id)
            .options(joinedload(Hashtag.image))
            .order_by(count_subquery.c.count.desc())
            .limit(limit)
            .all()
        )
        
    def get_trending_lists_sites(self, location: dict) -> dict:
        """Fetch lists and sites with highest scoring."""

        top_list_global = self.get_top_lists(limit=5)
        top_sites_global = self.get_top_sites(limit=5, location=location)
        top_sites_by_hashtag = self.get_top_sites_by_hashtag(limit=5, hashtag_ids=[73,74,3])  # Example hashtag IDs)
        top_hashtags_last_days = self.get_top_hashtags_last_days(limit=5, days=7)

        return {
            "top_list_global": [ListBasicRead.from_orm(list_) for list_ in top_list_global],
            "top_sites_near": [SiteBasicRead.from_orm(site) for site in top_sites_global],
            "top_sites_by_hashtag": [{**SiteBasicRead.from_orm(site).dict(),"hashtag_id": hashtag_id} 
                                     for site, hashtag_id in top_sites_by_hashtag],
            "top_hashtags_last_days": [
                HashtagWithCount(
                    count=count,
                    hashtag=HashtagBasicRead.from_orm(hashtag)
                )
                for hashtag, count in top_hashtags_last_days
            ]
        }


    def get_list_by_user_id(
        self, user_id: int, 
        list_id: Union[int, List[int]]) -> Union[ListModel, List[ListModel], None]:
        """Fetch an active list(s) owned by a certain user_id."""
        if isinstance(list_id, list):
            return (
                self.db.query(ListModel)
                .filter(
                    ListModel.id.in_(list_id), 
                    ListModel.is_banned == False,  # noqa: E712
                    ListModel.owner == user_id)
                .all()
            )
        return (
            self.db.query(ListModel)
            .filter(
                ListModel.id == list_id, 
                ListModel.is_banned == False, # noqa: E712
                ListModel.owner == user_id)
            .first()
        )
        
    
    def get_lists_from_owner_id(self, user_id: int) -> list[ListModel]:
        return (
            self.db.query(ListModel)
            .options(
                joinedload(ListModel.image_file),
                joinedload(ListModel.sites).joinedload(Site.image),
                joinedload(ListModel.sites).joinedload(Site.hashtags)
            )
            .filter(
                ListModel.is_banned == False,
                ListModel.owner == user_id
            )
            .all()
        )

    def get_nearby_sites(self, city: list[str]) -> list[Site]:
        if isinstance(city, str):
            city = [city.lower()]

        return (
            self.db.query(Site)
            .filter(
                func.lower(Site.city).in_(city)
                )
                .all()
            )    
    
    def get_image(self, image_id: int) -> str:
        return self.db.query(Image).get(image_id)
    
    def add_image_path(self, image: Image) -> Image:
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image
        
    def check_sites_id(self, sites_id: list[int]) -> bool | None:
        """Fetch all sites from their ids."""
        existing_ids = (
            self.db.query(Site.id)
            .filter(Site.id.in_(sites_id))
            .all()
            )
        
        found_ids = {id_tuple[0] for id_tuple in existing_ids}
        return set(sites_id) == found_ids
    
    def get_site_ids_from_list(self, list_id: int) -> list[int]:
        """Fetch site IDs directly from list_site_association table."""
        stmt = select(list_site_association.c.site_id).where(
            list_site_association.c.list_id == list_id
        )
        result = self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    def update_list_site_association(self, list_id: int, new_site_ids: list[int]) -> bool:
        """Update the list_site_association table for a given list_id."""
        try:
            if new_site_ids:
                insert_values = [
                    {"list_id": list_id, "site_id": site_id}
                    for site_id in new_site_ids
                ]
                insert_stmt = insert(list_site_association).values(insert_values)
                self.db.execute(insert_stmt)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print("Error updating list_site_association for list %d: %s", list_id, e)
            return False
    

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


    def get_record_kpis(
        self,
        model: Type[DeclarativeMeta],
        record_id: int,
    ) -> dict:
        if not record_id:
            return {"status": "error", "message": "No record ID provided"}

        if model == ListModel:
            stmt = select(
                ListModel.id,
                ListModel.likes,
                ListModel.shares,
                ListModel.saves,
                ListModel.visit_count,
                ListModel.image,
                ListModel.created_at
            ).where(ListModel.id == record_id)

            SchemaClass = ListKPIs

        elif model == Site:
            stmt = select(
                Site.id,
                Site.lists_count,
                Site.click_count
            ).where(Site.id == record_id)

            SchemaClass = SiteKPIs

        else:
            return {"status": "error", "message": "Unsupported model type"}

        result = self.db.execute(stmt).fetchone()
        if result is None:
            return {"status": "error", "message": "Record not found"}

        # Convert to Pydantic schema
        data_dict = dict(result._mapping)
        parsed = SchemaClass(**data_dict)

        return {"status": "success", "content": parsed.model_dump()}


    @staticmethod
    def _delete_image_file(filename: str) -> bool:
        try:
            image_folder = os.path.join(IMAGES_DIR, filename)
            if os.path.exists(image_folder):
                os.remove(image_folder)
                return True
            else:
                print(f"File not found: {image_folder}")
                return False
        except Exception as e:
            print(f"Error deleting file {image_folder}: {e}")
            return False
    
    def delete_list_image(self, image_id: Union[int, List[int]]) -> dict:
        """Delete one or more lists images"""
        try:
            if not isinstance(image_id, list):
                image_id = [image_id]

            images_to_delete: Image = (
                self.db.query(Image)
                .filter(Image.id.in_(image_id))
                .all()
            )

            if not images_to_delete:
                return {"status": "error", "message": f"No images found with ID(s): {image_id}"}

            for obj in images_to_delete:
                self._delete_image_file(filename=obj.name)
                self.db.delete(obj)

            self.db.commit()
            return {
                "status": "success", 
                "message": f"Deleted images with IDs: {image_id}"
                }
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Error deleting image(s) {image_id}: {e}"}
        
    def delete_list(self, list_id: Union[int, List[int]]) -> dict:
        """Delete one or more lists and their site associations, updating counters."""
        try:
            if not isinstance(list_id, list):
                list_id = [list_id]

            site_ids = self.db.execute(
                sa.select(list_site_association.c.site_id)
                .where(list_site_association.c.list_id.in_(list_id))
            ).scalars().all()

            assoc_delete_stmt = delete(list_site_association).where(
                list_site_association.c.list_id.in_(list_id)
            )
            self.db.execute(assoc_delete_stmt)

            lists_to_delete = (
                self.db.query(ListModel)
                .filter(ListModel.id.in_(list_id))
                .all()
            )

            if not lists_to_delete:
                return {"status": "error", "message": f"No lists found with ID(s): {list_id}"}

            for obj in lists_to_delete:
                self.db.delete(obj)

            if site_ids:
                self.update_metrics(
                    model=Site,
                    column_name="lists_count",
                    record_ids=list(set(site_ids)),  # Ensure uniqueness
                    addition=False
                )

            self.db.commit()
            return {
                "status": "success",
                "message": f"Deleted lists and updated associated site counters for IDs: {list_id}",
                "content": lists_to_delete
            }

        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Error deleting list(s) {list_id}: {e}"}

    
    def update_list(self, list_obj: ListModel) -> ListModel | None:
        """Update a list record."""
        try:
            self.db.commit()
            self.db.refresh(list_obj)
            return {"status": "success", "message": list_obj}
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Database update failed: {e}")
            return {"status": "error", "message": "Database update failed."}
    
    def update_site(self, site_obj: Site) -> Site | None:
        """Update a site record."""
        # TODO: Refactor with a more generic update method. Merge update_list too
        try:
            self.db.commit()
            self.db.refresh(site_obj)
            return {"status": "success", "message": site_obj}
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Database update failed: {e}")
            return {"status": "error", "message": "Database update failed."}
  
