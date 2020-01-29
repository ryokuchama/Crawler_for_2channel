from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import os
import re
import emoji
import time
import datetime

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class Crawler:
    def __init__(
        self, f, l, driver, min_words, max_words, max_backlinks
        ):
        self.f = f
        self.l = l
        self.driver = driver
        self.min_words = min_words
        self.max_words = max_words
        self.max_backlinks = max_backlinks

    def main(self):
        # open thread url list
        # URLのリストを開く
        with open(urllist, 'r') as ff:
            urls = ff.readlines()
        start_num = 0
        start_time = datetime.datetime.now()
        
        for u in urls:
            ur = u.rstrip('\n')
            try:
                self.driver.get(ur)
                # wait for read all html
                # ページ上のすべての要素が読み込まれるまで待機（15秒でタイムアウト判定）
                WebDriverWait(self.driver, 60).until(EC.presence_of_all_elements_located)
            except Exception as ee:
                print('Error: ', ee.args)
                time.sleep(15)
                continue

            html = self.driver.page_source.encode('utf-8')
            soup = BeautifulSoup(html, "html.parser")

            # pick up comment
            # レス抽出
            dom = soup.select('.post')
            f = open(savefile, 'a+', encoding='utf-8')
            for m in dom:
                if m.find(class_='back-links') and len(m.find_all(class_='back-links')) < self.max_backlinks:
                    escaped = m.find(class_='escaped')
                    sentence = escaped.text.strip()
                    if len(sentence) > self.max_words:
                        continue
                    elif 'ID:' in sentence or '正解' in sentence:
                        continue
                    elif '＿' in sentence or '￣' in sentence:
                        continue
                    elif 'http' in sentence or 'https' in sentence:
                        continue
                    elif sentence.count('>>') > 1:
                        continue
                    else:
                        ques = self.trim(sentence)
                    tooltip = m.find('a').text.strip('>')
                    ans = self.answer(tooltip)

                    if len(ques) > self.min_words and len(ans) > self.min_words:
                        print('a: '+ ques)
                        print('b: '+ ans)

                        self.f.write(
                            ques + '\t' + ans + '\n'
                            )
                        start_num += 1
                        
                        if start_num % 1000 == 0:
                            now = datetime.datetime.now()
                            self.l.write(
                                '{}lines ({})'.format(
                                    start_num, (now - start_time)
                                    ))
        self.l.close()
        self.f.close()
        self.driver.quit()
                    
    def answer(self, tooltip):
        try:
            sentence = self.driver.find_element(
                By.XPATH, "//*[@id='"+tooltip+"']/div[2]/span"
                ).text.strip()
            if len(sentence) > self.max_words:
                result = ''
            elif 'ID:' in sentence or '正解' in sentence:
                result = ''
            elif '＿' in sentence or '￣' in sentence:
                result = ''
            elif 'http' in sentence or 'https' in sentence:
                result = ''
            elif sentence.count('>>') > 1:
                result = ''
            else:
                result = self.trim(sentence)
        except Exception:
            result = ''

        return result

    def trim(self, sentence):
        text = sentence.strip()
        text = text.replace('  ', ' ')
        text = text.replace('\n', '')
        text = re.sub(r">>([0-9 \n]{1,6})", '', text)
        text = re.sub('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％�]', '', text)
        text = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)
        
        return text

savefile = os.getcwd()+'/corpus.txt'
urllist = os.getcwd()+'/urllist.txt'
logfile = os.getcwd() + '/log.txt'

# delete file if already exists. 既にコーパスファイルが存在している場合は削除
if os.path.isfile(savefile):
    os.remove(savefile)

# set up selenium
# seleniumのセットアップ
options = Options()
options.add_argument('--headless')
options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36')

driver = webdriver.Chrome(options=options)

f = open(savefile, 'a+', encoding='utf-8')
l = open(savefile, 'a+', encoding='utf-8')

min_words = 2
max_words = 50
max_backlinks = 6

crawl = Crawler(
    f, l, driver, min_words, max_words, max_backlinks
    )
crawl.main()