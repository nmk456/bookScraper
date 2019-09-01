from libGen import Library
from bs4 import BeautifulSoup
from urllib.parse import unquote
from tqdm import tqdm
import os
import requests
import math
import argparse

parser = argparse.ArgumentParser(description="Downloads books based on ISBN")
parser.add_argument("isbn", help="ISBN of book to download")
args = parser.parse_args()


def get_books(isbn=None, title=None, author=None):
    lib = Library()
    if isbn:
        ids = lib.search(isbn, mode="isbn")
    elif title:
        ids = lib.search(title, mode="title")
    elif author:
        ids = lib.search(author, mode="author")
    else:
        return []

    return lib.lookup(ids)


def download_books(md5, mirror='http://93.174.95.29/_ads/'):
    url = mirror + md5
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    link = "http://93.174.95.29" + soup.find('a', href=True, text='GET')['href']
    filename = unquote(link.split("/")[-1])

    r = requests.get(link, stream=True)

    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024
    wrote = 0

    if not os.path.exists(os.path.join(os.getcwd(), filename)):
        with open(filename, 'wb') as f:
            for data in tqdm(r.iter_content(block_size),
                             total=math.ceil(total_size//block_size),
                             unit='KB',
                             unit_scale=True,
                             unit_divisor=1024,
                             smoothing=0.1):
                wrote += len(data)
                f.write(data)
    else:
        print("File already exists")

    if total_size != 0 and wrote != total_size:
        print("Download error")


def main():
    if os.path.exists(args.isbn):
        pass  # TODO: Allow text file with list of ISBNs
    else:
        book, *_ = get_books(isbn=args.isbn)
        download_books(book.__dict__['md5'])


if __name__ == "__main__":
    main()
