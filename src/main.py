import requests
import json
import dotenv
import os
import re

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

def get_wall_post(owner_id, post_id, token):
    url = f"https://api.vk.com/method/wall.getById"
    params = {
        "posts": f"{owner_id}_{post_id}",
        "access_token": token,
        "v": "5.131",
        "extended": 1
    }
    response = requests.get(url, params=params).json()
    if "response" in response and response["response"]["items"]:
        return response["response"]["items"][0]
    else:
        print(f"Error getting post {owner_id}_{post_id}: {response}")
        return None

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
        print(f"Error getting comments for post {owner_id}_{post_id}: {response}")
        return []

if __name__ == "__main__":
    token = os.getenv("ACCESS_TOKEN")

    with open("Destructive.txt", "r", encoding="utf-8") as f:
        links = [line.strip() for line in f]

    all_data = []

    for link in links:
        print(f"Processing link: {link}")

        if "t.me" in link:
            print(f"Ignoring Telegram link: {link}")
            continue

        match = re.search(r"https?://vk\.com/([a-zA-Z0-9_\-]+)", link)
        if match:
            screen_name = match.group(1)

            wall_match = re.search(r"wall(-?\d+)_(\d+)", link)
            if wall_match:
                owner_id = int(wall_match.group(1))
                post_id = int(wall_match.group(2))

                post = get_wall_post(owner_id, post_id, token)
                if post:
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

                    comments = get_post_comments(post_id, owner_id, token)
                    post_info["comments"] = [{"comment_id": c.get("id"), "from_id": c.get("from_id"), "text": c.get("text")} for c in comments]

                    all_data.append({
                        "screen_name": screen_name,
                        "post": post_info
                    })

            else:
                info = resolve_screen_name(screen_name, token)
                if not info:
                    print(f"Could not resolve screen_name: {screen_name}")
                    continue

                object_type = info["type"]
                object_id = info["object_id"]

                if object_type == "group":
                    object_id = -object_id

                all_data.append({
                    "screen_name": screen_name,
                    "object_id": object_id,
                    "type": object_type
                })

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print("Data successfully saved to output.json")