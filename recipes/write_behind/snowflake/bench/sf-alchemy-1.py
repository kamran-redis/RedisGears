#!/usr/bin/env python

import time
import sys
import os
from timeit import default_timer as timer
from datetime import timedelta

import sqlalchemy
from sqlalchemy.sql import text

USER = os.getenv('SNOW_USER')
PWD = os.getenv('SNOW_PWD')
ACCT = os.getenv('SNOW_ACCT')
DB = os.getenv('SNOW_DB')

count = int(sys.argv[1]) if len(sys.argv) > 0 else 10
if count > 16384:
    count = 16384
    print("warning: maximum batch size is %s" % count)

connstr = 'snowflake://{user}:{password}@{account}'.format(user=USER, password=PWD, account=ACCT)
engine = sqlalchemy.create_engine(connstr).execution_options(autocommit=True)
cc = engine.connect()

try:
    cc.execute("DROP DATABASE {}".format(DB))
except:
    pass
cc.execute("CREATE DATABASE {}".format(DB))
cc.execute("USE DATABASE {}".format(DB))
cc.execute("CREATE TABLE person1 (id VARCHAR(100), first VARCHAR(100), last VARCHAR(100), age VARCHAR(100), PRIMARY KEY (id))");

first = 1
n = count
last = first + n

t0 = timer()

if True:
# if False:
    print("inserting...")
    sql1 = "INSERT INTO person1 (id,first,last,age) VALUES (%s, '{}', '{}', '{}')".format('john', 'doe', '42')
    data = []
    for i in range(first, last):
        data.append([i])
    t0 = timer()
    cc.execute(sql1, data)
    t1 = timer()
    t_insert = timedelta(seconds=(t1-t0)/n)
    print("insert: {} (per row)".format(t_insert))

    rows = cc.execute("select count(*) from person1").fetchone()[0]
    print("rows: {}".format(rows))

# if True:
if False:
    print("updating...")
    data = []
    sql2 = "UPDATE person1 SET first='{}',last='{}',age='{}' WHERE id=%s".format('john', 'doe', '43')
    for i in range(first, last):
        data.append([i])
    t1 = timer()
    cc.execute(sql2, data)
    t2 = timer()
    t_update = seconds((t2-t1)/n)
    print("update: {} (per row)".format(t_update))

# if True:
if False:
    print("upserting...")
    data = []
    sql3 = ("MERGE INTO person1 d USING (SELECT 1 FROM DUAL) ON (d.id = %s) " + \
        "WHEN NOT MATCHED THEN INSERT (id,first,last,age) VALUES (%s, '{first}', '{last}', '{age}') " + \
        "WHEN MATCHED THEN UPDATE SET first='{first}',last='{last}',age='{age}'").format(first='john', last='doe', age='42')
    for i in range(first, last):
        data.append([i, i])
    t2 = timer()
    cc.execute(sql3, data)
    t3 = timer()
    t_merge_update = seconds((t3-t2)/n)
    print("update (merge): {} (per row)".format(t_merge_update))

# if True:
if False:
    print("deleting (type 1)...")
    data = []
    sql4 = "DELETE FROM person1 WHERE id=%s"
    for i in range(first, last):
        data.append([i])
    t3 = timer()
    cc.execute(sql4, data)
    t4 = timer()
    t_delete = seconds((t4-t3)/n)
    print("delete: {} (per row)".format(t_delete))

if True:
# if False:
    print("deleting (type 2)...")
    sql4 = "DELETE FROM person1 WHERE id in ({})".format(",".join("{}".format(i) for i in range(first, last)))
    t3 = timer()
    cc.execute(sql4)
    t4 = timer()
    t_delete = seconds((t4-t3)/n)
    print("delete: {} (per row)".format(t_delete))

rows = cc.execute("select count(*) from person1").fetchone()[0]
print("rows: {}".format(rows))

cc.execute("DROP DATABASE {}".format(DB))

cc.close()
