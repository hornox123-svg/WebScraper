import urllib.parse
from typing import TypedDict
from bs4 import BeautifulSoup, Tag

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def extract_page_data(html: str, page_url: str) -> PageData:
    normal_url = f'https://{normalize_url(page_url)}'
    page_data = PageData(
        url = normal_url,
        heading = get_heading_from_html(html),
        first_paragraph = get_first_paragraph_from_html(html),
        outgoing_links = get_urls_from_html(html, normal_url),
        image_urls = get_images_from_html(html, normal_url)
    )
    print(f'\n{page_data}\n')
    return page_data


def normalize_url(url: str) -> str:
    url_netloc = urllib.parse.urlsplit(url).netloc
    url_path = urllib.parse.urlsplit(url).path
    if url_path and url_path[-1] == '/':
        url_path = url_path[:-1]
    normal_url = url_netloc + url_path
    return normal_url

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    if soup.h1:
        return soup.h1.string
    elif soup.h2:
        return soup.h2.string
    else:
        return ''


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('main'):
        if soup.main.find('p'):
            return soup.main.p.string
    if soup.find('p'):
        return soup.p.string
    else:
        return ''


def get_urls_from_html(html: str, base_url: str) -> list[str] | str:
    try:
        soup = BeautifulSoup(html, 'html.parser')
        urls = soup.find_all("a")
        abs_urls = []
        for url in urls:
            url_parsed = url.get('href')
            abs_urls.append(urllib.parse.urljoin(base_url, url_parsed))
        return abs_urls
    except Exception as e:
        return f'Error: {e}'

def get_images_from_html(html: str, base_url: str) -> list[str] | str:
    try:
        soup = BeautifulSoup(html, 'html.parser')
        imgs = soup.find_all("img")
        abs_imgs = []
        for img in imgs:
            img_parsed = img.get('src')
            abs_imgs.append(urllib.parse.urljoin(base_url, img_parsed))
        return abs_imgs
    except Exception as e:
        return f'Error: {e}'
