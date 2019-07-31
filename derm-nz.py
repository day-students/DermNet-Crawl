from urllib.request import urlopen, Request
from urllib.parse import urljoin
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import os
import sys
from argparse import ArgumentParser
import re
import time
from pathlib import Path

def mkdir(path):
    try:
        os.mkdir(path)
    except OSError:
        pass

def open_url(path):
    req = Request(path, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'})
    try:
        res = urlopen(req)
        return res
    except HTTPError as e:
        print(f'{path} could not be opened')

def save_image(path, local_path):
    with open_url(path) as image_page:
        data = image_page.read()
    with open(local_path, 'wb') as file:
        file.write(data)
    print('.', end=' ')
    sys.stdout.flush()

def load_disease(path, local_base_path):
    start = time.time()

    with open_url(path) as page:
        soup = BeautifulSoup(page, features='html.parser')
    
    name = soup.find('div', class_='content__main').find('h1').text

    print(f'Loading Disease {name}', end=' ')
    sys.stdout.flush()

    local_path = local_base_path / name

    mkdir(local_path)

    image_link_blocks = soup.find_all('section', class_='imageLinkBlock')

    for image_link_block in image_link_blocks:
        fit_path = urljoin(path, image_link_block.find('img')['src'])
        tokens = fit_path.split('/')

        file_path = local_path / tokens[-1]
        
        if (tokens[-2].startswith('Fit')):
            identifier = tokens[-2][len('Fit') + 1:]
            tokens[-2] = f'CroppedFocusedImage{identifier}'

        water_path = '/'.join(tokens)
        save_image(water_path, file_path)
    
    end = time.time()

    print(f'Done ({end - start} seconds)')


parser = ArgumentParser(description='Downloads images from DermNet New Zealand')
parser.add_argument('--all', action='store_true', help='Download all files')
parser.add_argument('--dis', nargs='+', help='Download certain diseases (regex)')

# Open the main page

start = time.time()
args = parser.parse_args()

base_path = 'https://www.dermnetnz.org/topics/'

with open_url(base_path) as main_page:
    soup = BeautifulSoup(main_page, features='html.parser')

#mkdir('nz')

mkdir('nz')

if args.all:
    local_path = Path('nz/all')

    mkdir(local_path)

    links = soup.find_all('a', class_='topicsList__group__items__item', string=re.compile('.* images'))

    for link in links:
        url = urljoin(base_path, link['href'])
        load_disease(url, local_path)

elif args.dis:

    local_path = Path('nz/disease')
    mkdir(local_path)

    rees = [re.compile(f'({r}).*( images)') for r in args.dis]

    ree_paths = [(Path('nz/disease') / ''.join(c for c in r if c not in ('#%&{}\<>*?/ $!\'\":@'))) for r in args.dis]

    for ree_path in ree_paths:
        mkdir(ree_path)

    for ree, ree_path in zip(rees, ree_paths):
        links = soup.find_all('a', string=ree)
        for link in links:
            load_disease(urljoin(base_path, link['href']), ree_path)
            break
else:
    parser.print_help()

end = time.time()
print(f'Finished in {end - start} seconds')