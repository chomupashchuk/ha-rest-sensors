"""Suppoort for REST statistics."""
import logging
import requests
import time
import threading
import re

from homeassistant.components.sensor import DOMAIN as COMP_SENSOR
from homeassistant.components.binary_sensor import DOMAIN as COMP_BINARY_SENSOR
from homeassistant.const import (
    CONF_NAME,
    CONF_SENSORS,
    CONF_BINARY_SENSORS,
)
from homeassistant.helpers import discovery
from homeassistant.const import __version__ as LOCAL_VERSION

from .sensor import (
    SENSORS,
    DATA_REST,
    DEVICES,
    SENSOR_NBU_USD,
    SENSOR_NBU_EUR,
    SENSOR_NBU_EUR_FIRST,
    SENSOR_NBU_USD_FIRST,
    SENSOR_MONOBANK_USD_BID,
    SENSOR_MONOBANK_USD_ASK,
    SENSOR_MONOBANK_EUR_BID,
    SENSOR_MONOBANK_EUR_ASK,
    SENSOR_PRIVATBANK_USD_ASK,
    SENSOR_PRIVATBANK_USD_BID,
    SENSOR_PRIVATBANK_EUR_ASK,
    SENSOR_PRIVATBANK_EUR_BID,
    SENSOR_KREDOBANK_USD_ASK,
    SENSOR_KREDOBANK_USD_BID,
    SENSOR_KREDOBANK_EUR_ASK,
    SENSOR_KREDOBANK_EUR_BID,
)
from .binary_sensor import (
    BINARY_SENSORS,
    BINARY_SENSOR_UPDATE_DOCKER,
    BINARY_SENSOR_UPDATE_HASSIO,
)

_LOGGER = logging.getLogger(__name__)

NBU_USD_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json"
NBU_EUR_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=EUR&json"
NBU_EUR_FIRST_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={}01&valcode=EUR&json"
NBU_USD_FIRST_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={}01&valcode=USD&json"
MONOBANK_LINK = "https://api.monobank.ua/bank/currency"
PRIVATBANK_LINK = "https://api.privatbank.ua/p24api/exchange_rates?json&date={}"
KREDOBANK_LINK = "https://kredobank.com.ua/info/kursy-valyut/commercial"
# DOCKER_LINK = "https://registry.hub.docker.com/v2/repositories/homeassistant/home-assistant/tags/?page_size=100"
HASSIO_LINK = "https://version.home-assistant.io/stable.json"

HTTP_TIMEOUT = 60

SENSOR_LIST = [sensor for sensor in SENSORS]
BINARY_SENSOR_LIST = [sensor for sensor in BINARY_SENSORS]

for sensor in SENSOR_LIST:
    if sensor in BINARY_SENSOR_LIST:
        raise Exception(sensor)

