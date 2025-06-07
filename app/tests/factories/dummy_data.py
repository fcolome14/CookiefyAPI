from faker import Faker
from datetime import datetime, timezone, timedelta
import random

from app.models.user import User
from app.models.image import Image
from app.models.lists import List as ListModel
from app.models.site import Site
from app.models.hashtag import Hashtag
from app.models.category import Category

fake = Faker()

def create_dummy_user(index=0) -> User:
    return User(
        name=fake.name(),
        username=f"user{index}_{fake.user_name()}",
        email=f"user{index}_{fake.email()}",
        code=random.randint(1000, 9999),
        code_exp=(datetime.now() + timedelta(days=30)).isoformat(),
        hashed_password=fake.sha256(),
        is_active=True,
    )

def create_dummy_image(index=0) -> Image:
    return Image(
        name=f"image_{index}",
        data=b"fakeimagebinarydata",
        path=f"/static/images/image_{index}.jpg",
        created_at=fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc),
    )

def create_dummy_site(index=0, image_id=None, category_id=None) -> Site:
    return Site(
        name=f"Site {index} - {fake.company()}",
        address=fake.address(),
        city=fake.city(),
        contact=fake.phone_number(),
        image_id=image_id,
        category=category_id,
        created_at=fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc),
    )

def create_dummy_list(index=0, user_id=None, image_id=None) -> ListModel:
    return ListModel(
        name=f"List {index}",
        owner=user_id,
        description=fake.sentence(),
        likes=random.randint(0, 100),
        shares=random.randint(0, 50),
        saves=random.randint(0, 50),
        image=1,
        is_banned=random.choice([False, False, True]),
        is_public=random.choice([True, True, False]),
        accepts_contributions=random.choice([True, False]),
        created_at=fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc),
    )
