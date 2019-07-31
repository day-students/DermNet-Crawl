# DermNet-Crawl
Fetches images from DermNet and DermNet New Zealand

## Requirements

 - [Python 3](https://www.python.org/)
 - [BeautifulSoup (bs4)](https://www.crummy.com/software/BeautifulSoup/)

## Usage

Both derm.py and derm-nz.py can be used in the same way.

`derm.py [-h] [--all] [--dis DIS [DIS ...]]`
 - `--help` - prints the help message
 - `--all` - downloads all categories
 - `--dis DIS [DIS ...]` - downloads diseases matching the regular expressions given
