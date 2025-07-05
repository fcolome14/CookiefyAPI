from enum import Enum


class EntityType(str, Enum):
    SITE = "site"
    LIST = "list"
    USER = "user"


class InteractionType(str, Enum):
    LIKE = "like"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
