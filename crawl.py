import urllib.parse
from typing import TypedDict
import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup, Tag

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int = 1, max_pages: int = 20) -> None:
        self.base_url = base_url
        self.base_domain = urllib.parse.urlparse(base_url).hostname
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = aiohttp.ClientSession()
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        if self.should_stop:
            return False
        async with self.lock:
            if len(self.visited) >=self.max_pages:
                self.should_stop = True
                print('Reached maximum number of pages to crawl.')
                return False
            if normalized_url in self.visited:
                return False
            else:
                self.visited.add(normalized_url)
                return True

    async def get_html(self, url: str):
        try:
            async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as r:
                r.raise_for_status()
                if r.headers.get('content-type') in 'text/html':
                    raise Exception('Content-type is not text/html')
                return await r.text()
        except Exception as e:
            print(f'ERROR: {e}')
            return 'ERROR'


    async def crawl_page(self, base_url, current_url=None, page_data={}):
        if self.should_stop:
            print('!-==stopped==-!')
            return
        print(f'\n--Checking Link: {current_url}--\n')
        if self.base_domain != urllib.parse.urlparse(current_url).hostname:
            print(f'\t--different Domains--\n')
            return

        normal_curr_url = normalize_url(current_url)
        visted_page = await self.add_page_visit(normal_curr_url)
        if not visted_page:
            print(f'\t--already crawled too--\n')
            return

        async with self.semaphore:

            print(f'\n\t--Getting html of {normal_curr_url}--\n')
            curr_html = await self.get_html(current_url)

            print(f'\n\t--Extracting PageData--\n')
            async with self.lock:
                page_data[normal_curr_url] = extract_page_data(curr_html, current_url)


            print(f'\n\t--Checking for more links--\n')
            further_links = page_data[normal_curr_url].get('outgoing_links')
            print(f'\t\tFound {further_links}\n')

            tasks = []
            for link in further_links:
                print(f'--checking link: {link}--')
                task = (asyncio.create_task(self.crawl_page(base_url, link, page_data)))
                tasks.append(task)
        await asyncio.gather(*tasks)

        return page_data

    async def crawl(self, base_url):
        self.page_data = await self.crawl_page(self.base_url, self.base_url)
        return self.page_data

async def crawl_site_async(base_url: str, max_concurrency: int = 1, max_pages: int = 50):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        final_page_data = await crawler.crawl(base_url)
        return final_page_data



def extract_page_data(html: str, page_url: str) -> PageData:
    normal_url = f'https://{normalize_url(page_url)}'
    page_data = PageData(
        url = normal_url,
        heading = get_heading_from_html(html),
        first_paragraph = get_first_paragraph_from_html(html),
        outgoing_links = get_urls_from_html(html, normal_url),
        image_urls = get_images_from_html(html, normal_url)
    )
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
