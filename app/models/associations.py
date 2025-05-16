from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.base import Base

site_hashtag_association = Table(
    "site_hashtag_association",
    Base.metadata,
    Column("sites_id", Integer, ForeignKey("sites.id"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id"), primary_key=True),
)

list_site_association = Table(
    "list_site_association",
    Base.metadata,
    Column("list_id", Integer, ForeignKey("lists.id"), primary_key=True),
    Column("site_id", Integer, ForeignKey("sites.id"), primary_key=True),
)
