"""
工具包
"""
import asyncio
import threading
from collections.abc import Iterable
from asyncio.coroutines import iscoroutine
from logger import logger
from plugins import api


async def a_process_callback(task_result_list: list) -> None:
    """处理func产生的回调函数

    :param task_result_list: 多个任务的回调函数列表
    """
    # 展平回调任务
    callback_task_list = []
    for task_result in task_result_list:
        if iscoroutine(task_result):
            callback_task_list.append(task_result)
        elif isinstance(task_result, Iterable):
            for callback_task in task_result:
                if iscoroutine(callback_task):
                    callback_task_list.append(callback_task)

    # 调用回调任务
    logger.debug("加载了%s个回调任务", len(callback_task_list))
    await asyncio.gather(*callback_task_list)


def process_task(task_dict: dict) -> None:
    """处理同步task

    :param task_dict: 单个任务字典信息
    """
    uid_list = task_dict.get("uid", [])
    func = task_dict.get("function")
    args = task_dict.get("args", ())
    kwargs = task_dict.get("kwargs", {})

    # 保存多个uid的任务
    task_threading_list = []

    # 遍历多个uid
    for uid in uid_list:
        # 将uid增加到参数中，传递给func
        temp_args = [uid]
        temp_args.extend(args)
        temp_args = tuple(temp_args)

        new_task = threading.Thread(target=func, args=args, kwargs=kwargs)
        task_threading_list.append(new_task)
        new_task.start()

    # 保存func返回的回调函数
    task_result_list = []
    for task in task_threading_list:
        task.join()
        task_result_list.append(task.get_result())

    # 处理回调函数
    asyncio.run(a_process_callback(task_result_list))


async def a_process_task(task_dict: dict) -> None:
    """处理异步task

    :param task_dict: 单个任务字典信息
    """
    uid_list = task_dict.get("uid", [])
    func = task_dict.get("function")
    args = task_dict.get("args", ())
    kwargs = task_dict.get("kwargs", {})

    # 保存多个uid的任务
    task_coroutine_list = []

    # 直接调用系统api的任务
    if func in api.available_apis:
        new_coroutine = func(*args, **kwargs)
        task_coroutine_list.append(new_coroutine)

    # 遍历多个uid
    for uid in uid_list:
        # 将uid增加到参数中，传递给func
        temp_args = [uid]
        temp_args.extend(args)
        temp_args = tuple(temp_args)

        new_coroutine = func(*temp_args, **kwargs)
        task_coroutine_list.append(new_coroutine)

    # 执行func
    task_result_list = await asyncio.gather(*task_coroutine_list)

    # 处理回调函数
    await a_process_callback(task_result_list)
