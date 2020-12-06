import re
from time import sleep

import requests as req
from loguru import logger

import main
import vk_
from file_handler import read_config

re_titles = r'(?<=}]},"title":{"runs":\[{"text":").*?(?="}])'
re_videos = r'(?<={"gridVideoRenderer":{"videoId":").*?(?=")'


def to_send(title, video_id, index):
    channel = 'основном' if index == 0 else 'втором'
    link = f'https://youtu.be/{video_id}'
    message = f'Новое видео на {channel} канале:\n\n"{title}"\n{link}'
    vk_.send(message=message, category='youtube')
    logger.debug(f'New youtube video send successfully! {link}')


def get_videos(channel_id):
    url = f'https://youtube.com/channel/{channel_id}/videos'

    page = req.get(url).text

    video_ids = re.findall(re_videos, page, re.MULTILINE)
    video_ids.reverse()
    video_titles = re.findall(re_titles, page, re.MULTILINE)
    video_titles.reverse()

    return video_ids, video_titles


@logger.catch(onerror=lambda _: main.restart_thread(start_yt, 'youtube'))
def start_yt():

    print('Youtube thread running')

    channels = read_config('youtube', 'channels', list_=True)
    last_video_ids = dict()

    # Первоначальное заполнение video_id
    for index, channel in enumerate(channels):
        # Сколько каналов в конфиге, столько и ключей словаря. Затем к ключу с id канала добавим id каждого видео
        video_ids, _ = get_videos(channel)
        last_video_ids.update({channel: video_ids})

    try:
        while True:
            for channel_index, channel in enumerate(channels):
                new_video_ids, new_video_titles = get_videos(channel)

                for video_index, new_video_id in enumerate(new_video_ids):

                    if new_video_id not in last_video_ids[channel]:
                        to_send(title=new_video_titles[video_index], video_id=new_video_id, index=channel_index)

                        last_video_ids[channel].append(new_video_id)

                sleep(2.5)

    except Exception as exception:
        restart_timer = int(read_config('data', 'delay'))
        logger.error(f'{exception} | YOUTUBE_T')
        print(f'Restart after {restart_timer} (yt) seconds ...')
        sleep(restart_timer)
        start_yt()
