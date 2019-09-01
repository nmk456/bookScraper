# Book Scraper

## Overview

This tool searches libgen (and soon other sites) to find an ebook matching the ISBN provided by the user.

## Requirements

* Python 3.7 (might work on earlier version, not tested)
* BeatifulSoup4
* TQDM
* Standalone binaries are provided for Windows (Linux soon maybe), they don't require anything

## Use

### Python Module

`python bookScraper.py 123456789`

### Binary Executable

`bookScraper.exe 123456789`

Replace 123456789 with the ISBN of the book you want to download. Downloads may be slow, but that appears to be limited by the server.
