"""The oilprice integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import slugify

from .const import (
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    PLATFORMS,
    SENSOR_STATE_KEYS,
    region_name,
)
from .coordinator import OilPriceDataUpdateCoordinator


def _normalize_entity_ids(
    entity_registry: er.EntityRegistry,
    entry: ConfigEntry,
    region: str,
) -> None:
    """Normalize entity IDs to the stable `you_jie_*` pattern."""
    region_slug = slugify(region_name(region))

    expected_sensor_ids = {
        key: f"sensor.you_jie_{region_slug}_{key}" for key in SENSOR_STATE_KEYS
    }
    expected_button_id = f"button.you_jie_{region_slug}_refresh"

    legacy_sensor_unique_ids = {
        f"{entry.entry_id}_oilprice",
        f"{entry.entry_id}_{region}",
    }

    for entity_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        if entity_entry.domain == "sensor" and entity_entry.unique_id in legacy_sensor_unique_ids:
            # Drop the old single-sensor model.
            entity_registry.async_remove(entity_entry.entity_id)
            continue

        if entity_entry.domain == "sensor" and entity_entry.unique_id:
            prefix = f"{entry.entry_id}_"
            if entity_entry.unique_id.startswith(prefix):
                field_key = entity_entry.unique_id[len(prefix) :]
                target_entity_id = expected_sensor_ids.get(field_key)
                if target_entity_id and entity_entry.entity_id != target_entity_id:
                    entity_registry.async_update_entity(
                        entity_entry.entity_id,
                        new_entity_id=target_entity_id,
                    )

        if (
            entity_entry.domain == "button"
            and entity_entry.unique_id == f"{entry.entry_id}_refresh"
            and entity_entry.entity_id != expected_button_id
        ):
            entity_registry.async_update_entity(
                entity_entry.entity_id,
                new_entity_id=expected_button_id,
            )

        # Compatibility cleanup from previous naming attempts.
        if "you_jia" in entity_entry.entity_id:
            entity_registry.async_update_entity(
                entity_entry.entity_id,
                new_entity_id=entity_entry.entity_id.replace("you_jia", "you_jie"),
            )


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from UI config entry."""
    region = entry.data[CONF_REGION]
    update_interval_hours = int(
        entry.options.get(CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS)
    )

    coordinator = OilPriceDataUpdateCoordinator(hass, region, update_interval_hours)
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        raise ConfigEntryNotReady("Failed to initialize oilprice data") from err

    unsubscribe_update_listener = entry.add_update_listener(_async_update_listener)
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "unsubscribe_update_listener": unsubscribe_update_listener,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Ensure existing and newly-created entities converge to one stable ID pattern.
    _normalize_entity_ids(er.async_get(hass), entry, region)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        runtime = hass.data[DOMAIN].pop(entry.entry_id, None)
        if runtime and runtime.get("unsubscribe_update_listener"):
            runtime["unsubscribe_update_listener"]()
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entries to latest schema."""
    if entry.version == 1:
        update_hours = entry.data.get(
            CONF_UPDATE_INTERVAL_HOURS,
            DEFAULT_UPDATE_INTERVAL_HOURS,
        )
        new_data = dict(entry.data)
        new_data.pop(CONF_UPDATE_INTERVAL_HOURS, None)
        new_options = dict(entry.options)
        new_options[CONF_UPDATE_INTERVAL_HOURS] = int(update_hours)
        hass.config_entries.async_update_entry(
            entry,
            data=new_data,
            options=new_options,
            version=2,
        )

    if entry.version in (2, 3):
        _normalize_entity_ids(er.async_get(hass), entry, entry.data[CONF_REGION])
        hass.config_entries.async_update_entry(entry, version=4)

    return True
