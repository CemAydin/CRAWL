#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

import requests
import codecs
import csv

import sys

SLEEP_TIME = 1

if sys.version_info[0] >= 3:
    unicode = str
import os
import sqlite3

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


con = sqlite3.connect('/path/to/file/db.sqlite3')
from htmlmin.minify import html_minify
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


# proxies = {'http': 'http://89.105.202.101:3128/'}

def simple_get(url):
    """
    GET isteği yaparak url almaya çalışır.
    Yanıt HTML veya XML ise, içeriğini döndürür.
    Aksi halde None döner.
    """
    try:
        # with closing(requests.get(url, stream=True, proxies=proxies)) as resp:
        with closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('{0} için yapılan istekte hata döndü: {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    # Yanıt HTML ise True, aksi takdirde False döndürür.

    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    # Hataları kaydeder.

    print(e)


domain = 'https://www.sikayetvar.com'
brand_names = ['garanti-bbva']
scraped_data = []
def writeFile(filename, open_type="a", data=scraped_data):
    with open(filename + ".csv", open_type, newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"')

        for row in data:
            writer.writerow(row)
        data.clear()
        csvfile.close()

for brand in brand_names:

    brand_url = domain + '/' + brand

    brand_source = simple_get(brand_url)
    brand_soup = BeautifulSoup(html_minify(brand_source), 'html.parser')

    pagination = brand_soup.find('nav', {'class': 'pagination-wrap'})

    sikayet_no = 0

    """
    Markaya ait sayfa sayısının tespiti:
    İlk sayfanın değeri 0'dır.
    Eğer pagination değeri varsa +1 eklenir.
    """

    if pagination != None:

        num_of_pages = pagination.find_all('a')
        page_numbs = []

        for page_no in num_of_pages:
            page_numbs.append(page_no.text)

        last_page_no = int(page_numbs[-2]) + 1

    else:
        last_page_no = 2
    headers = ['ID', 'Marka', 'Başlık', 'Açıklama', 'Tarih', 'Görüntüleme Sayısı', 'Etiketler']
    writeFile(filename=brand, data=headers, open_type="w")

    """
    Şikayetleri toplamak için
    Sayfalara gidilir
    pagination değeri yoksa sayfa sayısına 2 atanır
    """


    for x in range(1, last_page_no):
        page_num = x
        time.sleep(SLEEP_TIME)
        print("I'm sleeping " + str(SLEEP_TIME))
        log = '\n ' + brand + ' için ' + str(page_num) + '. sayfa okunuyor...\n'
        print(log)

        page_numbered_url = brand_url + '?page=' + str(page_num)
        page_source = simple_get(page_numbered_url)
        page_soup = BeautifulSoup(html_minify(page_source), 'html.parser')

        item_pages = []

        """
        Her sayfa ziyaret edilir
        Sayfalar diziye alınır
        """

        find_all_card_url = page_soup.find_all('p', {'class': 'card-text'})
        for complaint in find_all_card_url:
           """ contents_ = complaint.contents
            href_ = contents_[1]
            item_pages.append(href_)"""
           for a in complaint.find_all('a', href=True):

                item_pages.append( a['href'])

        for page in item_pages:

            sikayet_no = sikayet_no + 1

            """time.sleep(2.4)

            Diziden sayfalar çağırılır
            Şikayetler tek tek ziyaret edilir
            Şikayet sayfası pars edilir
            """

            sikayet_url = domain + page
            print('Okunan sayfa: ' + sikayet_url + '...')
            sikayet_source = simple_get(sikayet_url)
            sikayet_soup = BeautifulSoup(html_minify(sikayet_source), 'html.parser')

            """
            İndirilen kaynaktan
            İstenen veriler değişkenlere atanır
            """

            title = sikayet_soup.find('title')
            if title != None:
                title = title.text.strip('\n')
                title = title.replace(' - Şikayetvar', '')

            description = sikayet_soup.find('div', {'class': 'card-text'})
            if description != None:
                description = description.text.strip('\n')

            date = sikayet_soup.find('span', {'class': 'info-icn time-tooltip'})
            if date != None:
                date = date['title']

            views = sikayet_soup.find('span', {'class': 'js-view-count'})
            if views != None:
                find = views.find('span', {'class': 'count'})
                views = find.text

            try:
                hashtags = sikayet_soup.find_all('div', {'class': 'detailComp-tags clearfix'})
                tags = []
                for a in hashtags[0].find_all('a', href=True):
                    tags.append(a['title'])
            except:
                print("An exception occurred")




            row = [sikayet_no, brand, title, description, date, views,tags,sikayet_url]
            scraped_data.append(row)

        writeFile(filename=brand,data=scraped_data)

print('Tüm işlemler bitti!')