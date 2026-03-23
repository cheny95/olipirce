"""Data coordinator for the oilprice integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    OilPriceApiError,
    OilPriceCannotConnectError,
    OilPriceInvalidRegionError,
    async_fetch_oilprice,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OilPriceDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage periodic oilprice updates."""

    def __init__(self, hass: HomeAssistant, region: str, update_interval_hours: int) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{region}",
            update_interval=timedelta(hours=max(1, int(update_interval_hours))),
        )
        self._region = region

    @property
    def region(self) -> str:
        """Return configured region."""
        return self._region

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest oilprice data."""
        try:
            return await async_fetch_oilprice(self.hass, self._region)
        except OilPriceCannotConnectError as err:
            raise UpdateFailed("Unable to connect to oilprice service") from err
        except OilPriceInvalidRegionError as err:
            raise UpdateFailed("Region is invalid or unsupported") from err
        except OilPriceApiError as err:
            raise UpdateFailed(str(err)) from err
