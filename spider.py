import requests
from bs4 import BeautifulSoup
import math
from miscellaneous import *
from urllib.request import urlopen


class Spider:

    list_link = set()     # 用于记录爬取全部分类页面上代表各种类别的页面
    list_domain = 'list.jd.com'

    def __init__(self, project_name):
        self.boot()       # 建立链接，第一个爬虫的额外任务

    # 第一个爬虫的额外任务：创建项目文件夹，爬取全部分类页面
    @staticmethod
    def boot():
        url = ('https://www.jd.com/allSort.aspx')
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        source_code = requests.get(url, headers=header)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text)
        for i in soup.findAll('dd'):    # 一级类别
            for j in i.findAll('a'):    # 二级类别
                Spider.add_link_to_queue(j['href'])     # 保存到set中

    @staticmethod
    def crawl_class(thread_name, class_url):
        Spider.list_link.remove(class_url)
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        url = ('https:' + class_url)
        source_code = requests.get(url, headers=header)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text)
        c1 = soup.find('span', {'class': 'p-skip'})
        c2 = c1.find('b')
        c3 = c2.string              # 找到一个类别的最大页数
        max_page = int(c3)
        c5 = soup.find('h3')
        c6 = c5.find('b')
        class_name = c6.string          # 当前类别的名称
        try:
            print(thread_name + ' now crawling : ' + class_name)
        except:
            pass
        items_list = Spider.crawl_page(thread_name, class_url, max_page)
        result = {'name': class_name,
                  'item-list': items_list}
        upload_data(result)      # 上传数据到数据库

    # 主命令， 用于爬列表中的每一页
    @staticmethod
    def crawl_page(thread_name, class_url, max_page):
        page = 1  # 分页网站中代表页码的数字
        items_list = []
        while(page <= max_page):
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
            url = ('https:' + class_url + '&page=' + str(page) +
                   '&trans=1&JL=6_0_0#J_main')
            try:
                source_code = requests.get(url, headers=header)
            except:
                print(thread_name + ' can not connect to page ' + str(page))
                continue
            plain_text = source_code.text
            soup = BeautifulSoup(plain_text)
            for item in soup.findAll('li', {'class': 'gl-item'}):

                # 查找名字
                n1 = item.find('div', {'class': 'p-name'})
                n2 = n1.contents[1]
                n3 = n2.contents[1]
                item_name = n3.string          # name

                # 查找价格
                try:
                    skuid = int(item.div['data-sku'])  # 商品id
                except:
                    print(thread_name + ' can not get the ID of : ' + item_name)
                    continue
                item_price = None
                try:
                    url = ('https://p.3.cn/prices/get?type=1&area=1_72_4137&pdtk=YwqNdKy3uFcz74Ns5bPkiUemUPrM0QPVTonE6QUuq1bA%2BcdvMqAQsikUQNTSt0rv&pduid=817904038&pdpin=&pdbp=0&skuid=J_' +
                           str(skuid) + '&callback=cnp')                            # pdtk有可能会变
                    response = urlopen(url)
                    source_code = response.read()
                    text = str(source_code)
                    item_price = float(text.split('"')[7])          # 成功获取数据后的输出接口
                    print(thread_name + ' get the price of ' + item_name + ' : ' + str(item_price))
                except:
                    pass

                # 查找评论
                comments = []
                comment_url = ('https://sclub.jd.com/comment/productPageComments.action?productId=' + str(skuid) +
                                   '&score=0&sortType=3&page=0&pageSize=10')
                try:
                    source_code = requests.get(comment_url, headers=header)     # 获取记录评论的json文件
                except:
                    print(thread_name + ' can not get the comments of : ' + item_name)
                    continue
                text = source_code.json()
                product_comment_summary = text['productCommentSummary']
                comment_count = product_comment_summary['commentCount']     # 得到评论总量
                for i in range(math.ceil(comment_count/10)):
                    comment_url = ('https://sclub.jd.com/comment/productPageComments.action?productId=' + str(skuid) +
                                   '&score=0&sortType=3&page=' + str(i) +
                                    '&pageSize=10')
                    try:
                        source_code = requests.get(comment_url, headers=header)  # 获取记录评论的json文件
                    except:
                        print(thread_name + ' can not get the comment page ' + str(i) + ' of : ' + item_name)
                        continue
                    text = source_code.json()
                    comment_list = text['comments']
                    if(comment_list is not None):
                        for c in comment_list:
                            comments.append(c['content'])         # 评论输出接口
                this_item = {'item-id': skuid,
                             'item-name': item_name,
                             'item-price': item_price,
                             'comments': comments}
                items_list.append(this_item)
            print(thread_name + ' has ' + str(max_page-page) + 'pages left')
            page += 1
        return items_list

    @staticmethod
    def add_link_to_queue(link):   # 添加一个链接的集合
        if link in Spider.list_link:
            pass
        if Spider.list_domain not in link:      # 如果不是标准的list则不加入
            pass
        else:
            Spider.list_link.add(link)




