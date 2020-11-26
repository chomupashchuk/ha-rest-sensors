"""Suppoort for rest sensors."""
import logging
from datetime import timedelta

from homeassistant.const import CONF_NAME, CONF_SENSORS
from homeassistant.helpers.entity import Entity

# Internal component sensor names
SENSOR_NBU_USD = "currency_usd"
SENSOR_NBU_EUR = "currency_eur"
SENSOR_NBU_EUR_FIRST = "currency_eur_beginning"
SENSOR_NBU_USD_FIRST = "currency_usd_beginning"
SENSOR_MONOBANK_USD_BID = "monobank_usd_bid"
SENSOR_MONOBANK_USD_ASK = "monobank_usd_ask"
SENSOR_MONOBANK_EUR_BID = "monobank_eur_bid"
SENSOR_MONOBANK_EUR_ASK = "monobank_eur_ask"
SENSOR_PRIVATBANK_USD_ASK = "privatbank_usd_ask"
SENSOR_PRIVATBANK_USD_BID = "privatbank_usd_bid"
SENSOR_PRIVATBANK_EUR_ASK = "privatbank_eur_ask"
SENSOR_PRIVATBANK_EUR_BID = "privatbank_eur_bid"
SENSOR_KREDOBANK_USD_ASK = "kredobank_usd_ask"
SENSOR_KREDOBANK_USD_BID = "kredobank_usd_bid"
SENSOR_KREDOBANK_EUR_ASK = "kredobank_eur_ask"
SENSOR_KREDOBANK_EUR_BID = "kredobank_eur_bid"

# Home Assistant names
NAME_NBU_USD = "Currency USD NBU"
NAME_NBU_EUR = "Currency EUR NBU"
NAME_NBU_EUR_FIRST = "Currency EUR NBU First Day"
NAME_NBU_USD_FIRST = "Currency USD NBU First Day"
NAME_MONOBANK_USD_BID = "Currency USD Monobank Bid"
NAME_MONOBANK_USD_ASK = "Currency USD Monobank Ask"
NAME_MONOBANK_EUR_BID = "Currency EUR Monobank Bid"
NAME_MONOBANK_EUR_ASK = "Currency EUR Monobank Ask"
NAME_PRIVATBANK_USD_ASK = "Currency USD Privatbank Ask"
NAME_PRIVATBANK_USD_BID = "Currency USD Privatbank Bid"
NAME_PRIVATBANK_EUR_ASK = "Currency EUR Privatbank Ask"
NAME_PRIVATBANK_EUR_BID = "Currency EUR Privatbank Bid"
NAME_KREDOBANK_USD_ASK = "Currency USD Kredobank Ask"
NAME_KREDOBANK_USD_BID = "Currency USD Kredobank Bid"
NAME_KREDOBANK_EUR_ASK = "Currency EUR Kredobank Ask"
NAME_KREDOBANK_EUR_BID = "Currency EUR Kredobank Bid"


DATA_REST = "rest_sensors"
DEVICES = "rest_devices"

UNITS = 'rate'
ICON_EUR = 'mdi:currency-eur'
ICON_USD = 'mdi:currency-usd'

SENSOR_SCAN_INTERVAL_SECS = 5
SCAN_INTERVAL = timedelta(seconds=SENSOR_SCAN_INTERVAL_SECS)

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined like: Name, units, icon

SENSORS = {
    SENSOR_NBU_USD: [NAME_NBU_USD, UNITS, ICON_USD],
    SENSOR_NBU_EUR: [NAME_NBU_EUR, UNITS, ICON_EUR],
    SENSOR_NBU_EUR_FIRST: [NAME_NBU_EUR_FIRST, UNITS, ICON_EUR],
    SENSOR_NBU_USD_FIRST: [NAME_NBU_USD_FIRST, UNITS, ICON_USD],
    SENSOR_MONOBANK_USD_BID: [NAME_MONOBANK_USD_BID, UNITS, ICON_USD],
    SENSOR_MONOBANK_USD_ASK: [NAME_MONOBANK_USD_ASK, UNITS, ICON_USD],
    SENSOR_MONOBANK_EUR_BID: [NAME_MONOBANK_EUR_BID, UNITS, ICON_EUR],
    SENSOR_MONOBANK_EUR_ASK: [NAME_MONOBANK_EUR_ASK, UNITS, ICON_EUR],
    SENSOR_PRIVATBANK_USD_ASK: [NAME_PRIVATBANK_USD_ASK, UNITS, ICON_USD],
    SENSOR_PRIVATBANK_USD_BID: [NAME_PRIVATBANK_USD_BID, UNITS, ICON_USD],
    SENSOR_PRIVATBANK_EUR_ASK: [NAME_PRIVATBANK_EUR_ASK, UNITS, ICON_EUR],
    SENSOR_PRIVATBANK_EUR_BID: [NAME_PRIVATBANK_EUR_BID, UNITS, ICON_EUR],
    SENSOR_KREDOBANK_USD_ASK: [NAME_KREDOBANK_USD_ASK, UNITS, ICON_USD],
    SENSOR_KREDOBANK_USD_BID: [NAME_KREDOBANK_USD_BID, UNITS, ICON_USD],
    SENSOR_KREDOBANK_EUR_ASK: [NAME_KREDOBANK_EUR_ASK, UNITS, ICON_EUR],
    SENSOR_KREDOBANK_EUR_BID: [NAME_KREDOBANK_EUR_BID, UNITS, ICON_EUR],
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up a sensor for REST."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    device = hass.data[DATA_REST][DEVICES][name]
    add_entities(
        [
            BankRestSensor(name, device, sensor_type)
            for sensor_type in discovery_info[CONF_SENSORS]
        ],
        True,
    )


class BankRestSensor(Entity):
    """A sensor implementation for REST."""

    def __init__(self, name, device, sensor_type):
        """Initialize a sensor for REST."""
        self._name = SENSORS[sensor_type][0]
        self._api = device.api
        self._sensor_type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSORS[sensor_type][1]
        self._icon = SENSORS[sensor_type][2]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return True

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self._sensor_type in SENSORS:
            return self._api._sensor_attrib[self._sensor_type]
        return None

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._unit_of_measurement

    @property
    def available(self):
        """Return True if entity is available."""
        return self._api.available(self._sensor_type)

    def update(self):
        """Get the latest data and updates the state."""
        if not self.available:
            return
        _LOGGER.debug("Updating %s sensor", self._name)

        try:
        
            if self._api.available(self._sensor_type):
                self._state = self._api.sensor_data[self._sensor_type]
            else:
                self._state = None

        except KeyError:
            _LOGGER.warning("Problem updating sensors")
