"""Suppoort for rest sensors."""
import logging
from datetime import timedelta

from homeassistant.const import CONF_NAME, CONF_SENSORS
from homeassistant.helpers.entity import Entity

# Internal component sensor names
NBU_USD_SENSOR = "currency_usd"
NBU_EUR_SENSOR = "currency_eur"
NBU_EUR_FIRST_SENSOR = "currency_eur_beginning"
NBU_USD_FIRST_SENSOR = "currency_usd_beginning"
MONOBANK_USD_BID_SENSOR = "monobank_usd_bid"
MONOBANK_USD_ASK_SENSOR = "monobank_usd_ask"
MONOBANK_EUR_BID_SENSOR = "monobank_eur_bid"
MONOBANK_EUR_ASK_SENSOR = "monobank_eur_ask"
PRIVATBANK_USD_ASK_SENSOR = "privatbank_usd_ask"
PRIVATBANK_USD_BID_SENSOR = "privatbank_usd_bid"
PRIVATBANK_EUR_ASK_SENSOR = "privatbank_eur_ask"
PRIVATBANK_EUR_BID_SENSOR = "privatbank_eur_bid"
KREDOBANK_USD_ASK_SENSOR = "kredobank_usd_ask"
KREDOBANK_USD_BID_SENSOR = "kredobank_usd_bid"
KREDOBANK_EUR_ASK_SENSOR = "kredobank_eur_ask"
KREDOBANK_EUR_BID_SENSOR = "kredobank_eur_bid"

# Home Assistant names
NBU_USD_NAME = "Currency USD NBU"
NBU_EUR_NAME = "Currency EUR NBU"
NBU_EUR_FIRST_NAME = "Currency EUR NBU First Day"
NBU_USD_FIRST_NAME = "Currency USD NBU First Day"
MONOBANK_USD_BID_NAME = "Currency USD Monobank Bid"
MONOBANK_USD_ASK_NAME = "Currency USD Monobank Ask"
MONOBANK_EUR_BID_NAME = "Currency EUR Monobank Bid"
MONOBANK_EUR_ASK_NAME = "Currency EUR Monobank Ask"
PRIVATBANK_USD_ASK_NAME = "Currency USD Privatbank Ask"
PRIVATBANK_USD_BID_NAME = "Currency USD Privatbank Bid"
PRIVATBANK_EUR_ASK_NAME = "Currency EUR Privatbank Ask"
PRIVATBANK_EUR_BID_NAME = "Currency EUR Privatbank Bid"
KREDOBANK_USD_ASK_NAME = "Currency USD Kredobank Ask"
KREDOBANK_USD_BID_NAME = "Currency USD Kredobank Bid"
KREDOBANK_EUR_ASK_NAME = "Currency EUR Kredobank Ask"
KREDOBANK_EUR_BID_NAME = "Currency EUR Kredobank Bid"

DATA_REST = "bankrest"
DEVICES = "devices"

UNITS = 'rate'
ICON_EUR = 'mdi:currency-eur'
ICON_USD = 'mdi:currency-usd'

SENSOR_SCAN_INTERVAL_SECS = 5
SCAN_INTERVAL = timedelta(seconds=SENSOR_SCAN_INTERVAL_SECS)

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined like: Name, units, icon
SENSORS = {
    NBU_USD_SENSOR: [NBU_USD_NAME, UNITS, ICON_USD],
    NBU_EUR_SENSOR: [NBU_EUR_NAME, UNITS, ICON_EUR],
    NBU_EUR_FIRST_SENSOR: [NBU_EUR_FIRST_NAME, UNITS, ICON_EUR],
    NBU_USD_FIRST_SENSOR: [NBU_USD_FIRST_NAME, UNITS, ICON_USD],
    MONOBANK_USD_BID_SENSOR: [MONOBANK_USD_BID_NAME, UNITS, ICON_USD],
    MONOBANK_USD_ASK_SENSOR: [MONOBANK_USD_ASK_NAME, UNITS, ICON_USD],
    MONOBANK_EUR_BID_SENSOR: [MONOBANK_EUR_BID_NAME, UNITS, ICON_EUR],
    MONOBANK_EUR_ASK_SENSOR: [MONOBANK_EUR_ASK_NAME, UNITS, ICON_EUR],
    PRIVATBANK_USD_ASK_SENSOR: [PRIVATBANK_USD_ASK_NAME, UNITS, ICON_USD],
    PRIVATBANK_USD_BID_SENSOR: [PRIVATBANK_USD_BID_NAME, UNITS, ICON_USD],
    PRIVATBANK_EUR_ASK_SENSOR: [PRIVATBANK_EUR_ASK_NAME, UNITS, ICON_EUR],
    PRIVATBANK_EUR_BID_SENSOR: [PRIVATBANK_EUR_BID_NAME, UNITS, ICON_EUR],
    KREDOBANK_USD_ASK_SENSOR: [KREDOBANK_USD_ASK_NAME, UNITS, ICON_USD],
    KREDOBANK_USD_BID_SENSOR: [KREDOBANK_USD_BID_NAME, UNITS, ICON_USD],
    KREDOBANK_EUR_ASK_SENSOR: [KREDOBANK_EUR_ASK_NAME, UNITS, ICON_EUR],
    KREDOBANK_EUR_BID_SENSOR: [KREDOBANK_EUR_BID_NAME, UNITS, ICON_EUR],
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
    def state(self):
        """Return the state of the sensor."""
        return self._state

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
        return True

    def update(self):
        """Get the latest data and updates the state."""
        if not self.available:
            return
        _LOGGER.debug("Updating %s sensor", self._name)

        try:
        
            if self._sensor_type in SENSORS:
                self._state = self._api.sensor_data[self._sensor_type]

        except KeyError:
            _LOGGER.warning("Problem updating sensors for Ariston")
