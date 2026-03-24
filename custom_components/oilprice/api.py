"""API helpers for the oilprice integration."""

from __future__ import annotations

import re
from typing import Any, Optional, Tuple

from aiohttp import ClientError
from bs4 import BeautifulSoup
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .const import region_name

_BASE_URL = "http://www.huangjinjiage.cn/oil/{region}.html"
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
            raw_bytes = await response.read()
            text = _decode_page(raw_bytes)
    except ClientError as err:
        raise OilPriceCannotConnectError from err

    soup = BeautifulSoup(text, "html.parser")
    normalized_text = _normalize_text(soup.get_text("\n", strip=True))

    table_prices = _extract_prices_from_tables(soup)
    parsed_prices = _extract_prices_by_section(normalized_text)
    gas92 = _pick_price(table_prices.get("gas92"), parsed_prices.get("gas92"))
    gas95 = _pick_price(table_prices.get("gas95"), parsed_prices.get("gas95"))
    gas98 = _pick_price(table_prices.get("gas98"), parsed_prices.get("gas98"))
    die0 = _pick_price(table_prices.get("die0"), parsed_prices.get("die0"))

    time_text, tips_text = _extract_notice_fields(soup, normalized_text)

    if not any([gas92, gas95, gas98, die0, time_text, tips_text]):
        raise OilPriceInvalidRegionError

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


def _extract_notice_fields(
    soup: BeautifulSoup, page_text: str
) -> Tuple[Optional[str], Optional[str]]:
    """Extract notice time and tips from huangjinjiage page text."""
    page_lines = [_normalize_text(line) for line in soup.stripped_strings]
    page_lines = [line for line in page_lines if line]

    time_text = _extract_time_text(page_text)
    tip_text = _extract_tips_text(page_lines)

    return time_text, tip_text


def _normalize_text(text: str) -> str:
    """Normalize whitespace for predictable regex parsing."""
    return re.sub(r"\s+", " ", text).strip()


def _decode_page(raw_bytes: bytes) -> str:
    """Decode source page with fallback charsets used by Chinese websites."""
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_bytes.decode("utf-8", errors="ignore")


def _extract_prices_by_section(page_text: str) -> dict[str, Optional[str]]:
    """Extract fuel prices from ordered gasoline/diesel sections."""
    values = {"gas92": None, "gas95": None, "gas98": None, "die0": None}

    gasoline_match = re.search(
        r"今日汽油价格[（(]元/升[）)](.*?)今日柴油价格[（(]元/升[）)]",
        page_text,
    )
    if gasoline_match is not None:
        gasoline_prices = _extract_price_tokens(gasoline_match.group(1))
        # Order on page: 89, 92, 95, 98.
        if len(gasoline_prices) >= 4:
            values["gas92"] = _none_if_dash(gasoline_prices[1])
            values["gas95"] = _none_if_dash(gasoline_prices[2])
            values["gas98"] = _none_if_dash(gasoline_prices[3])

    diesel_match = re.search(
        r"今日柴油价格[（(]元/升[）)](.*?)(?:油价调整最新消息|今日油价最新消息|$)",
        page_text,
    )
    if diesel_match is not None:
        diesel_prices = _extract_price_tokens(diesel_match.group(1))
        # Order on page: 0, -10, -20, -35.
        if diesel_prices:
            values["die0"] = _none_if_dash(diesel_prices[0])

    return values


def _extract_prices_from_tables(soup: BeautifulSoup) -> dict[str, Optional[str]]:
    """Extract prices from table.bx layout by matching header columns."""
    values = {"gas92": None, "gas95": None, "gas98": None, "die0": None}

    for table in soup.select("table.bx"):
        header_cells = table.select("tbody tr:nth-of-type(1) th, tbody tr:nth-of-type(1) td")
        value_cells = table.select("tbody tr:nth-of-type(2) td, tbody tr:nth-of-type(2) th")
        if not header_cells or not value_cells:
            continue

        for index, header_cell in enumerate(header_cells):
            if index >= len(value_cells):
                continue

            header_text = _normalize_text(header_cell.get_text(" ", strip=True))
            value_text = _normalize_text(value_cells[index].get_text(" ", strip=True))
            value = _normalize_price_value(value_text)

            if "92" in header_text and "汽油" in header_text:
                values["gas92"] = value
            elif "95" in header_text and "汽油" in header_text:
                values["gas95"] = value
            elif "98" in header_text and "汽油" in header_text:
                values["gas98"] = value
            elif header_text.startswith("0") and "柴油" in header_text:
                values["die0"] = value

    return values


def _extract_price_tokens(text: str) -> list[str]:
    """Return ordered price-like tokens (decimal or standalone dash)."""
    return re.findall(r"\d+\.\d+|(?<!\d)-(?=\s|$)", text)


def _none_if_dash(value: str) -> Optional[str]:
    """Convert placeholder dash to None."""
    return None if value == "-" else value


def _normalize_price_value(value: str) -> Optional[str]:
    """Normalize table price cell value."""
    if not value or value == "-":
        return None
    return value


def _pick_price(primary: Optional[str], fallback: Optional[str]) -> Optional[str]:
    """Pick primary parsed value, otherwise fallback value."""
    return primary if primary is not None else fallback


def _extract_time_text(page_text: str) -> Optional[str]:
    """Extract next adjustment time sentence."""
    match = re.search(r"(油价下次调价时间[为:：]?[^；。\n]+)", page_text)
    if match is not None:
        return match.group(1).strip()

    match = re.search(r"(下次国内成品油价调整窗口时间为[^；。\n]+)", page_text)
    if match is not None:
        return match.group(1).strip()

    return None


def _extract_tips_text(page_lines: list[str]) -> Optional[str]:
    """Extract latest trend tip text from news lines."""
    for line in page_lines:
        if "今日油价最新消息" in line:
            return line

    for line in page_lines:
        if "油价调整最新消息" in line:
            return line

    return None


