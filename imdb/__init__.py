from bs4 import BeautifulSoup
from db.model import Basic
from util.config import config
import json
import multiprocessing as mp
import requests
import time
import tqdm

BASE_PATH = ' http://www.imdb.com/title/'


def get_page(movie_id):
    """
    Get page source

    :param str movie_id: movie id like tt0000001
    :return: http response
    :rtype: str
    """
    full_path = BASE_PATH + movie_id
    resp = requests.get(full_path)
    return resp.text if resp.status_code == 200 else None


def parse(content):
    """
    Get image url, description

    :param bs4.BeautifulSoup content: BeautifulSoup from html content
    :return: image and description
    :rtype: tuple
    """
    img = description = None

    attrs = {'type': 'application/ld+json'}
    full_info = content.find('script', attrs=attrs).text
    info_dict = json.loads(full_info)

    if 'image' in info_dict.keys():
        img = info_dict['image']
    if 'description' in info_dict.keys():
        description = info_dict['description']

    return img, description


def append(movie_id):
    """
    Create beautiful soup

    :param str movie_id: movie id like tt0000001
    :return: image and description
    :rtype: tuple
    """
    img = description = None

    try:
        resp = get_page(movie_id)
        soup = BeautifulSoup(resp, 'html.parser')
        img, description = parse(soup)
    except BaseException:
        time.sleep(10)

    return movie_id, img, description


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
        instance.is_crawled = True

        instances.append(instance)

    return instances
