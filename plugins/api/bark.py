"""
调用bark发送通知
"""
import json
import asyncio
import urllib.parse
from typing import Iterable, Union
import httpx
from logger import logger
from .conf import BARK_URL


async def _request(url: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp


async def notify_bark(
        uuid: Union[str, Iterable],
        content: str,
        title: str = None,
        sound: str = None,
        is_archive: bool = None,
        icon: str = None,
        group: str = None,
        level: str = None,
        target_url: str = None,
        copy: str = None,
        badge: int = None,
        auto_copy: bool = None) -> int:
    """发送通知到设备

    :param uuid: 设备id
    :param content: 通知内容
    :param title: 通知标题
    :param sound: 为推送设置不同铃声
    :param is_archive: 自动保存通知消息，默认为保存
    :param icon: 自定义推送图标URL
    :param group: 消息分组名
    :param level: 通知级别，可选(“active”, "timeSensitive", "passive")
    :param target_url: 点击推送跳转到的URL
    :param copy: 复制的内容
    :param badge: 角标数字
    :param auto_copy: 自动复制内容到剪切板，携带copy参数时优先复制copy参数内容

    :return: 成功推送消息数量
    """
    # 判断uuid和content是否为空
    if not (uuid and content):
        return False

    # 调整uuid格式
    if isinstance(uuid, str):
        uuid = [uuid]
    if not isinstance(uuid, Iterable):
        return False

    # 构建url
    url_list = []
    for uid in uuid:
        url = BARK_URL
        url = f"{url}/{uid}"

        if title:
            title = title.replace("/", "%2F")
            url = f"{url}/{title}"
        content = content.replace("/", "%2F")
        url = f"{url}/{content}?"

        # url参数添加
        param_dict = {}
        if sound:
            param_dict["sound"] = sound
        if is_archive is False:
            param_dict["isArchive"] = 0
        if icon:
            param_dict["icon"] = icon
        if group:
            param_dict["group"] = group
        if level:
            param_dict["level"] = level
        if target_url:
            param_dict["url"] = target_url
        if copy:
            param_dict["copy"] = copy
        if badge:
            param_dict["badge"] = badge
        if auto_copy:
            param_dict["autoCopy"] = 1

        url = f"{url}{urllib.parse.urlencode(param_dict)}"
        url_list.append(url)

    # 发送通知
    success_request = 0
    request_task_list = [_request(url) for url in url_list]
    request_resp_list = await asyncio.gather(*request_task_list)

    for url, request_resp in zip(url_list, request_resp_list):
        if not request_resp:
            continue
        resp_code = request_resp.status_code

        # HTTP异常
        if resp_code != 200:
            logger.warning("发送notification的请求异常 %s", url)
            continue

        # 通知异常
        rsp_json = json.loads(request_resp.text)
        if rsp_json.get("message") != "success":
            logger.warning("发送notification失败 %s", url)
            continue

        success_request += 1

    return success_request
