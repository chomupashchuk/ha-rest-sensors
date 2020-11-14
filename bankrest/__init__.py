"""Suppoort for REST statistics."""
import logging
import requests
import time
import threading

from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.const import (
    CONF_NAME,
    CONF_SENSORS,
)
from homeassistant.helpers import discovery

from .sensor import (
    SENSORS,
    DATA_REST,
    DEVICES,
    NBU_USD_SENSOR,
    NBU_EUR_SENSOR,
    NBU_EUR_FIRST_SENSOR,
    NBU_USD_FIRST_SENSOR,
    MONOBANK_USD_BID_SENSOR,
    MONOBANK_USD_ASK_SENSOR,
    MONOBANK_EUR_BID_SENSOR,
    MONOBANK_EUR_ASK_SENSOR,
    PRIVATBANK_USD_ASK_SENSOR,
    PRIVATBANK_USD_BID_SENSOR,
    PRIVATBANK_EUR_ASK_SENSOR,
    PRIVATBANK_EUR_BID_SENSOR,
    KREDOBANK_USD_ASK_SENSOR,
    KREDOBANK_USD_BID_SENSOR,
    KREDOBANK_EUR_ASK_SENSOR,
    KREDOBANK_EUR_BID_SENSOR,
)

_LOGGER = logging.getLogger(__name__)

NBU_USD_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json"
NBU_EUR_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=EUR&json"
NBU_EUR_FIRST_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={}01&valcode=EUR&json"
NBU_USD_FIRST_LINK = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={}01&valcode=USD&json"
MONOBANK_LINK = "https://api.monobank.ua/bank/currency"
PRIVATBANK_LINK = "https://api.privatbank.ua/p24api/exchange_rates?json&date={}"
KREDOBANK_LINK = "https://kredobank.com.ua/info/kursy-valyut/commercial"

HTTP_TIMEOUT = 60

SENSOR_LIST = [sensor for sensor in SENSORS]

