import json
import multiprocessing as mp
import os
import requests
import time
import tqdm
from attrdict import AttrDict
from boto3.session import Session
from bs4 import BeautifulSoup
from datetime import date
from db.model import Basic
from PIL import Image
from util.config import config
from util.log import logger

# request headers
BASE_PATH = ' http://www.imdb.com/title'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
ACCEPT_LANGUAGE = 'en-US,en;q=0.5'

# image maximum size
MAX_WIDTH = 1792
MAX_HEIGHT = 828

# cloud storage client
session = Session()

s3 = session.client(
    service_name='s3',
    aws_access_key_id=config.storage.access_key,
    aws_secret_access_key=config.storage.secret_key,
    endpoint_url='https://' + config.storage.host,
    region_name=config.storage.region,
)


def get_page(path):
    """
    Get page source

    :return: http response
    :rtype: str
    """
    headers = {
        'User-Agent': USER_AGENT,
        'Accept-Language': ACCEPT_LANGUAGE
    }
    resp = requests.get(path, headers=headers)

    return resp.text if resp.status_code == 200 else None


def parse(content):
    """
    Get json which contains movie information

    :param bs4.BeautifulSoup content: BeautifulSoup from html content
    :return: the json which contains movie information
    :rtype: json
    """
    # get ld json
    attrs = {'type': 'application/ld+json'}
    full_info = content.find('script', attrs=attrs).string

    return AttrDict(json.loads(full_info))


def get_information(path):
    """
    Get movie information by path

    :param str path: the url for crawling
    :return: response json
    :rtype: json
    """
    resp = get_page(path)
    soup = BeautifulSoup(resp, 'html.parser')

    return parse(soup)


def get_poster(info):
    """
    Get movie poster

    :param json info: movie json
    :return: image url
    :rtype: str
    """
    if 'image' not in info.keys():
        return None

    return info.image


def get_description(info):
    """
    Get movie description

    :param json info: movie json
    :return: description
    :rtype: str
    """
    if 'description' not in info.keys():
        return None

    return info.description


def get_horizontal_image(info):
    """
    Get horizontal image

    :param json info: the json which contains movie images
    :return: horizontal image
    :rtype: str
    """
    if 'image' not in info.keys():
        return None

    # returns dictionary if only one picture, otherwise list
    if isinstance(info.image, dict):
        first_img = info.image
    elif isinstance(info.image, tuple):
        first_img = info.image[0]

    # get image width and height
    width, height = int(first_img.width), int(first_img.height)

    if not 1.33 < width / height < 1.66:
        return None

    return first_img.url


def get_published_date(info):
    """
    Get published date of the movie

    :param json info: the json which contains movie images
    :return: published date
    :rtype: datetime.date
    """
    if 'datePublished' not in info.keys():
        return None

    return date.fromisoformat(info.datePublished)


def save_image(movie_id, url, horizontal=False):
    """
    Save image to cloud storage

    :param str movie_id: title id of the imdb
    :param bool horizontal: horizontal or not
    :return: upload status
    :rtype: bool
    """
    if not url:
        return False

    try:
        temp_path = f'{config.system.temporary}/images'

        name = f'{movie_id}_horizontal' if horizontal else f'{movie_id}'

        jpg_path = f'{temp_path}/{name}.jpg'
        webp_path = f'{temp_path}/{name}.webp'

        # get image content by using image url
        headers = {
            'Accept-Encoding': 'identity',
            'Connection': 'Keep-Alive',
        }

        bs = requests.get(url, stream=True, headers=headers)

        with open(jpg_path, 'wb') as f:
            # write image content to local file
            for b in bs:
                f.write(b)

        img = Image.open(jpg_path).convert('RGB')
        width, height = img.size

        # resize image
        if width >= MAX_WIDTH or height >= MAX_HEIGHT:
            width_ratio = width / MAX_WIDTH
            height_ratio = height / MAX_HEIGHT

            # get the best ratio
            min_ratio = min(width_ratio, height_ratio)

            nw = int(width / min_ratio)
            nh = int(height / min_ratio)

            # resize image for best ratio
            img = img.resize((nw, nh))

        # save image as webp file
        img.save(webp_path, 'WEBP')

        bucket = config.storage.bucket
        object_name = f'{config.storage.folder}/{name}.webp'

        # upload to object storage
        s3.upload_file(webp_path, bucket, object_name)

        # remove files from local path
        os.remove(jpg_path)
        os.remove(webp_path)

        return True
    except BaseException as e:
        logger.error(e)
        return False


def append(movie_id):
    """
    Create beautiful soup

    :param str movie_id: movie id like tt0000001
    :return: image, description, horizontal image and published date
    :rtype: tuple
    """
    movie = AttrDict()

    try:
        movie.title_id = movie_id

        path = f'{BASE_PATH}/{movie_id}'
        info = get_information(path)

        # save poster image to cloud
        poster_img = get_poster(info)
        movie.has_image = save_image(movie_id, poster_img)

        # extract movie information from the json
        movie.description = get_description(info)
        movie.published_date = get_published_date(info)

        path = f'{BASE_PATH}/{movie_id}/mediaindex'
        info = get_information(path)

        # save horizontal image to cloud
        horizontal_img = get_horizontal_image(info)
        _ = save_image(movie_id, horizontal_img, horizontal=True)
    except BaseException as e:
        logger.error(f'{e} for title_id={movie_id}')
        time.sleep(10)

    return movie


def crawl(ids):
    """
    Crawl movies description and image url

    :param list ids: title ids
    """
    temp_path = f'{config.system.temporary}/images'

    # create temporary path if not exists for images
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # create pool
    pool = mp.Pool(config.system.workers)

    records = list(tqdm.tqdm(pool.imap(append, ids), total=len(ids)))
    pool.close()
    pool.join()

    instances = []
    for record in records:
        if not record.get('title_id'):
            continue

        # create instance
        instance = Basic()
        instance.title_id = record.get('title_id')
        instance.image_url = record.get('img')
        instance.description = record.get('description')
        instance.horizontal_image = record.get('horizontal_image')
        instance.published_date = record.get('published_date')
        instance.has_image = record.get('has_image')
        instance.is_crawled = True

        instances.append(instance)

    return instances