class BankRestHandler():
    """REST handler"""
    
    def __init__(self, hass, name):
        """Initialize."""
        self._hass = hass
        self._name = name
        self._sensor_data = dict()
        self._sensor_attrib = dict()
        for sensor in SENSOR_LIST + BINARY_SENSOR_LIST:
            self._sensor_data[sensor] = None
            self._sensor_attrib[sensor] = None
        self.timer_periodic_read = None

    def read_data(self):

        self.timer_periodic_read = threading.Timer(600, self.read_data)
        self.timer_periodic_read.start()

        session = requests.Session()
        token = requests.auth.HTTPDigestAuth("user", "password")

        # NBU USD current day
        currency = None
        try:
            url = NBU_USD_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                currency = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error USD {}".format(ex))
        
        self._sensor_data[SENSOR_NBU_USD] = currency
        
        # NBU EURO current day
        
        currency = None
        try:
            url = NBU_EUR_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                currency = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error EUR {}".format(ex))
            
        self._sensor_data[SENSOR_NBU_EUR] = currency
                
        # NBU USD first day of the month
                
        currency = None
        try:
            url = NBU_USD_FIRST_LINK.format(time.strftime('%Y%m'))
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                currency = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error USD first {}".format(ex))
        
        self._sensor_data[SENSOR_NBU_USD_FIRST] = currency
        
        # NBU EURO first day of the month
                
        currency = None
        try:
            url = NBU_EUR_FIRST_LINK.format(time.strftime('%Y%m'))
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                currency = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error EUR first {}".format(ex))
        
        self._sensor_data[SENSOR_NBU_EUR_FIRST] = currency
        
        
        # Monobank current day
        
        currency_usd_ask = None
        currency_usd_bid = None
        currency_eur_ask = None
        currency_eur_bid = None
        try:
            url = MONOBANK_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                json_data = resp.json()
                for currency_id in json_data:
                    if currency_id['currencyCodeA'] == 840 and currency_id['currencyCodeB'] == 980:
                        currency_usd_bid = currency_id['rateBuy']
                        currency_usd_ask = currency_id['rateSell']
                    elif currency_id['currencyCodeA'] == 978 and currency_id['currencyCodeB'] == 980:
                        currency_eur_bid = currency_id['rateBuy']
                        currency_eur_ask = currency_id['rateSell']
        except Exception as ex:
            _LOGGER.warning("Monobank error {}".format(ex))
        
        self._sensor_data[SENSOR_MONOBANK_USD_BID] = currency_usd_bid
        self._sensor_data[SENSOR_MONOBANK_USD_ASK] = currency_usd_ask
        self._sensor_data[SENSOR_MONOBANK_EUR_BID] = currency_eur_bid
        self._sensor_data[SENSOR_MONOBANK_EUR_ASK] = currency_eur_ask
        
        # Privatbank current day
        
        currency_usd_ask = None
        currency_usd_bid = None
        currency_eur_ask = None
        currency_eur_bid = None
        try:
            url = PRIVATBANK_LINK.format(time.strftime('%d.%m.%Y'))
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                json_data = resp.json()
                for currency_id in json_data['exchangeRate']:
                    if 'currency' in currency_id and 'saleRate' in currency_id and 'purchaseRate' in currency_id:
                        if currency_id['currency'] == 'USD':
                            currency_usd_ask = currency_id['saleRate']
                            currency_usd_bid = currency_id['purchaseRate']
                        elif currency_id['currency'] == 'EUR':
                            currency_eur_ask = currency_id['saleRate']
                            currency_eur_bid = currency_id['purchaseRate']
        except Exception as ex:
            _LOGGER.warning("Privatbank error {}".format(ex))
                                        
        self._sensor_data[SENSOR_PRIVATBANK_USD_ASK] = currency_usd_ask
        self._sensor_data[SENSOR_PRIVATBANK_USD_BID] = currency_usd_bid
        self._sensor_data[SENSOR_PRIVATBANK_EUR_ASK] = currency_eur_ask
        self._sensor_data[SENSOR_PRIVATBANK_EUR_BID] = currency_eur_bid
        
        # Kredobank current day
        
        currency_usd_ask = None
        currency_usd_bid = None
        currency_eur_ask = None
        currency_eur_bid = None
        try:
            url = KREDOBANK_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                html_data = resp.text.splitlines()
                for line_num, line_str in enumerate(resp.text.splitlines()):
                    if '<td>840 USD</td>' in line_str:
                        kredo_ask = int(html_data[line_num+2][html_data[line_num+2].find('<td>')+4:html_data[line_num+2].find('</td>')])/100
                        kredo_bid = int(html_data[line_num+3][html_data[line_num+2].find('<td>')+4:html_data[line_num+2].find('</td>')])/100
                        currency_usd_ask = kredo_ask
                        currency_usd_bid = kredo_bid
                    if '<td>978 EUR</td>' in line_str:
                        kredo_ask = int(html_data[line_num+2][html_data[line_num+2].find('<td>')+4:html_data[line_num+2].find('</td>')])/100
                        kredo_bid = int(html_data[line_num+3][html_data[line_num+2].find('<td>')+4:html_data[line_num+2].find('</td>')])/100
                        currency_eur_ask = kredo_ask
                        currency_eur_bid = kredo_bid
        
        except Exception as ex:
            _LOGGER.warning("Kredobank error {}".format(ex))
                
        self._sensor_data[SENSOR_KREDOBANK_USD_ASK] = currency_usd_ask
        self._sensor_data[SENSOR_KREDOBANK_USD_BID] = currency_usd_bid
        self._sensor_data[SENSOR_KREDOBANK_EUR_ASK] = currency_eur_ask
        self._sensor_data[SENSOR_KREDOBANK_EUR_BID] = currency_eur_bid
         
        # # Docker version
        
        # online_ver = None
        # update = None
        # major_update = None
        # try:
        #     url = DOCKER_LINK
        #     resp = session.get(
        #         url,
        #         auth=token,
        #         verify=True,
        #         timeout=HTTP_TIMEOUT)
        #     if resp.ok:
        #         json_data = resp.json()
                
        #         for tag in json_data["results"]:
        #             if tag["name"] in [
        #                 "latest",
        #                 "landingpage",
        #                 "rc",
        #                 "beta",
        #                 "stable",
        #             ]:
        #                 continue
        #             elif "dev" in tag["name"]:
        #                 continue
        #             elif re.search(r"\b.+b\d", tag["name"]):
        #                 continue
        #             else:
        #                 online_ver = tag["name"]
        #                 break
                
        #         update, major_update = self._check_update(online_ver)
                
        # except Exception as ex:
        #     _LOGGER.warning("Remote version error {}".format(ex))
                   
        # self._sensor_data[BINARY_SENSOR_UPDATE_DOCKER] = update
        # self._sensor_attrib[BINARY_SENSOR_UPDATE_DOCKER] = dict()
        # self._sensor_attrib[BINARY_SENSOR_UPDATE_DOCKER]["Installed"] = LOCAL_VERSION
        # self._sensor_attrib[BINARY_SENSOR_UPDATE_DOCKER]["Online"] = online_ver
        # self._sensor_attrib[BINARY_SENSOR_UPDATE_DOCKER]["Major"] = major_update
             
        # Hassio version
        
        online_ver = None
        update = None
        major_update = None
        try:
            url = HASSIO_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                online_ver = resp.json()["homeassistant"]["default"]
                update, major_update = self._check_update(online_ver)
                
        except Exception as ex:
            _LOGGER.warning("Remote version error {}".format(ex))
                   
        self._sensor_data[BINARY_SENSOR_UPDATE_HASSIO] = update
        self._sensor_attrib[BINARY_SENSOR_UPDATE_HASSIO] = dict()
        self._sensor_attrib[BINARY_SENSOR_UPDATE_HASSIO]["Installed"] = LOCAL_VERSION
        self._sensor_attrib[BINARY_SENSOR_UPDATE_HASSIO]["Online"] = online_ver
        self._sensor_attrib[BINARY_SENSOR_UPDATE_HASSIO]["Major"] = major_update
             
        return
        
    @staticmethod
    def _check_update(online_ver):
        """Check if update is avaialable"""
        update = None
        major_update = None
        if LOCAL_VERSION and online_ver:
            online_part = online_ver.split(".")
            installed_part = LOCAL_VERSION.split(".")
            if online_ver == LOCAL_VERSION:
                update = False
                major_update = False
            for item in range(min(len(online_part), len(installed_part))):
                if online_part[item].isnumeric() and installed_part[item].isnumeric():
                    if int(online_part[item]) > int(installed_part[item]):
                        update = True
                        if item < min(len(online_part), len(installed_part)) - 1:
                            major_update = True
                        else:
                            major_update = False
                        break
            if not update and len(online_part) > len(installed_part):
                update = True
                major_update = False
        return update, major_update
                    
    def available(self, sensor):
        """Return if REST sensors are available."""
        return self._sensor_data.get(sensor, None) is not None
        
    @property
    def sensor_data(self):
        """Return if REST sensors."""
        return self._sensor_data

