from pathlib import Path

import requests


def download_book(request_url, base_dir, filename):
    response = requests.get(request_url)
    response.raise_for_status()
    if not base_dir.exists():
        Path.mkdir(base_dir)
    file = Path.cwd() / base_dir / filename
    with open(file, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    url = "https://tululu.org/txt.php?id=32168"
    base_dir = Path.cwd() / "books"
    for id in range(10):
        download_book(url, base_dir, f"id{id}.txt")
