from bs4 import BeautifulSoup
import requests
import lxml
import time
import os
import subprocess
import datetime

url = 'https://swallow.5ch.net/livejupiter/kako/kako0000.html'
filename = os.getcwd()+'/urllist.txt'
NGList = os.getcwd() + '/NGthread.txt'

def kakolog():
    List = []
    allThreads = requests.get(url)
    allThreads.encoding = allThreads.apparent_encoding
    threadsMenu = BeautifulSoup(allThreads.text, 'lxml')
    for t in threadsMenu.find_all(class_='menu_link'):
        a = t.find('a')
        links = a.get('href').lstrip('.')
        if 'html' in links:
            l = 'https://swallow.5ch.net/livejupiter/kako/' + links
        List.append(l)
    return List

def contains():
    threadURL = kakolog()
    start_point = 0
    container_num = len(threadURL)
    urls = 0
    ngtable = NGTable()
    f = open(filename, 'a+', encoding='utf-8')
    for t in threadURL:
        time.sleep(1)
        try:
            allResponse = requests.get(t)
            allResponse.encoding = allResponse.apparent_encoding
            soup = BeautifulSoup(allResponse.text, 'lxml')
            result = get_threads(soup, ngtable)
            urls += len(result)
            start_point += 1
            print('{:.1f}% ({}/{}) {}URLs'.format(
                (start_point/container_num) * 100, start_point, container_num, urls
                ))
            for r in result:
                f.write(
                    'https://swallow.5ch.net' + r + '\n'
                    )
            
        except Exception as e:
            print('Error: ', e.args)
            continue
    f.close()

def get_threads(soup, ngtable):
    l = []
    for odds in soup.find_all('p', class_='main_odd'):
        title = odds.find(class_='title').text
        if any(map(title.__contains__, ngtable)):
            continue
        if title.count('「') > 2 or title.count('y') > 3:
            continue
        if int(odds.find(class_='lines').text) > 30:
            odd = odds.find('a')
            odds_url = odd.get('href')
            l.append(odds_url)

    for evens in soup.find_all('p', class_='main_even'):
        tit = evens.find(class_='title').text
        if any(map(tit.__contains__, ngtable)):
            continue
        if tit.count('「') > 2 or tit.count('y') > 3:
            continue
        if int(evens.find(class_='lines').text) > 50:
            even = evens.find('a')
            evens_url = even.get('href')
            l.append(evens_url)
            
    return l

def NGTable():
    with open(NGList, 'r', encoding='utf-8') as f:
        l = [line.rstrip() for line in f]
    return l

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(start_time)
    if os.path.isfile(filename):
        os.remove(filename)
    contains()
    print(datetime.datetime.now()-start_time)
    print(
        subprocess.check_output(
            ['wc', '-l', filename]
        )
    )