from datetime import datetime
import logging
import json
import re

import requests

from mods.util import q_file_exists, q_file_expired, download_q_file, read_q_file

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Ailurus/68.0'}
DOUBAN_MOVIE_JSON_API = 'https://moviedb.8610000.xyz'


def get_movie_id(q_movies, title, year):
    mid = None
    for movie in q_movies:
        if (movie['original_title'] == title or ''.join(movie['title'].split()) == ''.join(title.split())) and movie['year'] == year:
            mid = movie['id']
            break
    return mid


def get_re_info(downloaded_dir, movie_re):
    re_result = re.match(movie_re, downloaded_dir.split('/')[-2])
    if re_result and (re_result.group(1), re_result.group(2)):
        return re_result.group(1), re_result.group(2)
    return None, None


def get_movie_info(title, year):
    logging.info('开始抓取 {} ...'.format(title))
    if not q_file_exists() or q_file_expired():
        download_q_file()
    q_movies = read_q_file()
    mid = get_movie_id(q_movies, title, year)

    url = DOUBAN_MOVIE_JSON_API + '/data/{}.json'.format(mid)
    r = requests.get(url, headers=HEADERS)
    r.encoding = 'utf-8'
    info_json = json.loads(r.text)
    return {
        'title': info_json['title'],
        '_type': '剧集' if info_json['episodes_count'] else '电影',
        'original_title': info_json['original_title'],
        'intro': info_json['intro'] if 'intro' in info_json and info_json['intro'] else '',
        'card_subtitle': info_json['card_subtitle'] if 'card_subtitle' in info_json and info_json['card_subtitle'] else '',
        'year': info_json['year'],
        'update_date': datetime.now(),
        'sharing_url': info_json['sharing_url'],
        'cover_url': info_json['cover_url'] if 'cover_url' in info_json and info_json['cover_url'] else info_json['pic']['normal'],
        'douban_rating': str(info_json['rating']['value']) if info_json['rating'] else '暂无'
    }
