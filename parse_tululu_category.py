import argparse
import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from library_parser import check_for_redirect, parse_book_page, request_from_url, download_txt, download_image


def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, "lxml")


def split_title_tag(soup):
    title_tag = soup.select_one("table.tabs h1")
    raw_title, raw_author = title_tag.text.split("::")
    title = raw_title.strip()
    author = raw_author.strip()
    return title, author


def get_relative_adresses_of_books(url, genre, start_page, end_page):
    urls = []
    for page in range(start_page, end_page):
        genre_url = f"{url}l{genre}/{page}/"
        try:
            soup = get_soup(genre_url)
        except requests.exceptions.HTTPError as error:
            print(error)
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            continue
        tables = soup.select("table.d_book")
        urls.extend([table.select_one("a")["href"] for table in tables])
    return urls


def save_as_json(books, dest_folder, json_path, filename="books_info"):
    folder = json_path if json_path else dest_folder
    Path(folder).mkdir(parents=True, exist_ok=True)
    path = Path(f"{folder}/{filename}.json")
    with open(path, "w", encoding="utf8") as file:
        json.dump(books, file, ensure_ascii=False)


def main():
    arguments = create_parser().parse_args()
    genre = arguments.genre
    start_page = arguments.start_page
    end_page = arguments.end_page
    dest_folder = arguments.dest_folder
    skip_imgs = arguments.skip_imgs
    skip_txt = arguments.skip_txt
    json_path = arguments.json_path

    url = "https://tululu.org/"
    relative_adresses_of_books = get_relative_adresses_of_books(
        url,
        genre,
        start_page,
        end_page
    )
    books = []
    for book_adress in relative_adresses_of_books:
        book_url = urljoin(url, book_adress)
        txt_url = f"{url}txt.php"
        book_id = book_adress.strip("/b")
        params = {
            "id": book_id
        }
        try:
            soup = get_soup(book_url)
            parsed_page = parse_book_page(request_from_url(book_url).text)
            if not skip_txt:
                txt_name = sanitize_filename(f"{parsed_page['author']}.txt")
                book_path = download_txt(txt_url, txt_name, dest_folder, params)
                parsed_page["book_path"] = book_path
            if not skip_imgs:
                pic_url = urljoin(book_url, parsed_page['image_url'])
                pic_name = parsed_page['image_name']
                pic_path = download_image(pic_url, pic_name, dest_folder)
                parsed_page["img_src"] = pic_path
                parsed_page.pop("image_url")
                parsed_page.pop("image_name")
            books.append(parsed_page)
        except requests.exceptions.HTTPError as error:
            print(error)
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            continue
    save_as_json(books, dest_folder, json_path)


def create_parser():
    parser = argparse.ArgumentParser(
        description="""Все представленные аргументы являются опциональными.
        По умолчанию будут скачаны все книги и картинки со всех доступных страниц
        в заранее определённые папки в корневом каталоге проекта."""
    )
    parser.add_argument(
        "-g",
        "--genre",
        default=55,
        type=int,
        help="""Введите номер жанра.
        По умолчанию будет указан номер 55, что соответствует жанру
        "Научная фантастика"."""
    )
    parser.add_argument(
        "-s",
        "--start_page",
        default=1,
        type=int,
        help="""Введите номер начальной страницы.
                Если не вводить номер конечной страницы,
                будут скачаны все доступные страницы
                с начальной включительно."""
    )
    parser.add_argument(
        "-e",
        "--end_page",
        default=5,
        type=int,
        help="""Введите номер конечной страницы.
                Если не вводить номер начальной страницы,
                будут скачаны все доступные страницы с первой по конечную
                (без включения конечной)."""
    )
    parser.add_argument(
        "-f",
        "--dest_folder",
        default="./books",
        help="""Введите путь к каталогу с результатами парсинга:
                картинкам, книгам, JSON."""
    )
    parser.add_argument(
        "-i",
        "--skip_imgs",
        action="store_true",
        help="""По умолчанию картинки будут скачаны.
                Для отмены укажите при запуске аргумент без значения."""
    )
    parser.add_argument(
        "-t",
        "--skip_txt",
        action="store_true",
        help="""По умолчанию тексты книг будут скачаны.
                Для отмены укажите при запуске аргумент без значения."""
    )
    parser.add_argument(
        "-j",
        "--json_path",
        default=None,
        help="Введите путь к *.json файлу с результатами."
    )

    return parser


if __name__ == "__main__":
    main()
