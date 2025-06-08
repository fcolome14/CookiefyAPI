# import pytest
# from unittest.mock import MagicMock
# from app.services.post_service import PostService
# from app.schemas.post import ListCreate, ListUpdate
# from app.models.lists import List as ListModel

# @pytest.fixture
# def mock_post_service():
#     repo = MagicMock()
#     service = PostService(db=None, auth_code_service=None, time_utils=None)
#     service.post_repo = repo
#     return service, repo

# @pytest.mark.asyncio
# async def test_create_list_duplicate(mock_post_service):
#     service, repo = mock_post_service
#     repo.get_list_by_name.return_value = ListModel(id=1, name="List", owner=1)

#     result = await service.create_list(
#         1,
#         ListCreate(name="List", description="", is_public=True, accepts_contributions=False)
#     )

#     assert result["status"] == "error"
#     repo.add_list.assert_not_called()


# def test_update_list_with_invalid_sites(mock_post_service):
#     service, repo = mock_post_service
#     repo.get_list_by_list_id.return_value = ListModel(id=1, name="List", owner=1)
#     repo.get_site_ids_from_list.return_value = [1, 2]
#     repo.check_sites_id.return_value = False

#     update_payload = ListUpdate(**{
#         "id": 1,
#         "name": "New Name",
#         "description": "Updated",
#         "likes": 0,
#         "shares": 0,
#         "saves": 0,
#         "accepts_contributions": False,
#         "is_public": True,
#         "sites": [999],
#         "image": "https://example.com/image.jpg"
#     })

#     result = service._update_list(repo.get_list_by_list_id.return_value, update_payload)

#     assert result["status"] == "error"
#     assert "Invalid site IDs" in result["payload"]
