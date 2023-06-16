# Парсер онлайн-библиотеки

Скрипт умеет парсить сайт онлайн [библиотеки](https://tululu.org/). Собирает информацию о книгах и может скачать книги и изображения к ним 
в формате txt.

Команда для установки зависимостей:
``` 
pip install -r requirements.txt
``` 
## Скрипт скачивания книг по их id

Запустите скрипт командой:
```
python main.py 
```
Скрипт скачает книги и изображения к ним, которые после можно будет найти в папке `books` 
соответственно, а также появится файл `books.json` с информацией о книгах. 

Скрипт имеет следующие аргументы для более "умного" парсинга:

- `-s (--start_id)` и `-e (--end_id)`: Они определяют начальный и конечный id книг для скачивания.

Пример запуска скрипта с аргументами:
```
python library_parser.py -s 700 -e 710 
```

Приведенная выше команда скачает книги начиная со страниц 700 по 710 в папку `books`

## Скрипт для скачивания категории книг

Находясь в директории проекта, откройте с помощью python3 файл `parse_tululu_category.py`

```
python parse_tululu_category.py
```
По умолчанию, в директории проекта будет создан файл `books_descriptions.json` с данными о книгах, а также папки `books` и `images`, в которые будут скачаны тексты книг и обложки из категории `Научная фантастика`.

Доступен ряд аргументов, и все они являются необязательными.

Для того, чтобы увидеть меню со справкой об аргументах, запустите скрипт с аргументом `-h` или `--help`:

```
python parse_tululu_category.py -h
```

```
python parse_tululu_category.py --help
```

В результате в консоль выведется следующее:

```
usage: parse_tululu_category.py [-h] [-g GENRE] [-s START_PAGE] [-e END_PAGE] [-f DEST_FOLDER] [-i] [-t] [-j JSON_PATH]

Все представленные аргументы являются опциональными. По умолчанию будут скачаны все книги и картинки со всех доступных страниц в заранее
определённые папки в корневом каталоге проекта.

options:
  -h, --help            show this help message and exit
  -g GENRE, --genre GENRE
                        Введите номер жанра. По умолчанию будет указан номер 55, что соответствует жанру "Научная фантастика".
  -s START_PAGE, --start_page START_PAGE
                        Введите номер начальной страницы. Если не вводить номер конечной страницы, будут скачаны все доступные страницы с
                        начальной включительно.
  -e END_PAGE, --end_page END_PAGE
                        Введите номер конечной страницы. Если не вводить номер начальной страницы, будут скачаны все доступные страницы с
                        первой по конечную включительно.
  -f DEST_FOLDER, --dest_folder DEST_FOLDER
                        Введите путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
  -i, --skip_imgs       По умолчанию картинки будут скачаны. Для отмены укажите при запуске аргумент без значения.
  -t, --skip_txt        По умолчанию тексты книг будут скачаны. Для отмены укажите при запуске аргумент без значения.
  -j JSON_PATH, --json_path JSON_PATH
                        Введите путь к *.json файлу с результатами.
```