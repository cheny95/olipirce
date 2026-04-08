"""Tests for oilprice API parsing and error handling."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


# Provide lightweight stubs so tests can run without Home Assistant installed.
def _install_stub_modules() -> None:
    if "aiohttp" not in sys.modules:
        aiohttp_mod = types.ModuleType("aiohttp")

        class ClientError(Exception):
            """Stub aiohttp client error."""

        aiohttp_mod.ClientError = ClientError
        sys.modules["aiohttp"] = aiohttp_mod

    if "homeassistant" not in sys.modules:
        homeassistant_mod = types.ModuleType("homeassistant")
        helpers_mod = types.ModuleType("homeassistant.helpers")
        aiohttp_client_mod = types.ModuleType("homeassistant.helpers.aiohttp_client")
        util_mod = types.ModuleType("homeassistant.util")
        dt_mod = types.ModuleType("homeassistant.util.dt")

        def _placeholder_session(_hass):
            raise RuntimeError("async_get_clientsession should be patched in tests")

        def _default_now():
            return datetime.now(timezone.utc)

        aiohttp_client_mod.async_get_clientsession = _placeholder_session
        dt_mod.now = _default_now
        util_mod.dt = dt_mod

        sys.modules["homeassistant"] = homeassistant_mod
        sys.modules["homeassistant.helpers"] = helpers_mod
        sys.modules["homeassistant.helpers.aiohttp_client"] = aiohttp_client_mod
        sys.modules["homeassistant.util"] = util_mod
        sys.modules["homeassistant.util.dt"] = dt_mod


_install_stub_modules()


def _load_api_module():
    """Load api.py directly to avoid importing integration __init__.py in tests."""
    project_root = Path(__file__).resolve().parents[1]
    custom_components_dir = project_root / "custom_components"
    oilprice_dir = custom_components_dir / "oilprice"

    if "custom_components" not in sys.modules:
        custom_components_pkg = types.ModuleType("custom_components")
        custom_components_pkg.__path__ = [str(custom_components_dir)]
        sys.modules["custom_components"] = custom_components_pkg
    else:
        custom_components_pkg = sys.modules["custom_components"]

    if "custom_components.oilprice" not in sys.modules:
        oilprice_pkg = types.ModuleType("custom_components.oilprice")
        oilprice_pkg.__path__ = [str(oilprice_dir)]
        sys.modules["custom_components.oilprice"] = oilprice_pkg
    else:
        oilprice_pkg = sys.modules["custom_components.oilprice"]

    custom_components_pkg.oilprice = oilprice_pkg

    spec = importlib.util.spec_from_file_location(
        "custom_components.oilprice.api", oilprice_dir / "api.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load custom_components.oilprice.api")

    module = importlib.util.module_from_spec(spec)
    sys.modules["custom_components.oilprice.api"] = module
    spec.loader.exec_module(module)
    oilprice_pkg.api = module
    return module


api = _load_api_module()


SAMPLE_HTML = """
<div>
  安徽今日油价
  以下油价数据更新时间：2026年03月24日；油价下次调价时间为2026年4月7日 24:00；数据来源各地加油站，仅供参考，实际以各加油站为准。
</div>
<div>
  今日汽油价格（元/升）
  89号汽油
  92号汽油
  95号汽油
  98号汽油
  -
  8.51
  9.10
  10.60
  今日柴油价格（元/升）
  0号柴油
  -10号柴油
  -20号柴油
  -35号柴油
  8.30
  8.79
  -
  -
</div>
<div>
  安徽油价调整最新消息
  2026年3月24日今日油价最新消息：国际油价上涨，美国原油价格上涨3.1%到90.89美元/桶，新一轮10个工作日统计周期，经过10个工作日统计，预计油价上涨2205元/吨。
</div>
"""

TABLE_HTML = """
<div>
  <table class="bx" width="100%" cellspacing="0" cellpadding="0" border="1" align="center">
      <thead>
          <tr>
              <th colspan="4">今日汽油价格（元/升）</th>
          </tr>
      </thead>
      <tbody>
          <tr>
              <th>89号汽油</th>
              <th>92号汽油</th>
              <th>95号汽油</th>
              <th>98号汽油</th>
          </tr>
          <tr>
              <td></td>
              <td>8.57</td>
              <td>9.12</td>
              <td>10.62</td>
          </tr>
      </tbody>
  </table>

  <table class="bx" width="100%" cellspacing="0" cellpadding="0" border="1" align="center">
      <thead>
          <tr>
              <th colspan="4">今日柴油价格（元/升）</th>
          </tr>
      </thead>
      <tbody>
          <tr>
              <th>0号柴油</th>
              <th>-10号柴油</th>
              <th>-20号柴油</th>
              <th>-35号柴油</th>
          </tr>
          <tr>
              <td>8.31</td>
              <td>8.81</td>
              <td>9.23</td>
              <td></td>
          </tr>
      </tbody>
  </table>
  <div>以下油价数据更新时间：2026年03月24日；油价下次调价时间为2026年4月7日 24:00；</div>
  <div>2026年3月24日今日油价最新消息：国际油价上涨。</div>
