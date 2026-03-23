"""API helpers for the oilprice integration."""

from __future__ import annotations

import logging
import re
from typing import Any

from aiohttp import ClientError
from bs4 import BeautifulSoup
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .const import region_name

_LOGGER = logging.getLogger(__name__)

_BASE_URL = "http://www.qiyoujiage.com/{region}.shtml"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


class OilPriceApiError(Exception):
    """Base API error."""


class OilPriceCannotConnectError(OilPriceApiError):
    """Raised when remote endpoint cannot be reached."""


class OilPriceInvalidRegionError(OilPriceApiError):
    """Raised when region is invalid or unsupported."""


async def async_fetch_oilprice(hass, region: str) -> dict[str, Any]:
    """Fetch and parse oil price information for a region."""
    session = async_get_clientsession(hass)

    try:
        response = await session.get(_BASE_URL.format(region=region), headers=_HEADERS)
    except ClientError as err:
        raise OilPriceCannotConnectError from err

    if response.status >= 400:
        raise OilPriceCannotConnectError

    text = await response.text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(text, "html.parser")

    fuel_blocks = soup.select("#youjia > dl")
    if not fuel_blocks:
        raise OilPriceInvalidRegionError

    price_text = _extract_price_text(soup)
    entries: dict[str, str] = {}

    for block in fuel_blocks:
        title = block.select_one("dt")
        value = block.select_one("dd")
        if title is None or value is None:
            continue

        match = re.search(r"\d+", title.get_text(strip=True))
        if match is None:
            continue

        entries[match.group(0)] = value.get_text(strip=True)

    tip = soup.select_one("#youjiaCont > div:nth-of-type(2) > span")
    if tip is not None:
        entries["tips"] = tip.get_text(strip=True)

    entries["update_time"] = dt_util.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "state": price_text,
        "entries": entries,
        "region": region,
        "region_name": region_name(region),
    }


def _extract_price_text(soup: BeautifulSoup) -> str:
    info_blocks = soup.select("#youjiaCont > div")
    if len(info_blocks) > 1:
        text = info_blocks[1].get_text(strip=True)
        if text:
            return text
    return "油价信息已更新"

