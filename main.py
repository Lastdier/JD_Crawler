import threading
from queue import Queue
from spider import Spider

PROJECT_NAME = 'JD'
NUMBER_OF_THREAD = 16                          # 线程数
queue = Queue()

Spider(PROJECT_NAME)


def create_worker():
    for _ in range(NUMBER_OF_THREAD):
        w = threading.Thread(target=work)       # work函数指定每个线程的工作
        w.daemon = True
        w.start()


def work():
    while True:
        url = queue.get()
        try:
            Spider.crawl_class(threading.current_thread().name, url)
        except:
            print(threading.current_thread().name + 'work failed!')
        finally:
            queue.task_done()


create_worker()
for link in Spider.list_link:
    queue.put(link)
queue.join()
