import requests
from bs4 import BeautifulSoup
import argparse
import os
import sys
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import time
from glob import glob
import urllib.request
import numpy as np
import cv2

HEIGHT = 648
WIDTH = 648

def download(url):
    file_name = url.split('/')[-1]
    print(url)
    print('[+] Downloading: ', file_name)
    if not os.path.isfile(file_name):
        urllib.request.urlretrieve(url, file_name)
    print('[+] Finished Downloading: ', file_name)


def extract_file(file):
    print("[+] Extracting: " + file)
    os.system(f'tar -xf {file}')


def extract_threader(directory):
    files = glob(os.path.join(directory)+'/*.tgz')[4:]
    pool = ThreadPool(8)
    res = pool.map(extract_file, files)


def random_move():
    move_dir = os.getcwd() + '/Extracted_Images/'
    directories = next(os.walk('.'))[1]
    print(directories)
    for dir in directories:
        if dir=='Downloads' or dir=='Extracted_Images':
            continue
        os.chdir(dir)
        print(dir)
        images = glob(os.path.join(os.getcwd())+'/*.jpg')
        images = np.array(images)
        np.random.shuffle(images)
        images = images[:150]
        for image in images:
            print(image)
            os.system(f'mv {image} {move_dir}{dir}_{image.split("/")[-1]}')
        os.chdir('..')


def resize_image(image):
    img = cv2.imread(image)
    img = cv2.resize(img, (WIDTH, HEIGHT))
    cv2.imwrite(image, img)


def resize_image_mask(image):
    img = cv2.imread(image)
    img = cv2.resize(img, (WIDTH, HEIGHT))
    cv2.imwrite(f'{image.split(".")[0]}.jpg', img)


def resize_images_threader(dir):
    os.chdir(dir)
    ###
    directories = next(os.walk('.'))[1]
    for dir in directories:
        print("[+]Processing :", dir)
        if dir=='Downloads' or dir=='Extracted_Images' or dir == 'home':
            continue
        images = glob(os.path.join(os.getcwd())+'/'+dir+'/*.jpg')
        masks = glob(os.path.join(os.getcwd())+'/'+dir+'/masks/*.pbm')
        pool = ThreadPool(12)
        try:
            if cv2.imread(f'{masks[0].split(".")[0]}.jpg').shape[0] == WIDTH and cv2.imread(f'{masks[0].split(".")[0]}.jpg').shape[1] == HEIGHT:
                continue
        except Exception as e:
            print(e)
        res = pool.map(resize_image, images)
        res = pool.map(resize_image_mask, masks)
    ###

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='main', 
                                     description='Extracts YCB dataset from http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/',
                                     epilog='use --help for more options')
    
    parser.add_argument('-o', '--output_dir', required=True, help='(Required!) Output directory where you wish to extract and keep the images')
    parser.add_argument('-n', '--num_images', default=100, help='number of images you wish to keep')
    args = parser.parse_args()
    url = 'http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com'
    page = requests.get(url)
    os.makedirs(args.output_dir, exist_ok=True)
    os.chdir(args.output_dir)
    soup = BeautifulSoup(page.text)
    urls = []
    for row in soup.findAll('table')[0].tbody.findAll('tr'):
        try:
            urls.append(f'http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/{row.findAll("td")[2].contents[1]["href"]}')
        except Exception as e:
            pass
    os.makedirs('Downloads', exist_ok=True)
    os.makedirs('Extracted_Images', exist_ok=True)
    os.chdir('Downloads')
    for url_ in urls:
        download(url_)
    os.chdir('..')
    extract_threader(args.output_dir+'/Downloads')
    random_move()
    os.chdir(args.output_dir)
    resize_images_threader(args.output_dir)