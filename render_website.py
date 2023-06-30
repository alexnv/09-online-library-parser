import argparse
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from pathvalidate import sanitize_filename


def render_page(id, totalpages, books, template, dir):
    pages_nums = range(1, totalpages+1)
    rendered_page = template.render(
        books=books,
        current_page=id,
        total_pages=totalpages,
        pages_nums=pages_nums,
        prevous_page_link=f"../pages/index{id - 1}.html",
        next_page_link=f"../pages/index{id + 1}.html",
        pages_links=[{"href": f"../pages/index{num}.html", "id": num} for num in pages_nums],

    )
    filepath = Path.cwd() / dir / sanitize_filename(f"index{id}.html")
    with open(filepath, "w", encoding="utf8") as file:
        file.write(rendered_page)



def on_reload():
    arguments = create_parser().parse_args()
    json_path = arguments.json_path
    output_path = arguments.output_path
    books_per_page = arguments.books_per_page

    Path(output_path).mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.jinja2')

    with open(json_path, "r", encoding="utf8") as books_file:
        books = json.load(books_file)

    books_pages = [chunk for chunk in chunked(books, books_per_page)]
    totalpages = len(books_pages)
    for index, book_page in enumerate(books_pages, 1):
        books = [chunk for chunk in chunked(book_page, 2)]
        render_page(index, totalpages, books, template, output_path)


def main():
    arguments = create_parser().parse_args()
    book_folder = arguments.book_folder
    image_folder = arguments.image_folder

    on_reload()
    server = Server()
    server.watch('./*.jinja2', on_reload)
    server.watch(f"./{book_folder}/*.*", on_reload)
    server.watch(f"./{image_folder}/*.*", on_reload)
    server.serve(root=".")


def create_parser():
    parser = argparse.ArgumentParser(
        description="""Все представленные аргументы являются опциональными.
        По умолчанию будут скачаны все книги и картинки со всех доступных страниц
        в заранее определённые папки в корневом каталоге проекта."""
    )
    parser.add_argument(
        "-f",
        "--book_folder",
        default="./media/books",
        help="""Введите путь к каталогу с результатами парсинга:
                книгам, JSON."""
    )

    parser.add_argument(
        "-im",
        "--image_folder",
        default="./media/images",
        help="""Введите путь к каталогу с результатами парсинга (картинки)"""
    )

    parser.add_argument(
        "-j",
        "--json_path",
        default="./media/books_info.json",
        help="Введите путь к *.json файлу с результатами."
    )

    parser.add_argument(
        "-o",
        "--output_path",
        default="./pages",
        help="Введите путь к каталогу со сгенерированными страницами сайта"
    )
    parser.add_argument(
        "-p",
        "--books_per_page",
        default=10,
        help="Количество книг на странице"
    )

    return parser


if __name__ == "__main__":
    main()
