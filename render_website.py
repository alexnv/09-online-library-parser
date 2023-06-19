import argparse
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked
from pathvalidate import sanitize_filename


def livereload_server(rootdir):
    server = Server()
    server.watch('./*.jinja', shell('render_website.py', cwd='.'))
    server.serve(root=".")


def render_page(id, books, template, dir):
    rendered_page = template.render(books=books)
    filepath = Path.cwd() / dir / sanitize_filename(f"index{id + 1}.html")
    with open(filepath, "w", encoding="utf8") as file:
        file.write(rendered_page)


def main():
    arguments = create_parser().parse_args()
    book_folder = arguments.book_folder
    json_path = arguments.json_path
    output_path = arguments.output_path

    Path(output_path).mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.jinja2')

    with open(json_path, "r", encoding="utf8") as books_file:
        books_json = books_file.read()

    books = json.loads(books_json)
    books_pages = [chunk for chunk in chunked(books, 10)]
    for index, book_page in enumerate(books_pages):
        books = [chunk for chunk in chunked(book_page, 2)]
        render_page(index, books, template, output_path)

    livereload_server(output_path)


def create_parser():
    parser = argparse.ArgumentParser(
        description="""Все представленные аргументы являются опциональными.
        По умолчанию будут скачаны все книги и картинки со всех доступных страниц
        в заранее определённые папки в корневом каталоге проекта."""
    )
    parser.add_argument(
        "-f",
        "--book_folder",
        default="./books",
        help="""Введите путь к каталогу с результатами парсинга:
                картинкам, книгам, JSON."""
    )
    parser.add_argument(
        "-j",
        "--json_path",
        default="./books/books_info.json",
        help="Введите путь к *.json файлу с результатами."
    )

    parser.add_argument(
        "-o",
        "--output_path",
        default="./dist",
        help="Введите путь к каталогу со сгенерированными страницами сайта"
    )

    return parser


if __name__ == "__main__":
    main()
