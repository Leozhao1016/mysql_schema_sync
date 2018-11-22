from table_check import *

#传入游标，表，返回一个包含索引及列的字典
def getkey(cursor,db,tab):
    dict_key={}
    sql="SELECT index_name,GROUP_CONCAT(COLUMN_NAME order by SEQ_IN_INDEX) FROM  INFORMATION_SCHEMA.STATISTICS where table_schema='%s' and table_name='%s' group by index_name;"  %(db,tab)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for key in results:
            dict_key[key[0]]=key[1]
    except Exception as e:
        raise e
    return dict_key

#比较源表中有，而目标表中没有的索引，并返回索引名字；对这部分索引生成创建索引的sql
#传入源表，目标表中的{keyname,column}
def get_add_key(dicta,dictb):
    keyname=[]
    lista=list(dicta.values())
    listb=list(dictb.values())
    listadd=compact_add(lista,listb)
    for i in listadd:
        keyname.append(list(dicta.keys())[list(dicta.values()).index(i)])#根据value值返回key值，即索引名字
    return keyname

#对于源表中没有，目标表中有的索引，生成删除索引语句
def get_del_key(dicta,dictb):
    keyname=[]
    lista = list(dicta.values())
    listb = list(dictb.values())
    listdel = compact_del(lista, listb)
    for i in listdel:
        keyname.append(list(dictb.keys())[list(dictb.values()).index(i)])
    return keyname

#返回该索引的属性
def getkey_property(curosr,db,tab,keyname):
    property=0
    sql = "SELECT distinct non_unique FROM  INFORMATION_SCHEMA.STATISTICS where table_schema='%s' and table_name='%s' and index_name='%s';" % (db,tab,keyname)
    try:
        curosr.execute(sql) 	#执行sql语句
        for key in curosr.fetchall():	#获取查询的所有记录
            property=key[0]
    except Exception as e:
        raise e
    return  property

#生成创建索引的SQL,传入表名，索引属性，索引名字，索引列
def getkey_sql(tab,key_property,keyname,dict_key,mode):
    key_column=dict_key[keyname]
    if mode=='a':
        if (key_property==0 and keyname=='primay'): #主键
            sql = "alter table " + str(tab) + " add primary key " + str(key_column) +";"
        elif(key_property==0 and keyname!='primay'):#唯一索引
            sql = "alter table " + str(tab) + " add unique key " + str(keyname) + " ("+ key_column+")"+";"
        else: #普通索引
            sql = "alter table "+ str(tab) + " add  key " + str(keyname) + "("+ key_column+")"+";"
    else:#删除索引
        sql="alter table "+ str(tab) + " drop  key " + str(keyname) + " ;"
    return  sql
