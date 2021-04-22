import re
from time import sleep

import requests as req
from loguru import logger

import main
import vk_
from file_handler import read_config

re_titles = r'(?<=}]},"title":{"runs":\[{"text":").*?(?="}])'
re_videos = r'(?<={"gridVideoRenderer":{"videoId":").*?(?=")'

re_date = r'(?<="publishedTimeText":{"simpleText":"\d ).*?(?= ago)'
list_bad_dates = ['day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years']

# re_date_ru = r'(?<="publishedTimeText":{"simpleText":"\d ).*?(?= назад)'
# list_bad_dates_ru = ['день', 'дня', 'дней', 'неделю', 'недели', 'недель', 'месяц', 'месяца', 'месяцей', 'год', 'года', 'лет']


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
    video_dates = re.findall(re_date, page, re.MULTILINE)
    # video_dates = re.findall(re_date_ru, page, re.MULTILINE)
    video_dates.reverse()

    return video_ids, video_titles, video_dates


@logger.catch(onerror=lambda _: main.restart_thread(start_yt, 'youtube'))
def start_yt():

    print('Youtube thread running')

    channels = read_config('youtube', 'channels', list_=True)
    last_video_ids = dict()

    # Первоначальное заполнение video_id
    for index, channel in enumerate(channels):
        # Сколько каналов в конфиге, столько и ключей словаря. Затем к ключу с id канала добавим id каждого видео
        video_ids, _, _ = get_videos(channel)
        last_video_ids.update({channel: video_ids})

    try:
        while True:
            for channel_index, channel in enumerate(channels):
                new_video_ids, new_video_titles, new_video_date = get_videos(channel)

                for video_index, new_video_id in enumerate(new_video_ids):

                    # if new_video_id not in last_video_ids[channel] and new_video_date not in list_bad_dates_ru:
                    if new_video_id not in last_video_ids[channel] and new_video_date not in list_bad_dates:
                        video_title = new_video_titles[video_index]

                        video_title = video_title.replace('\\u0026', '&')  # Хардкод фикс M&B

                        to_send(title=video_title, video_id=new_video_id, index=channel_index)
                        last_video_ids[channel].append(new_video_id)

                sleep(2.5)

    except Exception as exception:
        restart_timer = int(read_config('data', 'delay'))
        logger.error(f'{exception} | YOUTUBE_T')
        print(f'Restart after {restart_timer} (yt) seconds ...')
        sleep(restart_timer)
        start_yt()
