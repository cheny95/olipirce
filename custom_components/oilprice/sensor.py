"""Sensor platform for oilprice."""

from __future__ import annotations

from typing import Any, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN, ICON, SENSOR_STATE_KEYS, region_name
from .coordinator import OilPriceDataUpdateCoordinator

_ENTITY_META: dict[str, tuple[str, str]] = {
    "gas92": ("92#汽油", "mdi:gas-station"),
    "gas95": ("95#汽油", "mdi:gas-station"),
    "gas98": ("98#汽油", "mdi:gas-station"),
    "die0": ("0#柴油", "mdi:gas-station"),
    "time": ("下次调价", "mdi:clock-outline"),
    "tips": ("调价提示", "mdi:bullhorn-outline"),
    "update_time": ("更新时间", "mdi:update"),
    "friendly_name": ("地区名称", "mdi:map-marker"),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up oilprice sensors from config entry."""
    coordinator: OilPriceDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    async_add_entities(
        [OilPriceFieldSensor(entry, coordinator, field_key) for field_key in SENSOR_STATE_KEYS]
    )


class OilPriceFieldSensor(CoordinatorEntity[OilPriceDataUpdateCoordinator], SensorEntity):
    """One sensor entity per oilprice field."""

    _attr_has_entity_name = False

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: OilPriceDataUpdateCoordinator,
        field_key: str,
    ) -> None:
        """Initialize field sensor."""
        super().__init__(coordinator)

        self._field_key = field_key
        self._region = entry.data[CONF_REGION]
        self._region_name = region_name(self._region)
        self._region_slug = slugify(self._region_name)

        field_name, icon = _ENTITY_META[field_key]
        self._attr_icon = icon if field_key != "gas92" else ICON

        self._attr_unique_id = f"{entry.entry_id}_{field_key}"
        self._attr_object_id = f"you_jie_{self._region_slug}_{field_key}"
        self._attr_name = f"油价-{self._region_name}-{field_name}"

    @property
    def native_value(self) -> Optional[str]:
        """Return the current field value."""
        if self._field_key == "friendly_name":
            return f"油价-{self._region_name}"

        data: dict[str, Any] = self.coordinator.data or {}
        value = data.get(self._field_key)
        if value is None:
            return None
        return str(value)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device metadata for grouping entities on one device page."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._region)},
            name=f"油价-{self._region_name}",
            manufacturer="qiyoujiage.com",
            model="Oil Price",
        )
