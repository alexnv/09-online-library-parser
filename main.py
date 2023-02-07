import urllib
from pathlib import Path
from urllib.request import Request

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

    with open(safe_filename, "wb") as file:
        file.write(response.content)
    return safe_filename.relative_to(Path.cwd())



def parse_book_page(book_id):
    page_book_url = f'https://tululu.org/b{book_id}/'
    response = requests.get(page_book_url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find(id='content').find('h1')
    title_text = title_tag.text
    name, author = title_text.split(" :: ")
    name_book = name.strip()
    author_book = author.strip()
    image_url = soup.find("div", class_="bookimage").find("a").find("img").attrs['src']

    return name_book, author_book, image_url


if __name__ == '__main__':
    base_dir = Path.cwd() / "books"
    for book_id in range(1,10):
        params = {"id": book_id}
        try:
            name, author, image = parse_book_page(book_id)
            url = "https://tululu.org/txt.php?" + urllib.parse.urlencode(params)
            download_txt(url, f"{book_id}. {name}.txt", base_dir)
        except requests.HTTPError:
            print("Такой книги нет")