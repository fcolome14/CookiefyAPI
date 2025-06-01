from app.models.site import Site
from app.models.lists import List as ListModel

def compute_site_score(site: Site, max_likes: int, max_lists: int, max_hashtags: int):
    w_likes = 0.4
    w_lists = 0.3
    w_tags = 0.3

    normalized_likes = site.likes / max_likes if max_likes else 0
    normalized_lists = site.list_count / max_lists if max_lists else 0
    normalized_tags = site.hashtag_score / max_hashtags if max_hashtags else 0

    return (
        w_likes * normalized_likes +
        w_lists * normalized_lists +
        w_tags * normalized_tags
    )
