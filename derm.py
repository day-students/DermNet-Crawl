from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import os
import sys
from argparse import ArgumentParser
import re
import time
from pathlib import Path

def download_image(name, url, base):
    """Downloads the image found at url"""

    with urlopen(url) as page:
        soup = BeautifulSoup(page, features='html.parser')

    dis_img = soup.find('img', id='disImg')
    img_url = dis_img['src']

    with urlopen(img_url) as img:
        with open(base / name, 'wb') as img_file:
            img_file.write(img.read())
        
    print('.', end=' ')
    sys.stdout.flush()

def load_photo_r(url, base, page_num):
    # Load the photos from the current page

    print(f'Page {page_num}', end=' ')
    sys.stdout.flush()

    with urlopen(url) as page:
        soup = BeautifulSoup(page, features='html.parser')

    col_left = soup.find('div', class_='contents').find('div', class_='left').find('div', class_='col_left')

    # Read the images
    thumbs = col_left.find_all('div', class_='thumbnails')

    # Read each image link
    for thumb in thumbs:
        link = thumb.find('a')
        href = urljoin(url, link['href'])
        name = link.find('div', class_='desc').text
        download_image(name, href, base)
        
    print('Done')

    # Download the next photo
    next_a = col_left.find('div', class_='NrResults').find('a', text='Next')
    if (next_a):
        load_photo_r(urljoin(url, next_a['href']), base, page_num + 1)

def load_photos(name, url, base):
    print(f'Loading photos of disease {name}')

    base = base / name
    try:
        os.mkdir(base)
    except OSError:
        pass

    load_photo_r(url, base, 1)

# Open a single category

def load_type(url, base):
    with urlopen(url) as page:
        soup = BeautifulSoup(page, features='html.parser')

    left = soup.find('div', class_='contents').find('div', class_='left')
    
    name = left.find('h2').text
    print(f'Downloading photos of type {name}')
    base = base / name
    try:
        os.mkdir(base)
    except OSError:
        pass

    links = left.find('table').find_all('a')

    for link in links:
        if (link.text not in ('Tes Cate5', 'Test Cat 6')):
            load_photos(link.text, urljoin(url, link['href']), base)

parser = ArgumentParser(description='Downloads images from DermNet')
parser.add_argument('--all', action='store_true', help='Download all files')
parser.add_argument('--dis', nargs='+', help='Download certain diseases (regex)')

# Open the main page

start = time.time()

args = parser.parse_args()

with urlopen('http://www.dermnet.com/dermatology-pictures-skin-disease-pictures/') as home:
    soup = BeautifulSoup(home, features='html.parser')

try:
    os.mkdir('data')
except OSError:
    pass

if args.all:

    type_links = soup.find('div', class_='contents').find('table').find_all('a')

    try:
        os.mkdir('data/all')
    except OSError:
        pass

    for type_link in type_links:
        load_type(urljoin('http://www.dermnet.com/dermatology-pictures-skin-disease-pictures/', type_link['href']), Path('data/all'))
elif args.dis:

    try:
        os.mkdir('data/disease')
    except OSError:
        pass


    rees = [re.compile(r) for r in args.dis]

    ree_paths = [(Path('data/disease') / ''.join(c for c in r if c not in ('#%&{}\<>*?/ $!\'\":@'))) for r in args.dis]

    for ree_path in ree_paths:
        try:
            os.mkdir(ree_path)
        except OSError:
            pass


    disease_links = soup.find('div', class_='contents').find_all('table')[1].find_all('a')
    for disease_link in disease_links:
        for ree, ree_path in zip(rees, ree_paths):
            mat = ree.match(disease_link.text)
            if (mat):
                load_photos(disease_link.text, urljoin('http://www.dermnet.com/dermatology-pictures-skin-disease-pictures/', disease_link['href']), ree_path)
                break
else:
    parser.print_help()

end = time.time()
print(f'Finished in {end - start} seconds')