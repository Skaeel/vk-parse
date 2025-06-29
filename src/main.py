import requests
import json
import dotenv
import os
import re
import time

from log import setup_logger

logger = setup_logger("vk-parse", "INFO")
dotenv.load_dotenv()

def resolve_screen_name(screen_name, token):
    url = f"https://api.vk.com/method/utils.resolveScreenName"
    params = {
        "screen_name": screen_name,
        "access_token": token,
        "v": "5.131"
    }
    response = requests.get(url, params=params).json()
    return response.get("response")

def get_wall_posts(owner_id, token, count=100):
    url = f"https://api.vk.com/method/wall.get"
    params = {
        "owner_id": owner_id,
        "count": count,
        "access_token": token,
        "v": "5.131",
        "extended": 1
    }
    response = requests.get(url, params=params).json()
    if "response" in response and response["response"]["items"]:
        return response["response"]["items"]
    else:
        logger.error(f"Error getting posts for owner_id {owner_id}: {response}")
        return []

def get_post_comments(post_id, owner_id, token, count=100):
    url = f"https://api.vk.com/method/wall.getComments"
    params = {
        "owner_id": owner_id,
        "post_id": post_id,
        "count": count,
        "need_likes": 1,
        "access_token": token,
        "v": "5.131"
    }
    response = requests.get(url, params=params).json()
    if "response" in response:
        return response["response"]["items"]
    else:
        logger.error(f"Error getting comments for post {owner_id}_{post_id}: {response}")
        return []

if __name__ == "__main__":
    token = os.getenv("ACCESS_TOKEN")

    with open("Destructive.txt", "r", encoding="utf-8") as f:
        links = [line.strip() for line in f]

    all_data = []

    for link in links:
        logger.info(f"Processing link: {link}")

        if "t.me" in link:
            logger.info(f"Ignoring Telegram link: {link}")
            continue

        match = re.search(r"https?://vk\.com/([a-zA-Z0-9_\-]+)", link)
        if match:
            screen_name = match.group(1)

            info = resolve_screen_name(screen_name, token)
            if not info:
                logger.info(f"Could not resolve screen_name: {screen_name}")
                continue

            object_type = info["type"]
            object_id = info["object_id"]

            if object_type == "group":
                object_id = -object_id

            posts = get_wall_posts(object_id, token)
            group_info = {
                "screen_name": screen_name,
                "object_id": object_id,
                "type": object_type,
                "posts": []
            }

            for post in posts:
                post_info = {
                    "post_id": post.get("id"),
                    "text": post.get("text"),
                    "attachments": [],
                    "comments": []
                }

                if "attachments" in post:
                    for attachment in post["attachments"]:
                        if attachment["type"] == "photo":
                            photo = attachment["photo"]
                            max_size_url = max(photo["sizes"], key=lambda x: x["width"] * x["height"])["url"]
                            post_info["attachments"].append({"type": "photo", "url": max_size_url})

                comments = get_post_comments(post.get("id"), object_id, token)
                post_info["comments"] = [{"comment_id": c.get("id"), "from_id": c.get("from_id"), "text": c.get("text")} for c in comments]

                group_info["posts"].append(post_info)

            all_data.append(group_info)

            time.sleep(0.5)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    logger.info("Data successfully saved to output.json")