"""
查询地区实时天气
"""
import json
from typing import Coroutine, Iterable, Union
import httpx
from logger import logger
from ..api import notify_bark
from .conf import API_KEY, GEOAPI_URL, WEATHER_URL, REC_TYPES


async def _get_location_id(
        location_name: str,
        adm: str = None,
        range_: str = None) -> str:
    """ 获取城市的location_id

    :param location_name: 需要查询地区的名称
    :param adm: 城市的上级行政区划
    :param range_: 搜索范围，可设定只在某个国家范围内进行搜索

    :return: 地区id
    """
    # 指定获取数量
    info_number = 1
    # 构建url
    url = GEOAPI_URL
    url += f"location={location_name}&key={API_KEY}&number={info_number}"

    if adm:
        url += f"&adm={adm}"
    if range_:
        url += f"&range={range_}"

    # 发送请求
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if not resp.status_code or resp.status_code != 200:
        logger.warning("获取location_id请求异常 %s", url)
        return None

    resp_json = json.loads(resp.text)
    resp_code = resp_json.get("code")
    if not resp_code or resp_code != "200":
        logger.warning("获取location_id返回异常 %s %s", url, resp_json)
        return None

    if not resp_json.get("location") or \
            len(resp_json.get("location")) != info_number:
        logger.warning("返回location列表异常 %s %s", url, resp_json)
        return None

    location_id = resp_json.get("location")[0].get("id")
    if not location_id:
        logger.warning("返回location的id异常 %s %s", url, resp_json)
        return None

    return location_id


async def get_weather(
        uid_dict: dict,
        location_name: str,
        adm: str = None,
        range_: str = None,
        rec_types: tuple = ("temp", "text")
) -> Union[Iterable[Coroutine], Coroutine]:
    """获取地区的天气信息

    :param uid_dict: 用户id字典
    :param location_name: 需要查询地区的名称
    :param adm: 城市的上级行政区划
    :param range_: 搜索范围，可设定只在某个国家范围内进行搜索
    :param rec_types: 需要获取信息的类别

    :return: 调用通知api的函数
    """
    # 获取地区id
    location_id = await _get_location_id(
        location_name=location_name,
        adm=adm,
        range_=range_
    )

    # 构建url
    url = WEATHER_URL
    url += f"location={location_id}&key={API_KEY}"

    # 发送请求
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if not resp.status_code or resp.status_code != 200:
        logger.warning("获取weather请求异常 %s", url)
        return None

    resp_json = json.loads(resp.text)
    resp_code = resp_json.get("code")
    if not resp_code or resp_code != "200":
        logger.warning("获取weather返回异常 %s %s", url, resp_json)
        return None

    weather_info = resp_json.get("now")
    if not weather_info:
        logger.warning("返回weather数据异常 %s %s", url, resp_json)

    # 构建通知内容
    content = ""
    for rec_type in rec_types:
        if rec_type not in list(REC_TYPES):
            continue

        rec_val = weather_info.get(rec_type, "")
        if rec_val == "":
            continue

        content += f"{REC_TYPES.get(rec_type).format(rec_val)} "

    # 构建通知函数
    callback_func = notify_bark(
        uuid=uid_dict.get("bark", {}).get("uuid"),
        content=content,
        title=f"{location_name}今日天气",
    )

    return callback_func
