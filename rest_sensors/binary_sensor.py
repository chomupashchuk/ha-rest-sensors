"""Suppoort for rest binary sensors."""
import logging
from datetime import timedelta

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_HEAT,
    BinarySensorEntity,
)
from homeassistant.const import CONF_NAME, CONF_BINARY_SENSORS
from homeassistant.helpers.entity import Entity

from .sensor import (
    DATA_REST,
    DEVICES,
)

# Internal component binary sensor names
# BINARY_SENSOR_UPDATE_DOCKER = "ha_docker_update"
BINARY_SENSOR_UPDATE_HASSIO = "ha_hassio_update"

# Home Assistant names
# NAME_UPDATE_DOCKER = "HA Docker Update Available"
NAME_UPDATE_HASSIO = "HA Hassio Update Available"

BINARY_SENSOR_SCAN_INTERVAL_SECS = 5
SCAN_INTERVAL = timedelta(seconds=BINARY_SENSOR_SCAN_INTERVAL_SECS)

_LOGGER = logging.getLogger(__name__)

# Binary Sensor types are defined like: Name, class, icon
BINARY_SENSORS = {
    # BINARY_SENSOR_UPDATE_DOCKER: [NAME_UPDATE_DOCKER, None, "mdi:package-down"],
    BINARY_SENSOR_UPDATE_HASSIO: [NAME_UPDATE_HASSIO, None, "mdi:package-down"],
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up a binary sensor for REST."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    device = hass.data[DATA_REST][DEVICES][name]
    add_entities(
        [
            BankRestBinarySensor(name, device, binary_sensor_type)
            for binary_sensor_type in discovery_info[CONF_BINARY_SENSORS]
        ],
        True,
    )


class BankRestBinarySensor(BinarySensorEntity):
    """A binary sensor implementation for REST."""

    def __init__(self, name, device, binary_sensor_type):
        """Initialize a binary sensor for REST."""
        self._name = BINARY_SENSORS[binary_sensor_type][0]
        self._api = device.api
        self._binary_sensor_type = binary_sensor_type
        self._is_on = False
        self._device_class = BINARY_SENSORS[binary_sensor_type][1]
        self._icon = BINARY_SENSORS[binary_sensor_type][2]

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return True

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._is_on

    #@property
    #def state(self):
    #    """Return the state of the binary sensor."""
    #    return self._is_on

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self._binary_sensor_type in BINARY_SENSORS:
            return self._api._sensor_attrib[self._binary_sensor_type]
        return None

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_class(self):
        """Return device class."""
        return self._device_class

    @property
    def available(self):
        """Return True if entity is available."""
        return self._api.available(self._binary_sensor_type)

    def update(self):
        """Get the latest data and updates the state."""
        if not self.available:
            return
        _LOGGER.debug("Updating %s binary sensor", self._name)

        try:
        
            if self._api.available(self._binary_sensor_type):
                self._is_on = self._api.sensor_data[self._binary_sensor_type]
            else:
                self._is_on = False

        except KeyError:
            _LOGGER.warning("Problem updating binary sensors")
