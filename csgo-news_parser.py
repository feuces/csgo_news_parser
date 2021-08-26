import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv

URL = 'https://blog.cs.money'

# Author: feuces
# Git: https://github.com/feuces

HEADERS = {'user-agent': UserAgent().random}
PROXIES = {'http': 'PROXIE'}

search_queries = ('Гайды', 'Киберспорт')


# Save to CSV table
def save_csv(items, path):
    with open(f'{path}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название статьи', 'Количество просмотров', 'Дата публикации', 'Ссылка', 'Текст'])
        for item in items:
            writer.writerow([item['tittle'], item['views'], item['date'], item['href'], item['text']])


# Get main HTML body
def get_main_html(url, params=None):
    r = requests.get(url, headers=HEADERS, proxies=PROXIES, params=params)
    return r


# Get links to news
def get_links(html, key):
    soup = BeautifulSoup(html.text, 'html.parser')
    news = soup.find_all('a', class_='card-default')
    news_links = [{'href': auto.get('href')} for auto in news]
    print(f'В категории "{key}" найдено {len(news_links)} новостей. Начинаем работу.\n')
    return news_links


# Collecting basic data
def get_info_news(links):
    all_news = list()
    for en, link in enumerate(links, 1):
        if 'https://blog.cs.money' in link['href']:
            html = get_main_html(link['href'])
            soup = BeautifulSoup(html.text, 'html.parser')
            text = [post.get_text(strip=True) for post in soup.select('.single__article > p')]
            tittle = soup.find('h1', class_='single__article-title').get_text(strip=True)
            date = soup.find('div', class_='single__article-top').find(class_='likes').get_text(strip=True)
            views = soup.find('div', class_='single__article-top').find(class_='views').get_text(strip=True)
            all_news.append(
                {'href': link['href'], 'tittle': tittle, 'date': date, 'views': views, 'text': '\n\n'.join(text)})
            print(f'[{en}/{len(links)}] {tittle}')
    return all_news


def parsing(keywords):
    s = requests.Session()
    s.headers.update(HEADERS)
    s.proxies.update(PROXIES)
    html = get_main_html(URL)
    html.raise_for_status()
    for key in keywords:
        html = get_main_html(URL, params={'s': key})
        links = get_links(html, key)
        save_csv(get_info_news(links), key)
        print(f'\nПарсинг статей по запросу "{key}" завершен и был сохранен в файл {key}.csv\n')


if __name__ == '__main__':
    parsing(search_queries)

