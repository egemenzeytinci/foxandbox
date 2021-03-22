from attrdict import AttrDict
from bs4 import BeautifulSoup
from db.model import Basic
from util.config import config
from util.log import logger
import json
import multiprocessing as mp
import requests
import time
import tqdm

BASE_PATH = ' http://www.imdb.com/title'


def get_page(path):
    """
    Get page source

    :return: http response
    :rtype: str
    """
    resp = requests.get(path)

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


def get_image_and_description(info):
    """
    Get movie poster and description

    :param json info: movie json
    :return: image and description
    :rtype: tuple
    """
    img = description = None

    if 'image' in info.keys():
        img = info.image
    if 'description' in info.keys():
        description = info.description

    return img, description


def get_horizontal_image(info):
    """
    Get horizontal image

    :param json info: the json which contains movie images
    :return: horizontal image
    :rtype: str
    """
    if 'image' not in info.keys():
        return

    # returns dictionary if only one picture, otherwise list
    if isinstance(info.image, dict):
        first_img = info.image
    elif isinstance(info.image, tuple):
        first_img = info.image[0]

    # get image width and height
    width, height = int(first_img.width), int(first_img.height)

    if not 1.33 < width / height < 1.66:
        return

    return first_img.url


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


def append(movie_id):
    """
    Create beautiful soup

    :param str movie_id: movie id like tt0000001
    :return: image, description and horizontal image
    :rtype: tuple
    """
    img = description = horizontal_image = None
    try:
        path = f'{BASE_PATH}/{movie_id}'
        info = get_information(path)
        img, description = get_image_and_description(info)

        path = f'{BASE_PATH}/{movie_id}/mediaindex'
        info = get_information(path)
        horizontal_image = get_horizontal_image(info)
    except BaseException as e:
        logger.error(e)
        time.sleep(10)

    return movie_id, img, description, horizontal_image


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
        # create instance
        instance = Basic()
        instance.title_id = record[0]
        instance.image_url = record[1]
        instance.description = record[2]
        instance.horizontal_image = record[3]
        instance.is_crawled = True

        instances.append(instance)

    return instances
