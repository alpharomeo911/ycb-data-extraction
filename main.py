import requests
from bs4 import BeautifulSoup
import argparse
import os
import sys
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import time
import glob
import urllib.request

def download(url):
    file_name = url.split('/')[-1]
    print(url)
    print('[+] Downloading: ', file_name)
    urllib.request.urlretrieve(url, file_name)
    print('[+] Finished Downloading: ', file_name)


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
    os.chdir('Downloads')
    for url_ in urls:
        download(url_)