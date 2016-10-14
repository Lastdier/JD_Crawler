import pymysql


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
