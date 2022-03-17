import aiohttp
import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import requests
import csv

URL = 'https://blog.cs.money'
HEADERS = {'user-agent': UserAgent().random}


class NewsParsing:
    def __init__(self):
        self.url = None
        self.proxie = None
        self.timeout = None
        self.main_info = []
        self.all_news = []

    def load_config(self):
        with open("config.json", encoding='utf=8') as cfg:
            cfg_json = json.load(cfg)
            self.proxie = cfg_json['settings']['proxie']
            self.url = cfg_json['settings']['search_queries']
            self.timeout = cfg_json['settings']['timeout']

    def save_csv(self):
        with open(f'news.csv', 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Title', 'Views', 'Date', 'Url', 'Post', 'Images'])
            for item in self.main_info:
                writer.writerow([item['title'], item['views'], item['date'], item['href'], item['text'], item['images']])

    # get news urls
    def get_all_urls_news(self):
        for tag in self.url:
            s = requests.Session()
            res = s.get(URL, params={'s': tag}, headers=HEADERS, proxies=self.proxie)
            soup = BeautifulSoup(res.text, 'lxml')
            urls = soup.select('.card-default[href]')
            self.all_news.extend([auto.get('href') for auto in soup.select('.card-default[href]')])
            print(f'{len(urls)} news were found in the "{tag}" category')

    # get title, views, publish, text, image urls
    async def pars_info(self, url, session, en):
        async with session.get(url, proxy=self.proxie['http'], headers=HEADERS) as res:
            await asyncio.sleep(self.timeout)
            soup = BeautifulSoup(await res.text(), 'lxml')
            top_info = soup.find(class_='single__article-top')
            title = top_info.find(class_='single__article-title').get_text(strip=True)
            date, views = top_info.find(class_='likes'), top_info.find(class_='views')
            text = [post.get_text(strip=True) for post in soup.select('.single__article > p')]
            images_urls = [image.get('href') for image in soup.select('.wp-block-image > a[href]')]
            print(f'[{en}/{len(self.all_news)}] {title}..\n{url}')
            self.main_info.append(
                {'href': url, 'title': title, 'date': date.get_text(strip=True),
                 'views': views.get_text(strip=True),
                 'text': '\n\n'.join(text), 'images': '\n'.join(images_urls)})

    async def get_data(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.pars_info(tag, session, en) for en, tag in enumerate(self.all_news)]
            await asyncio.gather(*tasks)


if __name__ == '__main__':
    main_parser = NewsParsing()
    main_parser.load_config()
    main_parser.get_all_urls_news()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_parser.get_data())
    main_parser.save_csv()