"""API helpers for the oilprice integration."""

from __future__ import annotations

import re
from typing import Any, Optional, Tuple

from aiohttp import ClientError
from bs4 import BeautifulSoup
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .const import FUEL_KEY_TO_ATTR, region_name

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
        async with session.get(_BASE_URL.format(region=region), headers=_HEADERS) as response:
            if response.status >= 400:
                raise OilPriceCannotConnectError
            text = await response.text(encoding="utf-8", errors="ignore")
    except ClientError as err:
        raise OilPriceCannotConnectError from err

    soup = BeautifulSoup(text, "html.parser")
    price_blocks = soup.select("#youjia > dl")
    if not price_blocks:
        raise OilPriceInvalidRegionError

    gas92 = None
    gas95 = None
    gas98 = None
    die0 = None

    for block in price_blocks:
        title = block.select_one("dt")
        value = block.select_one("dd")
        if title is None or value is None:
            continue

        match = re.search(r"\d+", title.get_text(strip=True))
        if match is None:
            continue

        fuel_no = match.group(0)
        fuel_value = value.get_text(strip=True)
        attr_name = FUEL_KEY_TO_ATTR.get(fuel_no)
        if attr_name == "gas92":
            gas92 = fuel_value
        elif attr_name == "gas95":
            gas95 = fuel_value
        elif attr_name == "gas98":
            gas98 = fuel_value
        elif attr_name == "die0":
            die0 = fuel_value

    time_text, tips_text = _extract_notice_fields(soup)

    update_time = dt_util.now().strftime("%Y-%m-%d %H:%M:%S")
    state = gas92 or time_text or "unknown"

    return {
        "state": state,
        "gas92": gas92,
        "gas95": gas95,
        "gas98": gas98,
        "die0": die0,
        "time": time_text,
        "tips": tips_text,
        "update_time": update_time,
        "region": region,
        "region_name": region_name(region),
    }


def _extract_notice_fields(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    """Extract notice time and tips from the block after #youjia."""
    notice_block = soup.select_one("#youjiaCont > div:nth-of-type(2)")
    if notice_block is None:
        return None, None

    text_parts = [part.strip() for part in notice_block.stripped_strings if part.strip()]
    if not text_parts:
        return None, None

    time_text = next((text for text in text_parts if "下次油价" in text), text_parts[0])

    tip_text = None
    span = notice_block.select_one("span")
    if span is not None:
        span_text = span.get_text(strip=True)
        if span_text:
            tip_text = span_text

    if tip_text is None:
        tip_text = next((text for text in text_parts if "预计" in text or "油价" in text), None)

    return time_text, tip_text
