import argparse
import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import urlparse, urlsplit, unquote, urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_base_url(url):
    parsed_uri = urlparse(url)
    base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return base_url


def get_file_extension_from_url(url):
    url_structure = urlsplit(url)
    path = unquote(url_structure.path)

    head, tail = os.path.split(path)
    root, ext = os.path.splitext(tail)

    return ext


def request_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def save_to_file(content, filename, folder):
    filepath = Path.cwd() / folder / sanitize_filename(filename)
    with open(filepath, "wb") as file:
        file.write(content)
    return filepath.relative_to(Path.cwd())


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """

    response = request_from_url(url)
    Path(folder).mkdir(parents=True, exist_ok=True)
    if not Path(filename).suffix:
        filename = f"{filename}.txt"
    logging.info(f"Скачиваем книгу по адресу {url} в файл {sanitize_filename(filename)}")
    return save_to_file(response.content, filename, folder)


def download_image(url, filename, folder='books/'):
    """Функция для скачивания графических файлов.
    Args:
        url (str): Cсылка на картинку, которую хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = request_from_url(url)
    Path(folder).mkdir(parents=True, exist_ok=True)

    if not Path(filename).suffix:
        image_extension = get_file_extension_from_url(url)
        filename = f"{filename}{image_extension}"

    logging.info(f"Скачиваем обложку книги по адресу {url} в файл {sanitize_filename(filename)}")
    return save_to_file(response.content, filename, folder)


def get_book_html(url):
    logging.info(f"Получаем данные со страницы книги {url}")
    response = request_from_url(url)
    return response.text


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')
    title_tag = soup.find(id='content').find('h1')
    title_text = title_tag.text
    name, author = title_text.split(" :: ")
    name_book = name.strip()
    author_book = author.strip()
    image_url = soup.find("div", class_="bookimage").find("a").find("img").attrs['src']
    book_url_selector = soup.select_one(".d_book:nth-of-type(1) tr:nth-of-type(4) a:nth-of-type(2)")
    book_url = book_url_selector["href"] if book_url_selector else None
    download_url = book_url

    comments = list(
        comment_div.find("span", class_="black").text for comment_div in soup.findAll("div", class_="texts"))
    genres = list(genre_el.text for genre_el in soup.find("span", class_="d_book").findAll("a"))

    book = {
        "name": name_book,
        "author": author_book,
        "comments": comments,
        "genres": genres,
        "image_url": image_url,
        "download_url": download_url,
    }
    return book


def save_books(books_info, filename="books.json", folder="books/"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    if not Path(filename).suffix:
        filename = f"{filename}.json"
    filepath = Path.cwd() / folder / sanitize_filename(filename)
    with open(filepath, "w", encoding='utf8') as file:
        json.dump(books_info, file, ensure_ascii=False, indent=2)


def main():
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser(
        description="script can parse https://tululu.org/ site and download books with images."
    )
    parser.add_argument("-s", "--start_id", default=1, type=int, help="set up start book id")
    parser.add_argument("-e", "--end_id", default=10, type=int, help="set up end book id")

    args = parser.parse_args()
    start = args.start_id
    end = args.end_id

    base_dir = Path.cwd() / "books"
    books = []
    for book_id in range(start, end):
        while True:
            page_book_url = f'https://tululu.org/b{book_id}/'
            try:
                base_url = get_base_url(page_book_url)
                book = parse_book_page(get_book_html(page_book_url))
                logging.info(f"Получены данные со страницы книги {page_book_url}")

                book_name = book['name']
                download_txt(urljoin(base_url, book['download_url']), f"{book_id} {book_name}.txt", base_dir)
                download_image(urljoin(base_url, book['image_url']), f"{book_id} {book_name}", base_dir)
                books.append(book)
                break
            except requests.HTTPError:
                logging.info(f"Книга не обнаружена по адресу {page_book_url}")
                break
            except requests.ConnectionError:
                logging.warning(
                    f"Не удалось установить соединение с сервером по адресу {page_book_url}. " +
                    f"Повторная попытка через 10 сек")

                time.sleep(10)

    save_books(books)


if __name__ == '__main__':
    main()