</div>
"""

SICHUAN_HTML = """
<div>
  <table class="bx" width="100%" cellspacing="0" cellpadding="0" border="1" align="center">
      <tbody>
          <tr>
              <td colspan="5"><strong>四川</strong><strong>今日油价查询（元/升）</strong></td>
          </tr>
          <tr>
              <td>地区</td>
              <td>92号汽油</td>
              <td>95号汽油</td>
              <td>98号汽油</td>
              <td>0号柴油</td>
          </tr>
          <tr>
              <td><a href="http://www.huangjinjiage.cn/oil/sichuan.html">四川油价</a></td>
              <td>8.66</td>
              <td>9.25</td>
              <td>10.56</td>
              <td>8.29</td>
          </tr>
          <tr>
              <td><a href="http://www.huangjinjiage.cn/oil/chengdu.html">成都油价</a></td>
              <td>8.66</td>
              <td>9.25</td>
              <td>10.56</td>
              <td>8.29</td>
          </tr>
      </tbody>
  </table>
  <div>油价下次调价时间为2026年4月7日 24:00</div>
  <div>2026年3月24日今日油价最新消息：国际油价上涨。</div>
</div>
"""

MULTI_CITY_FIRST_ROW_HTML = """
<div>
  <table class="bx" width="100%" cellspacing="0" cellpadding="0" border="1" align="center">
      <tbody>
          <tr>
              <td colspan="5"><strong>北京</strong><strong>今日油价查询（元/升）</strong></td>
          </tr>
          <tr>
              <td>地区</td>
              <td>92号汽油</td>
              <td>95号汽油</td>
              <td>98号汽油</td>
              <td>0号柴油</td>
          </tr>
          <tr>
              <td><a href="http://www.huangjinjiage.cn/oil/beijing.html">北京油价</a></td>
              <td>8.57</td>
              <td>9.12</td>
              <td>10.62</td>
              <td>8.31</td>
          </tr>
          <tr>
              <td><a href="http://www.huangjinjiage.cn/oil/chaoyang.html">朝阳油价</a></td>
              <td>7.11</td>
              <td>7.22</td>
              <td>7.33</td>
              <td>7.44</td>
          </tr>
      </tbody>
  </table>
  <div>油价下次调价时间为2026年4月7日 24:00</div>
  <div>2026年3月24日今日油价最新消息：国际油价上涨。</div>
