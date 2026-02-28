---
name: get_weather
description: 获取指定城市的实时天气信息
---

# 获取天气信息技能说明（v2，默认 Open-Meteo｜无需 API Key）

为提升稳定性与可用性，本技能默认使用 Open-Meteo（免费、无需密钥），并提供 wttr.in 与 OpenWeatherMap 作为备选。

## 一、快速开始（推荐：Open-Meteo）
- 支持中文或英文城市名（例："成都"、"Chengdu"、"北京"、"Beijing"）
- 返回当前气温、体感、湿度、风速/风向、云量、降水与中文天气描述

请在 `python_repl` 中执行：
```python
import requests

def _wmo_mapping(code:int)->str:
    mapping = {
        0:'晴',1:'少云',2:'多云(中)',3:'多云(多)',45:'雾',48:'雾(沉积)',
        51:'毛毛雨(小)',53:'毛毛雨(中)',55:'毛毛雨(大)',56:'冻毛毛雨(小)',57:'冻毛毛雨(大)',
        61:'小雨',63:'中雨',65:'大雨',66:'冻雨(小/中)',67:'冻雨(大)',
        71:'小雪',73:'中雪',75:'大雪',77:'雪粒',
        80:'阵雨(小)',81:'阵雨(中)',82:'阵雨(大)',
        85:'阵雪(小/中)',86:'阵雪(大)',
        95:'雷阵雨',96:'雷阵雨伴小冰雹',99:'雷阵雨伴大冰雹'
    }
    return mapping.get(code, f'天气代码 {code}')


def get_weather(city:str)->str:
    """使用 Open-Meteo 查询城市实时天气。返回已格式化的中文字符串。"""
    try:
        # 1) 地理编码
        geo = requests.get(
            'https://geocoding-api.open-meteo.com/v1/search',
            params={'name': city, 'count': 1, 'language': 'zh', 'format': 'json'},
            timeout=8
        ).json()
        if not geo.get('results'):
            return '查询失败：未找到城市'
        r = geo['results'][0]
        lat, lon = r['latitude'], r['longitude']
        tz = r.get('timezone', 'Asia/Shanghai')
        # 2) 实时天气
        weather = requests.get(
            'https://api.open-meteo.com/v1/forecast',
            params={
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m,cloud_cover',
                'timezone': tz
            },
            timeout=8
        ).json()
        cur = weather.get('current', {})
        desc = _wmo_mapping(cur.get('weather_code'))
        return (
            f"城市：{r.get('name')} | 当前温度：{cur.get('temperature_2m')}℃ | 体感：{cur.get('apparent_temperature')}℃ | "
            f"湿度：{cur.get('relative_humidity_2m')}% | 风速：{cur.get('wind_speed_10m')} m/s | 风向：{cur.get('wind_direction_10m')}° | "
            f"云量：{cur.get('cloud_cover')}% | 降水：{cur.get('precipitation')} mm | 天气：{desc}"
        )
    except Exception as e:
        return f'查询失败：{e}'

# 示例：
print(get_weather('成都'))
# print(get_weather('Chengdu'))
```

## 二、备选方案 A：wttr.in（有时不稳定｜无需密钥）
```python
import requests
city_pinyin = 'chengdu'  # 城市拼音/英文
url = f"https://wttr.in/{city_pinyin}?format=j1"
try:
    data = requests.get(url, timeout=10).json()
    temp = data['current_condition'][0]['temp_C']
    cond = data['current_condition'][0]
    desc = cond['lang_zh'][0]['value'] if 'lang_zh' in cond and cond['lang_zh'] else cond['weatherDesc'][0]['value']
    print(f'当前温度：{temp}℃，天气：{desc}')
except Exception as e:
    print(f'查询失败：{e}')
```

## 三、备选方案 B：OpenWeatherMap（稳定｜需注册 API Key）
1) 注册获取 API Key：https://home.openweathermap.org/
2) 执行：
```python
import requests
city = 'Chengdu'
API_KEY = 'YOUR_API_KEY'
url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
try:
    data = requests.get(url, timeout=10).json()
    temp = data['main']['temp']
    desc = data['weather'][0]['description']
    print(f'当前温度：{temp}℃，天气：{desc}')
except Exception as e:
    print(f'查询失败：{e}')
```

## 备注
- Open-Meteo 返回单位：温度(℃)、风速(m/s)、降水(mm)。
- 如果城市存在重名，建议在 city 中加入国家/地区信息（如 "Chengdu, China"）。
- 若需小时级/未来预报，可在 Open-Meteo 请求中添加 hourly/daily 参数，详见官方文档。
