"""Support for AVM FRITZ!SmartHome lightbulbs."""
from __future__ import annotations

# from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
    DEVICE_CLASS_BLIND,
    CoverDeviceClass,
    CoverEntity,
)
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import FritzBoxEntity
from .const import (
    CONF_COORDINATOR,
    DOMAIN as FRITZBOX_DOMAIN,
)

SUPPORT_FLAGS = SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the FRITZ!SmartHome blind from ConfigEntry."""
    coordinator = hass.data[FRITZBOX_DOMAIN][entry.entry_id][CONF_COORDINATOR]

    async_add_entities(
        [
            FritzboxBlind(coordinator, ain)
            for ain, device in coordinator.data.items()
            if device.has_blind
        ]
    )


class FritzboxBlind(FritzBoxEntity, CoverEntity):
    """Representation of a blind device."""

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def device_class(self) -> CoverDeviceClass | None:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_BLIND

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return 100 == self.device.get_level_percentage()

    @property
    def current_cover_position(self) -> int:
        """Return the current position of the cover."""
        return 100 - self.device.get_level_percentage()

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self.hass.async_add_executor_job(self.device.set_blind_open)

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        await self.hass.async_add_executor_job(self.device.set_blind_close)

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        await self.hass.async_add_executor_job(self.device.set_blind_stop)

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        await self.hass.async_add_executor_job(
            self.device.set_level_percentage, 100 - position
        )
