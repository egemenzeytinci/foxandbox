from attrdict import AttrDict
from bs4 import BeautifulSoup
from datetime import date
from db.model import Basic
from util.config import config
from util.log import logger
import json
import multiprocessing as mp
import requests
import time
import tqdm

BASE_PATH = ' http://www.imdb.com/title'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'


def get_page(path):
    """
    Get page source

    :return: http response
    :rtype: str
    """
    headers = {'User-Agent': USER_AGENT}
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

        # extract movie information from the json
        movie.img = get_poster(info)
        movie.description = get_description(info)
        movie.published_date = get_published_date(info)

        path = f'{BASE_PATH}/{movie_id}/mediaindex'
        info = get_information(path)
        movie.horizontal_image = get_horizontal_image(info)
    except BaseException as e:
        logger.error(f'{e} for title_id={movie_id}')
        time.sleep(10)

    return movie


def crawl(ids):
    """
    Crawl movies description and image url

    :param list ids: title ids
    """
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
        instance.is_crawled = True

        instances.append(instance)

    return instances
