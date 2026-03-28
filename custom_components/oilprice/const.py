"""Constants for the oilprice integration."""

DOMAIN = "oilprice"
PLATFORMS = ["sensor", "button"]

CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"
DEFAULT_UPDATE_INTERVAL_HOURS = 12
MIN_UPDATE_INTERVAL_HOURS = 1
MAX_UPDATE_INTERVAL_HOURS = 168

DEFAULT_REGION = "beijing"
ICON = "mdi:gas-station"

FUEL_KEY_TO_ATTR = {
    "92": "gas92",
    "95": "gas95",
    "98": "gas98",
    "0": "die0",
}

SENSOR_STATE_KEYS = (
    "gas92",
    "gas95",
    "gas98",
    "die0",
    "time",
    "tips",
    "update_time",
    "friendly_name",
)

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
    "shanxisheng": "陕西",
    "sichuan": "四川",
    "tianjin": "天津",
    "xinjiang": "新疆",
    "xizang": "西藏",
    "yunnan": "云南",
    "zhejiang": "浙江",
}

REGION_SELECTOR_OPTIONS = [
    {"value": code, "label": f"{name} ({code})"} for code, name in REGIONS.items()
]


def region_name(region: str) -> str:
    """Return a friendly region name."""
    return REGIONS.get(region, region)
