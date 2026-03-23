"""Config flow for oilprice integration."""

from __future__ import annotations

import logging
from typing import Any, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_REGION
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .api import OilPriceCannotConnectError, OilPriceInvalidRegionError, async_fetch_oilprice
from .const import DEFAULT_NAME, DOMAIN, REGION_SELECTOR_OPTIONS, region_name

_LOGGER = logging.getLogger(__name__)


class OilPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for oilprice."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            region = user_input[CONF_REGION]
            name = user_input.get(CONF_NAME, DEFAULT_NAME).strip() or DEFAULT_NAME

            await self.async_set_unique_id(region)
            self._abort_if_unique_id_configured()

            try:
                # Validate once during setup so users get immediate feedback.
                await async_fetch_oilprice(self.hass, region)
            except OilPriceCannotConnectError:
                errors["base"] = "cannot_connect"
            except OilPriceInvalidRegionError:
                errors["base"] = "invalid_region"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error while validating region")
                errors["base"] = "unknown"
            else:
                title = f"{name}-{region_name(region)}"
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_NAME: name,
                        CONF_REGION: region,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REGION, default="anhui"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=REGION_SELECTOR_OPTIONS,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )

