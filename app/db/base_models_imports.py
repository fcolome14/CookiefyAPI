""" This file’s only job is to load all models once so Base.metadata.create_all() 
or Alembic autogenerate can discover all tables. """

from app.models.site import Site
from app.models.image import Image
from app.models.category import Category
from app.models.hashtag import Hashtag
from app.models.associations import list_site_association, site_hashtag_association
from app.models.lists import List
from app.models.user import User
from app.models.user_interactions import UserInteraction