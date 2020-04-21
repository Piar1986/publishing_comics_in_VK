import os
import random
import requests
from dotenv import load_dotenv
from pathlib import Path


def get_comic_count():
    url = "http://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    last_comic_number = response.json()['num']
    return last_comic_number


def get_random_comic(comic_count):
    random_comic_number = random.randint(1, comic_count)
    url = f'https://xkcd.com/{random_comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    response_result = response.json()
    author_comment = response_result['alt']
    image_url = response_result['img']
    return image_url, author_comment


def download_comic_image(url, filename, folder='images'):
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def get_upload_image_url():
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'group_id':group_id,
        'access_token':access_token, 
        'v':VERSION
    }
    response = requests.get(url, params=params)
    upload_image_url = response.json()['response']['upload_url']
    return upload_image_url


def upload_image_to_server(url, filename, folder='images'):
    filepath = os.path.join(folder, filename)
    with open(filepath, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    response_result = response.json()
    server = response_result['server']
    photo = response_result['photo']
    hash_code = response_result['hash']
    return server, photo, hash_code


def save_image_in_group_album(server, photo, hash_code):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'server':server,
        'photo':photo,
        'hash':hash_code,
        'group_id':group_id,
        'access_token':access_token, 
        'v':VERSION,
    }
    response = requests.post(url, params=params)
    response_result = response.json()['response']
    response.raise_for_status()
    media_id = response_result[0]['id']
    owner_id = response_result[0]['owner_id']
    return media_id, owner_id


def post_to_group(media_id, owner_id, comment):
    url = 'https://api.vk.com/method/wall.post'
    params = {
        'owner_id':f'-{group_id}',
        'attachments':f'photo{owner_id}_{media_id}',
        'message':comment,
        'from_group':0,
        'access_token':access_token, 
        'v':VERSION,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()


def remove_posted_image(filename, folder='images'):
    filepath = os.path.join(folder, filename) 
    try:   
        os.remove(filepath)
    except OSError:
        print('Не найден файл для удаления:', filepath)


if __name__ == '__main__':
    
    version = 5.103
    
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN')
    group_id = os.getenv('GROUP_ID')

    Path('images').mkdir(parents=True, exist_ok=True)

    comic_count = get_comic_count()

    comic_image_url, comic_author_comment = get_random_comic(comic_count)

    comic_filename = comic_image_url.split('/')[-1]
    download_comic_image(comic_image_url, comic_filename)

    upload_image_url = get_upload_image_url()

    server, photo, hash_code = upload_image_to_server(upload_image_url, comic_filename)

    media_id, owner_id = save_image_in_group_album(server, photo, hash_code)
    
    post_to_group(media_id, owner_id, comic_author_comment)

    remove_posted_image(comic_filename)