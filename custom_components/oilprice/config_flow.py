"""Config flow for oilprice integration."""

from __future__ import annotations

import logging
from typing import Any, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_REGION
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .api import OilPriceCannotConnectError, OilPriceInvalidRegionError, async_fetch_oilprice
from .const import (
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_REGION,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    MAX_UPDATE_INTERVAL_HOURS,
    MIN_UPDATE_INTERVAL_HOURS,
    REGION_SELECTOR_OPTIONS,
    region_name,
)

_LOGGER = logging.getLogger(__name__)


class OilPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for oilprice."""

    VERSION = 4

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return options flow handler."""
        return OilPriceOptionsFlow(config_entry)

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None) -> FlowResult:
        """Handle first step for creating an entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            region = user_input[CONF_REGION]
            update_interval_hours = int(user_input[CONF_UPDATE_INTERVAL_HOURS])

            if not _is_valid_hours(update_interval_hours):
                errors["base"] = "invalid_update_interval"
                return self.async_show_form(
                    step_id="user",
                    data_schema=_build_user_schema(region, update_interval_hours),
                    errors=errors,
                )

            await self.async_set_unique_id(region)
            self._abort_if_unique_id_configured()

            try:
                await async_fetch_oilprice(self.hass, region)
            except OilPriceCannotConnectError:
                errors["base"] = "cannot_connect"
            except OilPriceInvalidRegionError:
                errors["base"] = "invalid_region"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error while validating region")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"油价-{region_name(region)}",
                    data={CONF_REGION: region},
                    options={CONF_UPDATE_INTERVAL_HOURS: update_interval_hours},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_user_schema(DEFAULT_REGION, DEFAULT_UPDATE_INTERVAL_HOURS),
            errors=errors,
        )


class OilPriceOptionsFlow(config_entries.OptionsFlow):
    """Handle options for oilprice."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[dict[str, Any]] = None) -> FlowResult:
        """Update options."""
        if user_input is not None:
            update_interval_hours = int(user_input[CONF_UPDATE_INTERVAL_HOURS])
            if not _is_valid_hours(update_interval_hours):
                return self.async_show_form(
                    step_id="init",
                    data_schema=_build_options_schema(update_interval_hours),
                    errors={"base": "invalid_update_interval"},
                )

            return self.async_create_entry(
                title="",
                data={CONF_UPDATE_INTERVAL_HOURS: update_interval_hours},
            )

        default_hours = int(
            self.config_entry.options.get(
                CONF_UPDATE_INTERVAL_HOURS,
                DEFAULT_UPDATE_INTERVAL_HOURS,
            )
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_build_options_schema(default_hours),
        )


def _build_user_schema(default_region: str, default_hours: int) -> vol.Schema:
    """Build schema for first setup."""
    return vol.Schema(
        {
            vol.Required(CONF_REGION, default=default_region): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=REGION_SELECTOR_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_UPDATE_INTERVAL_HOURS,
                default=default_hours,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_UPDATE_INTERVAL_HOURS,
                    max=MAX_UPDATE_INTERVAL_HOURS,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


def _build_options_schema(default_hours: int) -> vol.Schema:
    """Build schema for options."""
    return vol.Schema(
        {
            vol.Required(
                CONF_UPDATE_INTERVAL_HOURS,
                default=default_hours,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_UPDATE_INTERVAL_HOURS,
                    max=MAX_UPDATE_INTERVAL_HOURS,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            )
        }
    )


def _is_valid_hours(value: int) -> bool:
    """Validate interval hours range."""
    return MIN_UPDATE_INTERVAL_HOURS <= value <= MAX_UPDATE_INTERVAL_HOURS
