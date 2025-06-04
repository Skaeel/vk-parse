import re
import json
from unittest.mock import patch, MagicMock
from main import resolve_screen_name, get_wall_post, get_post_comments

def test_resolve_screen_name():
    mock_response = {
        "response": {
            "type": "group",
            "object_id": 123456789
        }
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = mock_response

        token = "test_token"
        screen_name = "example_group"
        result = resolve_screen_name(screen_name, token)

        assert result == mock_response["response"]
        mock_get.assert_called_once_with(
            "https://api.vk.com/method/utils.resolveScreenName", 
            params={
                "screen_name": screen_name,
                "access_token": token,
                "v": "5.131"
            }
        )

def test_get_wall_post():
    mock_response = {
        "response": {
            "items": [
                {
                    "id": 987654321,
                    "text": "Test post text",
                    "attachments": []
                }
            ]
        }
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = mock_response

        token = "test_token"
        owner_id = -123456789
        post_id = 987654321
        result = get_wall_post(owner_id, post_id, token)

        assert result == mock_response["response"]["items"][0]
        mock_get.assert_called_once_with(
            "https://api.vk.com/method/wall.getById", 
            params={
                "posts": f"{owner_id}_{post_id}",
                "access_token": token,
                "v": "5.131",
                "extended": 1
            }
        )

def test_get_post_comments():
    mock_response = {
        "response": {
            "items": [
                {
                    "id": 1,
                    "from_id": 123456789,
                    "text": "Test comment text"
                },
                {
                    "id": 2,
                    "from_id": 987654321,
                    "text": "Another test comment"
                }
            ]
        }
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = mock_response

        token = "test_token"
        post_id = 987654321
        owner_id = -123456789
        count = 100
        result = get_post_comments(post_id, owner_id, token, count)

        assert result == mock_response["response"]["items"]
        mock_get.assert_called_once_with(
            "https://api.vk.com/method/wall.getComments", 
            params={
                "owner_id": owner_id,
                "post_id": post_id,
                "count": count,
                "need_likes": 1,
                "access_token": token,
                "v": "5.131"
            }
        )

def test_get_wall_post_error():
    mock_response = {
        "error": {
            "error_code": 15,
            "error_msg": "Access denied"
        }
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = mock_response

        token = "test_token"
        owner_id = -123456789
        post_id = 987654321
        result = get_wall_post(owner_id, post_id, token)

        assert result is None

def test_get_post_comments_error():
    mock_response = {
        "error": {
            "error_code": 15,
            "error_msg": "Access denied"
        }
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = mock_response

        token = "test_token"
        post_id = 987654321
        owner_id = -123456789
        result = get_post_comments(post_id, owner_id, token)

        assert result == []

def test_ignore_telegram_links():
    links = [
        "https://t.me/example_channel", 
        "https://vk.com/example_group", 
        "https://vk.com/wall-123456789_987654321" 
    ]

    filtered_links = [link for link in links if "t.me" not in link]

    assert len(filtered_links) == 2
    assert "https://t.me/example_channel"  not in filtered_links

def test_regex_parsing():
    link = "https://vk.com/wall-123456789_987654321" 
    match = re.search(r"https?://vk\.com/([a-zA-Z0-9_\-]+)", link)
    wall_match = re.search(r"wall(-?\d+)_(\d+)", link)

    assert match.group(1) == "wall-123456789_987654321"
    assert wall_match.group(1) == "-123456789"
    assert wall_match.group(2) == "987654321"

def test_save_to_json(tmpdir):
    data = [
        {
            "screen_name": "example_group",
            "post": {
                "post_id": 987654321,
                "text": "Test post text",
                "attachments": [],
                "comments": []
            }
        }
    ]

    file_path = tmpdir.join("output.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    with open(file_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == data