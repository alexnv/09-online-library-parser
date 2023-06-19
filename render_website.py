import argparse
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.jinja2')


    with open("./books/books_info.json", "r", encoding="utf8") as books_file:
        books_json = books_file.read()

    books = json.loads(books_json)

    rendered_page = template.render(books=books)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def create_parser():
    parser = argparse.ArgumentParser(
        description="""Все представленные аргументы являются опциональными.
        По умолчанию будут скачаны все книги и картинки со всех доступных страниц
        в заранее определённые папки в корневом каталоге проекта."""
    )
    parser.add_argument(
        "-f",
        "--dest_folder",
        default="./books",
        help="""Введите путь к каталогу с результатами парсинга:
                картинкам, книгам, JSON."""
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
