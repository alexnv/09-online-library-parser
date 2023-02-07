import logging
import urllib
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    path = Path.cwd() / folder
    path.mkdir(parents=True, exist_ok=True)
    if not Path(filename).suffix:
        filename = f"{filename}.txt"
    safe_filename = path / sanitize_filename(filename)
    logging.info(f"Скачиваем книгу по адресу {url} в файл {safe_filename}")

    with open(safe_filename, "wb") as file:
        file.write(response.content)
    return safe_filename.relative_to(Path.cwd())


def download_image(url, filename, folder='books/'):
    """Функция для скачивания графических файлов.
    Args:
        url (str): Cсылка на картинку, которую хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    path = Path.cwd() / folder
    path.mkdir(parents=True, exist_ok=True)
    if not Path(filename).suffix:
        filename = f"{filename}.jpg"

    safe_filename = path / sanitize_filename(filename)
    logging.info(f"Скачиваем обложку книги по адресу {url} в файл {safe_filename}")
    with open(safe_filename, "wb") as file:
        file.write(response.content)
    return safe_filename.relative_to(Path.cwd())


def parse_book_page(url):
    logging.info(f"Получаем данные со страницы книги {url}")
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find(id='content').find('h1')
    title_text = title_tag.text
    name, author = title_text.split(" :: ")
    name_book = name.strip()
    author_book = author.strip()
    image_url = soup.find("div", class_="bookimage").find("a").find("img").attrs['src']

    comments = set(comment_div.find("span", class_="black").text for comment_div in soup.findAll("div", class_="texts"))
    genres = set(genre_el.text for genre_el in soup.find("span", class_="d_book").findAll("a"))
    logging.info(f"Получены данные со страницы книги {url}")
    return {"name": name_book,
            "author": author_book,
            "comments": comments,
            "genres": genres,
            "image": image_url,
            }


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    base_dir = Path.cwd() / "books"
    for book_id in range(1, 10):
        params = {"id": book_id}
        try:
            page_book_url = f'https://tululu.org/b{book_id}/'
            book_info = parse_book_page(page_book_url)
            url = "https://tululu.org/txt.php?" + urllib.parse.urlencode(params)
            book_name = book_info['name']
            download_txt(url, f"{book_id}. {book_name}.txt", base_dir)
            url = urllib.parse.urljoin("https://tululu.org/", book_info['image'])
            download_txt(url, f"{book_id}. {book_name}.jpg", base_dir)
        except requests.HTTPError:
            logging.info(f"Книга не обнаружена по адресу {page_book_url}")
