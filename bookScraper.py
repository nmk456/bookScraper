import argparse
import logging
import math
import os
import re
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from libGen import Library

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.WARNING)


def check_isbn(isbn):
    """Return true if input is valid ISBN"""
    isbn = str(isbn)

    try:
        int(isbn)
    except ValueError:
        return False

    isbn = [int(char) for char in isbn]

    if len(isbn) == 10:
        s = 0
        t = 0
        for i in range(10):
            t += isbn[i]
            s += t
        return s % 11 == 0
    elif len(isbn) == 13:
        s = 0
        for i in range(13):
            if i % 2 == 0:
                s += isbn[i]
            else:
                s += isbn[i] * 3
        return s % 10 == 0
    else:
        return False


def get_books(isbn=None, title=None, author=None):
    lib = Library()
    if isbn:
        logging.debug(f"Searching for ISBN: {isbn}")
        ids = lib.search(isbn, mode="isbn")
    elif title:
        logging.debug(f"Searching for title: {author}")
        ids = lib.search(title, mode="title")
    elif author:
        logging.debug(f"Searching for author: {title}")
        ids = lib.search(author, mode="author")
    else:
        return []

    logging.debug(f"IDs Found: {ids}")

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
                             total=math.ceil(total_size // block_size),
                             unit='KB',
                             unit_scale=True,
                             unit_divisor=1024,
                             smoothing=0.1):
                wrote += len(data)
                f.write(data)
    else:
        logging.error("File already exists")

    if total_size != 0 and wrote != total_size:
        logging.error("Download error")
    else:
        logging.info(f"File downloaded successfully: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Downloads books based on ISBN")
    parser.add_argument("isbn", help="ISBN of book to download")
    args = parser.parse_args()

    if args.isbn.isdigit():
        try:
            book, *_ = get_books(isbn=args.isbn)
            download_books(book.__dict__['md5'])
        except requests.exceptions.HTTPError as e:
            if "500" in str(e.response):
                logging.error(f"Book not found for ISBN: {args.isbn}")
            else:
                logging.error(str(e.response))

    elif os.path.isfile(args.isbn):
        with open(args.isbn) as f:
            isbns = f.read()

        isbns = re.findall(r"[\w']+", isbns)
        isbns = [x for x in isbns if check_isbn(x)]

        logging.debug(f"ISBNs: {isbns}")

        for isbn in isbns:
            try:
                book, *_ = get_books(isbn=isbn)
                download_books(book.__dict__['md5'])
            except requests.exceptions.HTTPError as e:
                if "500" in str(e.response):
                    logging.error(f"Book not found for ISBN: {isbn}")
                else:
                    logging.error(str(e.response))

    else:
        logging.critical("Invalid input. Please input an ISBN or text file containing a list of ISBNs.")


def test():
    good_isbns = ["9781566199094", 9781566199094, "1566199093", 1566199093]
    bad_isbns = ["6937", "29323478523452983", "hello world!", 51, 582863, (5, 2), 4915834592]
    for value in good_isbns:
        assert check_isbn(value), "Valid ISBN was found invalid."
    for value in bad_isbns:
        assert not check_isbn(value), "Invalid ISBN was found valid."


if __name__ == "__main__":
    main()
    # test()
