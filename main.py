import requests
from pathlib import Path
import os
from dotenv import load_dotenv
import random
import shutil


def find_number_latest_comic():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    return response.json()['num']


def publish_comic(image_id, owner_id, token, text):
    payload = {
        'owner_id': '-223447832',
        'access_token': token,
        'from_group': 1,
        'v': '5.154',
        'message': text,
        'attachments': f'photo{owner_id}_{image_id}'
    }
    url = 'https://api.vk.com/method/wall.post'
    response = requests.post(url, data=payload)
    response.raise_for_status()


def save_photo(photo, server, hash, token):
    payload = {
        'access_token': token,
        'group_id': '223447832',
        'photo': photo,
        'v': '5.154',
        'server': server,
        'hash': hash
    }
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()['response'][-1]


def upload_photo_to_address(name_folder, upload_url):
    with open(os.path.join(name_folder, f"image.png"), 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()


def get_upload_url(client_id, token):
    payload = {
        'client_id': client_id,
        'access_token': token,
        'v': '5.154',
        'group_id': '223447832'
    }
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_comic(last_comic_num):
    url = f'https://xkcd.com/{random.randint(0, last_comic_num)}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def main():
    load_dotenv()
    client_id = os.environ["VK_CLIENT_ID"]
    vk_token = os.environ['VK_TOKEN']
    last_comic_num = find_number_latest_comic()
    comic = get_comic(last_comic_num)
    name_folder = 'files'
    Path(name_folder).mkdir(exist_ok=True)
    with open(os.path.join(name_folder, f"image.png"), 'wb') as file:
        file.write(get_image(comic['img']))
    upload_url = get_upload_url(client_id, vk_token)
    address = upload_photo_to_address(name_folder, upload_url)
    album = save_photo(address['photo'], address['server'], address['hash'], vk_token)
    publish_comic(album['id'], album['owner_id'], vk_token, comic['alt'])
    shutil.rmtree(name_folder)


if __name__ == "__main__":
    main()