def setup(hass, config):
    """Set up the REST component."""
    
    hass.data.setdefault(DATA_REST, {DEVICES: {}})
    name = DATA_REST
    sensors = SENSOR_LIST
    binary_sensors = BINARY_SENSOR_LIST
    try:
        api = BankRestHandler(hass, name=name)
        
        api.timer_periodic_read = threading.Timer(1, api.read_data)
        api.timer_periodic_read.start()
    except Exception as ex:
        _LOGGER.error("unknown error rest {}".format(ex))
    hass.data[DATA_REST][DEVICES][name] = BankRestDevice(api)
    if sensors:
        discovery.load_platform(
            hass,
            COMP_SENSOR,
            DATA_REST,
            {CONF_NAME: name, CONF_SENSORS: sensors},
            config
        )
    if binary_sensors:
        discovery.load_platform(
            hass,
            COMP_BINARY_SENSOR,
            DATA_REST,
            {CONF_NAME: name, CONF_BINARY_SENSORS: binary_sensors},
            config
        )
    if not hass.data[DATA_REST][DEVICES]:
        return False
        
    # Return boolean to indicate that initialization was successful.
    return True


class BankRestDevice:
    """Representation of a base REST discovery device."""

    def __init__(
            self,
            api,
    ):
        """Initialize the entity."""
        self.api = api
