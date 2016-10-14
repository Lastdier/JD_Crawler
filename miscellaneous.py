import os
import json
import pymysql


# save the website you crawled
def create_project_directory(directory):
    if not os.path.exists(directory):
        print('Creating directory' + directory)
        os.makedirs(directory)


# create a queue and crawled files
def create_datafiles(project_name):
    queue = project_name + '/data_file.json'
    if not os.path.isfile(queue):
        write_file(queue)


# create a new file
def write_file(path):
    f = open(path, 'w')
    f.close()


# add data to an exiting file
def append_to_file(path, data):
    with open(path, 'a') as f:      # a 意思是启用追加模式
        f.write(data + '\n')


# delete the content of a file
def delete_file_content(path):
    with open(path, 'w'):           # 用w模式打开，令文件成为空白文件
        pass


# read a file and convert it to set item
# set data structure can prevent crawling the same url twice
def file_to_set(file_name):
    result = set()
    with open(file_name, 'rt') as f:        # rt代表文本读模式
        for line in f:
            result.add(line.replace('\n', ''))
    return result


# convert a set to a file
def set_to_file(items, file):
    delete_file_content(file)
    for item in sorted(items):
        append_to_file(file, item)


def data_to_json_file(data, path):
    string = json.dumps(data, ensure_ascii=False, indent=2)
    print(string)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(string + '\n')


def upload_data(data):
    connect = pymysql.connect(host='localhost', port=3306, user='root', db='jd_data', charset='utf8')
    try:
        for item in data['item-list']:
            cur = connect.cursor()
            v1 = [item['item-id'], item['item-name'], item['item-price'], data['name']]
            cur.execute("INSERT INTO item_information (item_id, item_name, item_price, item_class) values (%s, %s, %s, %s)", v1)
            cur.close()
            count = 0
            for comment in item['comments']:
                cur = connect.cursor()
                v2 = [comment, count, item['item-id']]
                cur.execute("INSERT INTO comments (comment_content, count, item_id) values (%s, %s, %s)", v2)
                cur.close()
                count += 1
        connect.commit()
        print('Upload succeed!')
    except Exception as e:
        print('Upload failed!')
        print(e)
    finally:
        connect.close()


