# mysql_schema_sync
1.工作中经常有需要同步不同数据库之间表结构的需求，如PROD--->UAT;PROD---->FAT;为了实现这一需求，写了一个小程序来实现。



2.功能说明：同步两个源之间（source数据库，target数据库）的表结构，包括表的差异，字段差异（命名、长度、新旧字段），索引差异（命名、是否唯一、复合索引）
；程序通过比较source,和target之间的差异，在当前路径下生成一个差异文件，并到target数据库执行相关SQL;使target库的表结构跟source完全一致。



3.使用说明：由于数据库的用户名，密码等信息属于重要敏感信息，所以将这些数据存储在数据库中，并用python去读取。
需要在除了source,target之外另一个数据库中创建如下表。注意：source端数据库建议配置从库。


CREATE TABLE `db_sync` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '表id',
  `server_source` varchar(640) NOT NULL COMMENT '源服务器',
  `port_source` varchar(64) NOT NULL COMMENT '源服务器端口',
  `user_source` varchar(64) NOT NULL COMMENT '源数据库用户',
  `password_source` varchar(128) NOT NULL COMMENT '源数据库密码',
  `db_source` varchar(64) NOT NULL COMMENT '源数据库schema',
  `server_dest` varchar(640) NOT NULL COMMENT '目标服务器',
  `port_dest` varchar(64) NOT NULL COMMENT '目标服务器端口',
  `user_dest` varchar(64) NOT NULL COMMENT '目标数据库用户',
  `password_dest` varchar(128) NOT NULL COMMENT '目标数据库密码',
  `db_dest` varchar(64) NOT NULL COMMENT '目标数据库schema',
  `created_dt` timestamp NULL NOT CURRENT_TIMESTAMP COMMENT '数据行创建时间',
  `comment` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='数据库表结构同步表';



在main函数中修改连接该数据库信息
con=pymysql.connect(host='***',user='***',passwd='***', db='***')



4.程序使用Pytho3编写，使用时可以结合Linux定时任务实现定时同步表结构：
python3 main.py 3


