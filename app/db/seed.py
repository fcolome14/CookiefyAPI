""" Load static data to database """
import os
from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.hashtag import Hashtag
from app.models.image import Image
from app.utils.logger import get_logger

logger = get_logger(__name__)
STATIC_IMG_DIR = "app/static/images"

class Seed:
    @staticmethod
    def seed_data(db: Session):
        if db.query(Category).count() == 0:
            Seed.add_categories(db)

        if db.query(Hashtag).count() == 0:
            Seed.add_hashtags(db)
        
        if db.query(Image).count() == 0:
            Seed.add_images(db)


    @staticmethod
    def add_categories(db: Session):
        categories = [
            {"name": "Restaurant"},
            {"name": "Bar"},
            {"name": "Pub"},
            {"name": "Café"},
            {"name": "Street Food"},
           ]

        category_models = [Category(**cat) for cat in categories]
        db.add_all(category_models)
        db.commit()
        for category in category_models:
            db.refresh(category)
        logger.info(f"Added {len(category_models)} categories.")
    
    
    @staticmethod
    def add_images(db: Session):
        
        for filename in os.listdir(STATIC_IMG_DIR):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            filepath = os.path.join(STATIC_IMG_DIR, filename)
            with open(filepath, 'rb') as f:
                image_data = f.read()

            image = Image(name=filename, data=image_data)
            db.add(image)

        db.commit()
        db.close()
        logger.info("Added default images successfully")


    @staticmethod
    def add_hashtags(db: Session):
        hashtags = [
            {"name": "Asian"},
            {"name": "Mexican"},
            {"name": "Spanish"},
            {"name": "Italian"},
            {"name": "French"},
            {"name": "American"},
            {"name": "Indian"},
            {"name": "Mediterranean"},
            {"name": "Restaurant"},
            {"name": "Bar"},
            {"name": "Cocktails"},
            {"name": "Japanese"},
            {"name": "Chinese"},
            {"name": "Thai"},
            {"name": "Vietnamese"},
            {"name": "Korean"},
            {"name": "Turkish"},
            {"name": "Greek"},
            {"name": "Lebanese"},
            {"name": "Moroccan"},
            {"name": "Brazilian"},
            {"name": "Peruvian"},
            {"name": "Argentinian"},
            {"name": "Caribbean"},
            {"name": "African"},
            {"name": "Vegan"},
            {"name": "Vegetarian"},
            {"name": "Gluten-Free"},
            {"name": "Steakhouse"},
            {"name": "Seafood"},
            {"name": "Burger"},
            {"name": "Pizza"},
            {"name": "Tapas"},
            {"name": "Brunch"},
            {"name": "Coffee"},
            {"name": "Bakery"},
            {"name": "Ice Cream"},
            {"name": "Sushi"},
            {"name": "Ramen"},
            {"name": "Fast Food"},
            {"name": "Fine Dining"},
            {"name": "Casual Dining"},
            {"name": "Street Food"},
            {"name": "Fusion"},
            {"name": "Buffet"},
            {"name": "Wine Bar"},
            {"name": "Craft Beer"},
            {"name": "Deli"},
            {"name": "Gastropub"},
            {"name": "Food Truck"},
            {"name": "Pasta"},
            {"name": "Salad"},
            {"name": "Dessert"},
            {"name": "Brasserie"},
            {"name": "Bistro"},
            {"name": "Café"},
            {"name": "Patisserie"},
            {"name": "Taverna"},
            {"name": "Trattoria"},
            {"name": "Taverne"},
            {"name": "Churrascaria"},
            {"name": "Parrilla"},
            {"name": "Asador"},
            {"name": "Taqueria"},
            {"name": "BBQ"}
        ]
        hashtags_data = [Hashtag(**tag) for tag in hashtags]
        db.add_all(hashtags_data)
        db.commit()
        for tag in hashtags_data:
            db.refresh(tag)
        logger.info(f"Added {len(hashtags_data)} hashtags.")
