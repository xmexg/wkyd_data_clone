# -*- coding: utf-8 -*-

import multiprocessing as mp
from multiprocessing import Process

import downsqldata

downsqldata.create_table()  # 创建数据库表
db = downsqldata.open_mysql()  # 打开数据库连接
start_id = None  # 起始id,默认为None,则从数据库中获取最大id
err_save_code_times = 0  # 连续的保存失败次数
all_times = 0  # 总次数
all_err_times = 0  # 总错误次数
max_process = 100  # 最大进程数
processes = []  # 进程列表

start_id = start_id or downsqldata.up_start_id(db)  # 当未设置有效初始值时,从数据库中获取最大id


def mul_request_sqlData(start_id, index, res_shared_data):
    res = downsqldata.request_sqlData(start_id)  # 获取数据
    res_shared_data[index] = res  # 将数据放入共享数据结构


'''
克隆学校运动数据入口
'''


def start_down():
    global start_id, err_save_code_times, all_times, all_err_times, max_process, processes
    while True:
        print(
            " ! 开始获取id: " + str(start_id) + " - " + str(start_id + max_process - 1) + " 的数据" + " 总次数: " + str(
                all_times) + " 总错误次数: " + str(all_err_times), end="\r")
        manager = mp.Manager()
        processes = []  # 进程列表
        res_shared_data = manager.list([None] * max_process)  # 响应包共享的数据结构

        for i in range(max_process):
            p = Process(target=mul_request_sqlData, args=(start_id + i, i, res_shared_data))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        for ele in res_shared_data:
            save_code = downsqldata.save_to_mysql(ele, db)  # 保存数据
            if save_code != 0:
                print(
                    " ! 发生错误, 错误code: " + str(save_code) + " 错误id: " + str(start_id) + " 错误信息: " + str(ele))
                err_save_code_times += 1
                all_err_times += 1
            else:
                err_save_code_times = 0
            if err_save_code_times >= 10:
                print(" - 连续10次保存失败,退出")
                exit(0)
            all_times += 1
            start_id += 1  # id自增
