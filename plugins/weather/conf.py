"""
weather包配置文件
"""
API_KEY = ""
GEOAPI_URL = "https://geoapi.qweather.com/v2/city/lookup?"
WEATHER_URL = "https://devapi.qweather.com/v7/weather/now?"
REC_TYPES = {
    "obsTime": "观测时间:{}",
    "temp": "温度:{}",
    "feelsLike": "体感温度:{}",
    "text": "{}",
    "wind360": "风向角度:{}",
    "windDir": "风向:{}",
    "windScale": "风力等级:{}",
    "windSpeed": "风速:{}",
    "humidity": "湿度:{}%",
    "precip": "当前小时累计降水量:{}mm",
    "pressure": "大气压强:{}",
    "vis": "能见度:{}km",
    "cloud": "云量:{}%",
    "dew": "露点温度:{}"
}