class BankRestHandler():
    """REST handler"""
    
    def __init__(self, hass, name):
        """Initialize."""
        self._hass = hass
        self._name = name
        self._sensor_data = dict()
        for sensor in SENSOR_LIST:
            self._sensor_data[sensor] = None
        self.timer_periodic_read = None

    def read_data(self):

        self.timer_periodic_read = threading.Timer(600, self.read_data)
        self.timer_periodic_read.start()

        nbu_usd_value = None
        nbu_eur_value = None
        nbu_eur_first_value = None
        nbu_usd_first_value = None
        monobank_eur_ask_value = None
        monobank_eur_bid_value = None
        monobank_usd_ask_value = None
        monobank_usd_bid_value = None
        privatbank_eur_ask_value = None
        privatbank_eur_bid_value = None
        privatbank_usd_ask_value = None
        privatbank_usd_bid_value = None
        kredobank_eur_ask_value = None
        kredobank_eur_bid_value = None
        kredobank_usd_ask_value = None
        kredobank_usd_bid_value = None
        
        session = requests.Session()
        token = requests.auth.HTTPDigestAuth("user", "password")

        try:
            url = NBU_USD_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                nbu_usd_value = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error USD {}".format(ex))
        
        try:
            url = NBU_EUR_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                nbu_eur_value = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error EUR {}".format(ex))
        
        nbu_time = time.strftime('%Y%m')
        
        try:
            url = NBU_USD_FIRST_LINK.format(nbu_time)
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                nbu_usd_first_value = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error USD first {}".format(ex))
        
        try:
            url = NBU_EUR_FIRST_LINK.format(nbu_time)
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                nbu_eur_first_value = resp.json()[0]['rate']
        except Exception as ex:
            _LOGGER.warning("NBU error EUR first {}".format(ex))
        
        try:
            url = MONOBANK_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                monobank_data = resp.json()
                for currency_id in monobank_data:
                    if currency_id['currencyCodeA'] == 840 and currency_id['currencyCodeB'] == 980:
                        monobank_usd_bid_value = currency_id['rateBuy']
                        monobank_usd_ask_value = currency_id['rateSell']
                    elif currency_id['currencyCodeA'] == 978 and currency_id['currencyCodeB'] == 980:
                        monobank_eur_bid_value = currency_id['rateBuy']
                        monobank_eur_ask_value = currency_id['rateSell']
        except Exception as ex:
            _LOGGER.warning("Monobank error {}".format(ex))
        
        privatbank_time = time.strftime('%d.%m.%Y')
        
        try:
            url = PRIVATBANK_LINK.format(privatbank_time)
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                privatbank_data = resp.json()
                for currency_id in privatbank_data['exchangeRate']:
                    if 'currency' in currency_id and 'saleRate' in currency_id and 'purchaseRate' in currency_id:
                        if currency_id['currency'] == 'USD':
                            privatbank_usd_ask_value = currency_id['saleRate']
                            privatbank_usd_bid_value = currency_id['purchaseRate']
                        elif currency_id['currency'] == 'EUR':
                            privatbank_eur_ask_value = currency_id['saleRate']
                            privatbank_eur_bid_value = currency_id['purchaseRate']
        except Exception as ex:
            _LOGGER.warning("Privatbank error {}".format(ex))
                
        try:
            url = KREDOBANK_LINK
            resp = session.get(
                url,
                auth=token,
                verify=True,
                timeout=HTTP_TIMEOUT)
            if resp.ok:
                html_reply = resp.text.splitlines()
                for line_num, line_str in enumerate(resp.text.splitlines()):
                    if '<td>840 USD</td>' in line_str:
                        kredo_ask = int(html_reply[line_num+2][html_reply[line_num+2].find('<td>')+4:html_reply[line_num+2].find('</td>')])/100
                        kredo_bid = int(html_reply[line_num+3][html_reply[line_num+2].find('<td>')+4:html_reply[line_num+2].find('</td>')])/100
                        kredobank_usd_ask_value = kredo_ask
                        kredobank_usd_bid_value = kredo_bid
                    if '<td>978 EUR</td>' in line_str:
                        kredo_ask = int(html_reply[line_num+2][html_reply[line_num+2].find('<td>')+4:html_reply[line_num+2].find('</td>')])/100
                        kredo_bid = int(html_reply[line_num+3][html_reply[line_num+2].find('<td>')+4:html_reply[line_num+2].find('</td>')])/100
                        kredobank_eur_ask_value = kredo_ask
                        kredobank_eur_bid_value = kredo_bid
        
        except Exception as ex:
            _LOGGER.warning("Kredobank error {}".format(ex))
                        
        self._sensor_data[NBU_USD_SENSOR] = nbu_usd_value
        self._sensor_data[NBU_EUR_SENSOR] = nbu_eur_value
        self._sensor_data[NBU_EUR_FIRST_SENSOR] = nbu_eur_first_value
        self._sensor_data[NBU_USD_FIRST_SENSOR] = nbu_usd_first_value
        self._sensor_data[MONOBANK_USD_BID_SENSOR] = monobank_usd_bid_value
        self._sensor_data[MONOBANK_USD_ASK_SENSOR] = monobank_usd_ask_value
        self._sensor_data[MONOBANK_EUR_BID_SENSOR] = monobank_eur_bid_value
        self._sensor_data[MONOBANK_EUR_ASK_SENSOR] = monobank_eur_ask_value
        self._sensor_data[PRIVATBANK_USD_ASK_SENSOR] = privatbank_usd_ask_value
        self._sensor_data[PRIVATBANK_USD_BID_SENSOR] = privatbank_usd_bid_value
        self._sensor_data[PRIVATBANK_EUR_ASK_SENSOR] = privatbank_eur_ask_value
        self._sensor_data[PRIVATBANK_EUR_BID_SENSOR] = privatbank_eur_bid_value
        self._sensor_data[KREDOBANK_USD_ASK_SENSOR] = kredobank_usd_ask_value
        self._sensor_data[KREDOBANK_USD_BID_SENSOR] = kredobank_usd_bid_value
        self._sensor_data[KREDOBANK_EUR_ASK_SENSOR] = kredobank_eur_ask_value
        self._sensor_data[KREDOBANK_EUR_BID_SENSOR] = kredobank_eur_bid_value
        
        return
        
    @property
    def available(self):
        """Return if REST sensors are available."""
        return True
        
    @property
    def sensor_data(self):
        """Return if REST sensors."""
        return self._sensor_data

def setup(hass, config):
    """Set up the REST component."""
    
    hass.data.setdefault(DATA_REST, {DEVICES: {}})
    name = DATA_REST
    sensors = SENSOR_LIST
    try:
        api = BankRestHandler(hass, name=name)
        
        api.timer_periodic_read = threading.Timer(1, api.read_data)
        api.timer_periodic_read.start()
    except:
        _LOGGER.error("unknown error rest")
    hass.data[DATA_REST][DEVICES][name] = BankRestDevice(api)
    if sensors:
        discovery.load_platform(
            hass,
            SENSOR,
            DATA_REST,
            {CONF_NAME: name, CONF_SENSORS: sensors},
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
