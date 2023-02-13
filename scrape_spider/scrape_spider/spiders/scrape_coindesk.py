import scrapy
import re
from scrapy.crawler import CrawlerProcess
from helper_coindesk import fetch_latest_url

class CoindeskSpider(scrapy.Spider):
    name = 'coindesk'
    categories = ['markets','business','policy']
    news_df = fetch_latest_url(categories)
    start_urls = news_df['url'].to_list()

    # start_urls = ['https://www.coindesk.com/markets/2023/02/10/first-mover-asia-kraken-crypto-staking-settlement-bedevils-markets-as-bitcoin-lingers-below-219k/']

    def parse(self, response):
        print(response.url)
        page = response.url.split('/')[-2]
        print(page)
        filename = f'coindesk-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        headline = response.css('div.at-headline').css('h1::text').get()
        sub_headline = response.css('div.at-subheadline').css('h2::text').get()
        imgs = response.xpath('//*[@id="fusion-app"]/div[2]/div[1]/main/article/div/div/header/div').css('source::attr(srcset)').get()

        print('---------------------- HEADLINE ----------------------')
        print(headline)
        print('-------------------- SUB-HEADLINE --------------------')
        print(sub_headline)
        print('-------------------- CONTENT --------------------')

        res = ''

        for paragraph in response.xpath('//*[@id="fusion-app"]/div[2]/div[1]/main/div[1]/div/section/div[2]/div[3]/div[2]'):
            prg = paragraph.css('div').get()
            between_tag = re.findall(r'>(.*?)<|<p>(.*?)<', prg)
            # print(between_tag)
            # print()

            for tp_text in between_tag:
                res += ''.join(list(tp_text))

        print(res)
        print('----------------------- IMG -----------------------')

        img = imgs.split(',')[0].split(' ')[0] if imgs != None else None
        print(img)


        yield {
            'url':response.url,
            'headline':headline,
            'sub-headline':sub_headline,
            'content':res,
            'image':img
            }

if __name__ == "__main__":
    process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(CoindeskSpider)
    process.start() # the script will block here until the crawling is finished
