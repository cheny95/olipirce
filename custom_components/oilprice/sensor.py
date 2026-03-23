"""Sensor platform for the oilprice integration."""

from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .api import (
    OilPriceApiError,
    OilPriceCannotConnectError,
    OilPriceInvalidRegionError,
    async_fetch_oilprice,
)
from .const import DEFAULT_NAME, DOMAIN, ICON, SCAN_INTERVAL, region_name

_LOGGER = logging.getLogger(__name__)

_FUEL_ALIAS_MAP = {
    "92": "gas92",
    "95": "gas95",
    "98": "gas98",
    "0": "die0",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up oilprice sensor from config entry."""
    region = entry.data[CONF_REGION]

    coordinator = OilPriceDataUpdateCoordinator(hass, region)
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        raise ConfigEntryNotReady("Failed to initialize oilprice data") from err

    async_add_entities([OilPriceSensor(entry, coordinator)])


class OilPriceDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage periodic oilprice updates."""

    def __init__(self, hass: HomeAssistant, region: str) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{region}",
            update_interval=SCAN_INTERVAL,
        )
        self._region = region

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


class OilPriceSensor(CoordinatorEntity[OilPriceDataUpdateCoordinator], SensorEntity):
    """Representation of a single oilprice sensor."""

    _attr_icon = ICON
    _attr_has_entity_name = False

    def __init__(self, entry: ConfigEntry, coordinator: OilPriceDataUpdateCoordinator) -> None:
        """Initialize the oilprice sensor entity."""
        super().__init__(coordinator)
        region = entry.data[CONF_REGION]

        self._attr_unique_id = f"{entry.entry_id}_{region}"
        self._attr_name = entry.title or f"{DEFAULT_NAME}-{region_name(region)}"

    @property
    def native_value(self) -> Optional[str]:
        """Return the current sensor value."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get("state")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes for the sensor."""
        data = self.coordinator.data
        if not data:
            return {}

        attrs = dict(data.get("entries", {}))
        for raw_key, alias_key in _FUEL_ALIAS_MAP.items():
            if raw_key in attrs and alias_key not in attrs:
                attrs[alias_key] = attrs[raw_key]

        attrs["region"] = data.get("region")
        attrs["region_name"] = data.get("region_name")
        return attrs
