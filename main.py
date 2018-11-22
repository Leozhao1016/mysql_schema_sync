# -*- coding: UTF-8 -*-
import sys
import os
import time
import operator

from cloumn_check import *
from key_check import *

#初始化不同的数据库
def init(src_ip,src_db,src_db_user,src_db_pass):
  dbsource = connect_db(src_ip,src_db,src_db_user,src_db_pass)
  cursorsource = dbsource.cursor()
  return cursorsource

#手动关闭数据库
def close_db(cursorsource):
  cursorsource.close()

#连接数据库
def connect_db(ip,db,db_user,db_pass):
  db = pymysql.connect(host=ip, db=db, user=db_user, passwd=db_pass,charset='utf8')
  return db

def sql_exexute(coursor,f):
    sql_list = f.read().split(';')[:-1]  # sql文件最后一行加上;
    sql_list = [x.replace('\n', ' ') if '\n' in x else x for x in sql_list]
    for sql_item in sql_list:
        sql = sql_item + ";"
        try:
            coursor.execute(sql)
        except Exception as e:
            raise e

if __name__ == '__main__':
    id = sys.argv[1]
    cur_path = os.path.abspath(os.curdir)
    cur_time= time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
    out_put=(cur_path + '/' + 'dbsync' + cur_time + '.sql')
    con=pymysql.connect(host='10.80.61.80',user='root',passwd='wjzs1qaz', db='archive')
    cursor=con.cursor()
    try:
        sql = "select  server_source, port_source, user_source, password_source, db_source," \
              "server_dest, port_dest, user_dest, password_dest, db_dest " \
              "from db_sync " \
              "where id = '%s' " % (id)
        cursor.execute(sql)  # 执行sql语句
        results = cursor.fetchall()
        for row in results:
            server_source = row[0]
            port_source = row[1]
            user_source = row[2]
            password_source = row[3]
            db_source = row[4]
            server_dest= row[5]
            port_dest = row[6]
            user_dest = row[7]
            password_dest = row[8]
            db_dest = row[9]
    except Exception as e:
        raise e
    finally:
        cursor.close()

    srccoursor=init(server_source,db_source,user_source,password_source)
    tagcoursor=init(server_dest,db_dest,user_dest,password_dest)
    source_table=get_table(srccoursor)
    dest_table=get_table(tagcoursor)
    add_table=compact_add(source_table,dest_table)
    same_table=compact_same(source_table,dest_table)
    del_table=compact_del(source_table,dest_table)

    with open(out_put,'w',encoding="utf-8") as f: # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
        for tab in add_table:
            sql=get_table_sql(srccoursor,tab)
            print(sql)
            f.write(sql+'\n')
    #需要比较表结构的表
        for tab in same_table:
            source_column=clumn_get(srccoursor,tab,db_source)
            dest_column=clumn_get(tagcoursor,tab,db_dest)
            add_column=compact_add(source_column,dest_column)
            same_column =compact_same (source_column, dest_column)
            del_column =compact_del (source_column, dest_column)
            source_dict = getkey(srccoursor, db_source, tab)
            target_dict = getkey(tagcoursor, db_dest, tab)
            add_key = get_add_key(source_dict, target_dict)
            del_key = get_del_key(source_dict, target_dict)

        #source中有，target中没有的列，需要添加
            if add_column:
                for column in add_column:
                    column_type=clumntype_get(srccoursor,tab,column)
                    sql=column_sql(tab,column,column_type,'a')
                    f.write(sql+'\n')
        #source,target中都有，需要对比，并修改
            for column in same_column:
                source_column_type=clumntype_get(srccoursor,tab,column)
                targte_column_type=clumntype_get(tagcoursor,tab,column)
            # 如果两个列表完全一致，则不需要修改
                if operator.eq(source_column_type,targte_column_type):
                    continue
                else:
                    sql=column_sql(tab,column,source_column_type,'c')
                    f.write(sql+'\n')
        # source中没有，target中有，需要删除
            if del_column:
                for column in del_column:
                    column_type = clumntype_get(tagcoursor, tab, column)
                    sql = column_sql(tab, column, column_type, 'd')
                    f.write(sql+'\n')
        #源表中又，目标表中没有的索引需要添加
            if add_key:
                for key in add_key:
                    key_property=getkey_property(srccoursor,db_source,tab,key)
                    sql=getkey_sql(tab,key_property,key,source_dict,'a')
                    f.write(sql+ '\n')
        # 源表中又，目标表中没有的索引需要删除
            if del_key:
                for key in del_key:
                    key_property = getkey_property(srccoursor, db_source, tab, key)
                    sql = getkey_sql(tab, key_property, key, target_dict,'d')
                    f.write(sql+ '\n')
    f.close()
    with open(out_put, 'r+',encoding="utf-8") as f:
        sql_exexute(tagcoursor,f)

    close_db(srccoursor)
    close_db(tagcoursor)