</div>
"""


class _FakeResponse:
    def __init__(self, status: int, text: str) -> None:
        self.status = status
        self._text = text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def text(self, encoding: str = "utf-8", errors: str = "ignore") -> str:
        return self._text

    async def read(self) -> bytes:
        return self._text.encode("utf-8")


class _FakeSession:
    def __init__(self, response: _FakeResponse | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error

    def get(self, _url: str, headers: dict | None = None):
        if self._error is not None:
            raise self._error
        return self._response


class ApiFetchTests(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_oilprice_success(self) -> None:
        session = _FakeSession(response=_FakeResponse(status=200, text=SAMPLE_HTML))
        fixed_now = datetime(2026, 3, 24, 16, 32, 5, tzinfo=timezone.utc)

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session), patch(
            "custom_components.oilprice.api.dt_util.now", return_value=fixed_now
        ):
            data = await api.async_fetch_oilprice(hass=object(), region="anhui")

        self.assertEqual(data["gas92"], "8.51")
        self.assertEqual(data["gas95"], "9.10")
        self.assertEqual(data["gas98"], "10.60")
        self.assertEqual(data["die0"], "8.30")
        self.assertEqual(data["time"], "油价下次调价时间为2026年4月7日 24:00")
        self.assertIn("今日油价最新消息", data["tips"])
        self.assertEqual(data["trend"], "上涨")
        self.assertEqual(data["next_adjust_date"], "2026年4月8日0点")
        self.assertEqual(data["update_time"], "2026-03-24 16:32:05")
        self.assertEqual(data["region_name"], "安徽")

    async def test_fetch_oilprice_http_error(self) -> None:
        session = _FakeSession(response=_FakeResponse(status=404, text="not found"))

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session):
            with self.assertRaises(api.OilPriceCannotConnectError):
                await api.async_fetch_oilprice(hass=object(), region="anhui")

    async def test_fetch_oilprice_client_error(self) -> None:
        session = _FakeSession(error=api.ClientError("network error"))

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session):
            with self.assertRaises(api.OilPriceCannotConnectError):
                await api.async_fetch_oilprice(hass=object(), region="anhui")

    async def test_fetch_oilprice_invalid_region_content(self) -> None:
        bad_html = "<html><body>no fuel data here</body></html>"
        session = _FakeSession(response=_FakeResponse(status=200, text=bad_html))

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session):
            with self.assertRaises(api.OilPriceInvalidRegionError):
                await api.async_fetch_oilprice(hass=object(), region="unknown")

    async def test_fetch_oilprice_table_layout_success(self) -> None:
        session = _FakeSession(response=_FakeResponse(status=200, text=TABLE_HTML))

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session):
            data = await api.async_fetch_oilprice(hass=object(), region="beijing")

        self.assertEqual(data["gas92"], "8.57")
        self.assertEqual(data["gas95"], "9.12")
        self.assertEqual(data["gas98"], "10.62")
        self.assertEqual(data["die0"], "8.31")

    async def test_fetch_oilprice_region_table_uses_first_row(self) -> None:
        session = _FakeSession(response=_FakeResponse(status=200, text=SICHUAN_HTML))

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session):
            data = await api.async_fetch_oilprice(hass=object(), region="sichuan")

        self.assertEqual(data["gas92"], "8.66")
        self.assertEqual(data["gas95"], "9.25")
        self.assertEqual(data["gas98"], "10.56")
        self.assertEqual(data["die0"], "8.29")

    async def test_fetch_oilprice_multi_city_table_uses_first_row(self) -> None:
        session = _FakeSession(response=_FakeResponse(status=200, text=MULTI_CITY_FIRST_ROW_HTML))

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session):
            data = await api.async_fetch_oilprice(hass=object(), region="beijing")

        self.assertEqual(data["gas92"], "8.57")
        self.assertEqual(data["gas95"], "9.12")
        self.assertEqual(data["gas98"], "10.62")
        self.assertEqual(data["die0"], "8.31")

    async def test_fetch_oilprice_tips_with_strong_tag(self) -> None:
        """Test that tips extraction includes text within <strong> tags."""
        html_with_strong = """
        <div>
          <h2>安徽油价调整最新消息</h2>
          <p>2026年4月8日今日油价最新消息：国际油价下跌，美国原油价格下跌12.61%到96.32美元/桶，
          布伦特原油价格下跌10.26%到92.31美元/桶，新一轮10个工作日统计周期，经过10个工作日统计，
          <strong>根据国家对油价的调控，今晚汽油上涨420元/吨，柴油上涨400元/吨，
          即92号汽油上涨0.33元/升，0号柴油上涨0.34元/升</strong>，
          下次国内成品油价调整窗口时间为2026年4月21日24时（2026年4月22日0点）。</p>
        </div>
        """
        session = _FakeSession(response=_FakeResponse(status=200, text=html_with_strong))

        with patch("custom_components.oilprice.api.async_get_clientsession", return_value=session):
            data = await api.async_fetch_oilprice(hass=object(), region="anhui")

        self.assertIn("今日油价最新消息", data["tips"])
        self.assertIn("根据国家对油价的调控", data["tips"])
        self.assertIn("今晚汽油上涨420元/吨", data["tips"])
        self.assertEqual(data["trend"], "上涨")


class ApiParserTests(unittest.TestCase):
    def test_extract_trend_text(self) -> None:
        self.assertEqual(api._extract_trend_text("预计油价上涨0.5元/升"), "上涨")
        self.assertEqual(api._extract_trend_text("预计油价下调200元/吨"), "下调")
        self.assertEqual(api._extract_trend_text("本轮调价或将搁浅"), "搁浅")
        self.assertEqual(
            api._extract_trend_text(
                "今日油价最新消息：国际油价下跌。新一轮10个工作日统计周期，经过7个工作日统计，预计油价上涨190元/吨，即油价上涨0.14元/升-0.17元/升。"
            ),
            "上涨",
        )
        self.assertIsNone(
            api._extract_trend_text(
                "今日油价最新消息：新一轮10个工作日统计周期，国际油价下跌，但暂无预计油价方向。"
            )
        )
        self.assertEqual(
            api._extract_trend_text(
                "2026年4月2日今日油价最新消息：国际油价下跌，美国原油价格下跌1.46%到98.66美元/桶，"
                "布伦特原油价格下跌2.85%到100.31美元/桶，新一轮10个工作日统计周期，经过7个工作日统计，"
                "预计油价上涨190元/吨，即油价上涨0.14元/升-0.17元/升，下次国内成品油价调整窗口时间为2026年4月7日24时。"
            ),
            "上涨",
        )
        self.assertIsNone(
            api._extract_trend_text(
                "2026年4月2日今日油价最新消息：国际油价下跌，美国原油价格下跌1.46%到98.66美元/桶，布伦特原油价格下跌2.85%。"
            )
        )
        self.assertIsNone(api._extract_trend_text("无明确趋势"))

    def test_extract_next_adjust_date_text(self) -> None:
        self.assertEqual(
            api._extract_next_adjust_date_text("油价下次调价时间为2026年4月7日 24:00"),
            "2026年4月8日0点",
        )
        self.assertEqual(
            api._extract_next_adjust_date_text("下次国内成品油价调整窗口时间为2026年4月8日0点"),
            "2026年4月8日0点",
        )
        self.assertEqual(
            api._extract_next_adjust_date_text("油价下次调价时间为2026年4月9日 09:30"),
            "2026年4月9日9:30",
        )
        self.assertIsNone(api._extract_next_adjust_date_text("无日期"))


if __name__ == "__main__":
    unittest.main()

