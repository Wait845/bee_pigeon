"""
入口脚本
"""
import asyncio
import threading
from datetime import datetime
from asyncio.coroutines import iscoroutinefunction
from croniter import croniter
from logger import logger
import tasks
from utils import a_process_task, process_task


async def main():
    """异步函数入口
    """
    sync_task_list = []
    async_task_list = []

    for task_index, task in enumerate(tasks.task_list):
        # 判断schedule是否符合
        schedule = task.get("schedule", None)
        if not (schedule and croniter.is_valid(schedule)):
            logger.warning("schedule不存在或非法,index_%s", task_index)
            continue
        if not croniter.match(schedule, datetime.now()):
            continue

        # 判断func属于异步函数还是同步函数,并分配到不同列表
        func = task.get("function", None)
        if iscoroutinefunction(func):
            async_task_list.append(task)
        elif callable(func):
            sync_task_list.append(task)
        else:
            logger.warning("function不存在或非法,index_%s", task_index)

    logger.debug("准备执行同步任务数: %s", len(sync_task_list))
    sync_task_thread_list = []
    for sync_task in sync_task_list:
        sync_task_thread = threading.Thread(
                            target=process_task,
                            args=(sync_task,))
        sync_task_thread_list.append(sync_task_thread)
        sync_task_thread.start()

    logger.debug("准备执行异步任务数: %s", len(async_task_list))
    await asyncio.gather(*[
        a_process_task(async_task)
        for async_task in async_task_list
    ])

    # 阻塞同步函数
    for sync_task_thread in sync_task_thread_list:
        sync_task_thread.join()


if __name__ == "__main__":
    asyncio.run(main())
