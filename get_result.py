"""
获取最后要提交的表格
"""

import csv,json
import datetime
import sys, getopt

if __name__ == "__main__":
    # try:
    #     opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    # except getopt.GetoptError:
    #     print('test.py -i <inputfile> -o <outputfile>'()
    #     sys.exit(2)
    input_file = r"tests/snapshot.json"
    output_file1 = "result.csv"
    db_path = r"tests/db.sqlite3"
    output_file2 = "bills.csv"
    import json
    data = json.load(open(input_file,"r",encoding="utf-8"))
    data = [{
        "时间": d["time"],
        "命令": d["description"],
        "快充1":",".join(d["station_area"]["FC1"]),
        "快充2":",".join(d["station_area"]["FC2"]),
        "慢充1":",".join(d["station_area"]["SC1"]),
        "慢充2": ",".join(d["station_area"]["SC2"]),
        "慢充3": ",".join(d["station_area"]["SC3"]),
        "等待区": ",".join(d["waiting_area"]),
    }
    for d in data
    ]
    with open(output_file1, mode="w", encoding="utf-8-sig", newline="") as f:
        # 基于打开的文件，创建 csv.DictWriter 实例，将 header 列表作为参数传入。
        writer = csv.DictWriter(f, list(data[0].keys()))
        # 写入 header
        writer.writeheader()
        # 写入数据
        writer.writerows(data)
    import sqlite3
    import pandas as pd
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("select * from billmodel", conn)
    df['start_time'] = df['start_time'].apply(lambda x:datetime.datetime.strptime(x.split(".")[0],"%Y-%m-%d %H:%M:%S"))
    df['time'] = df['time'].apply(lambda x: datetime.datetime.strptime(x.split(".")[0],'%Y-%m-%d %H:%M:%S'))
    df['end_time'] = df['end_time'].apply(lambda x: datetime.datetime.strptime(x.split(".")[0],'%Y-%m-%d %H:%M:%S'))
    df.to_csv(output_file2, index=False,date_format='%H:%M:%S')