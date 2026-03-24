"""Button platform for oilprice."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN, region_name
from .coordinator import OilPriceDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up oilprice refresh button from config entry."""
    coordinator: OilPriceDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities([OilPriceRefreshButton(entry, coordinator)])


class OilPriceRefreshButton(CoordinatorEntity[OilPriceDataUpdateCoordinator], ButtonEntity):
    """Button to trigger immediate refresh."""

    _attr_icon = "mdi:refresh"
    _attr_has_entity_name = False

    def __init__(self, entry: ConfigEntry, coordinator: OilPriceDataUpdateCoordinator) -> None:
        """Initialize refresh button."""
        super().__init__(coordinator)
        region = entry.data[CONF_REGION]
        self._region = region
        self._region_name = region_name(region)
        self._region_slug = slugify(self._region_name)
        self._attr_unique_id = f"{entry.entry_id}_refresh"
        self._attr_object_id = f"you_jie_{self._region_slug}_refresh"
        self._attr_name = f"油价-{self._region_name}-立即更新"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device metadata for grouping entities on one device page."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._region)},
            name=f"油价-{self._region_name}",
            manufacturer="Chan",
            model="Oil Price",
        )

