import requests
from pathlib import Path
import os
from dotenv import load_dotenv
import random
import shutil


def check_vk_response(response):
    if response.history:
            raise requests.HTTPError


def publish_comic(image_id, owner_id, token, text, group_id):
    payload = {
        'owner_id': f'-{group_id}',
        'access_token': token,
        'from_group': 1,
        'v': '5.154',
        'message': text,
        'attachments': f'photo{owner_id}_{image_id}'
    }
    url = 'https://api.vk.com/method/wall.post'
    response = requests.post(url, data=payload)
    response.raise_for_status()
    check_vk_response(response)


def save_photo(photo, server, hash, token, group_id):
    payload = {
        'access_token': token,
        'group_id': group_id,
        'photo': photo,
        'v': '5.154',
        'server': server,
        'hash': hash
    }
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(url, data=payload)
    response.raise_for_status()
    check_vk_response(response)
    return response.json()['response'][-1]


def upload_photo_to_address(name_folder, upload_url):
    with open(os.path.join(name_folder, f"image.png"), 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    check_vk_response(response)
    return response.json()


def get_upload_url(token, group_id):
    payload = {
        'access_token': token,
        'v': '5.154',
        'group_id': group_id
    }
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=payload)
    check_vk_response(response)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_comic(name_folder):
    last_comic_response = requests.get('https://xkcd.com/info.0.json')
    last_comic_response.raise_for_status()
    check_vk_response(last_comic_response)
    last_comic_num = last_comic_response.json()['num']
    url = f'https://xkcd.com/{random.randint(0, last_comic_num)}/info.0.json'
    random_comic_response = requests.get(url)
    random_comic_response.raise_for_status()
    check_vk_response(random_comic_response)
    comic= random_comic_response.json()
    Path(name_folder).mkdir(exist_ok=True)
    image_response = requests.get(comic['img'])
    image_response.raise_for_status()
    check_vk_response(image_response)
    image = image_response.content
    with open(os.path.join(name_folder, f"image.png"), 'wb') as file:
        file.write(image)
    return comic


def main():
    load_dotenv()
    # client_id = os.environ["VK_CLIENT_ID"]
    vk_token = os.environ['VK_TOKEN']
    group_id = os.environ['VK_GROUP_ID']
    name_folder = 'files'
    try:
        comic = get_comic(name_folder)
        upload_url = get_upload_url(vk_token, group_id)
        address = upload_photo_to_address(name_folder, upload_url)
        album = save_photo(address['photo'], address['server'], address['hash'], vk_token, group_id)
        publish_comic(album['id'], album['owner_id'], vk_token, comic['alt'], group_id)
    except requests.HTTPError:
        print('HTTP error occurred')
    except requests.ConnectionError:
        print('Connection is interrupted')
    finally:
        shutil.rmtree(name_folder)


if __name__ == "__main__":
    main()
