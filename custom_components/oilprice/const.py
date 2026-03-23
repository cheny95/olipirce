"""Constants for the oilprice integration."""

from datetime import timedelta

DOMAIN = "oilprice"
PLATFORMS = ["sensor"]

DEFAULT_NAME = "油价"
ICON = "mdi:gas-station"
SCAN_INTERVAL = timedelta(hours=8)

REGIONS: dict[str, str] = {
    "anhui": "安徽",
    "beijing": "北京",
    "chongqing": "重庆",
    "fujian": "福建",
    "gansu": "甘肃",
    "guangdong": "广东",
    "guangxi": "广西",
    "guizhou": "贵州",
    "hainan": "海南",
    "hebei": "河北",
    "heilongjiang": "黑龙江",
    "henan": "河南",
    "hubei": "湖北",
    "hunan": "湖南",
    "jiangsu": "江苏",
    "jiangxi": "江西",
    "jilin": "吉林",
    "liaoning": "辽宁",
    "neimenggu": "内蒙古",
    "ningxia": "宁夏",
    "qinghai": "青海",
    "shandong": "山东",
    "shanghai": "上海",
    "shanxi": "山西",
    "shan-xi": "陕西",
    "sichuan": "四川",
    "tianjin": "天津",
    "xinjiang": "新疆",
    "xizang": "西藏",
    "yunnan": "云南",
    "zhejiang": "浙江",
}

REGION_SELECTOR_OPTIONS: list[dict[str, str]] = [
    {"value": code, "label": f"{name} ({code})"} for code, name in REGIONS.items()
]


def region_name(region: str) -> str:
    """Return a friendly region name."""
    return REGIONS.get(region, region)

