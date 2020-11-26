# Description
Home Assistant integration which fetches data from Ukrainian banks and creates sensors automatically.
Currently data is being fetched from NBU, Kredobank, Monobank, Privatbank.
It also creates binary sensort for Home Assistant updates (docker and Hassio), which includes attributes for installed and online versions and indication if it is a major update.
The reason for this integration is more flexibility with more complex REST sensors. Templates can get really complex in order to parse the data (for example in Privatbank specific currency must be found within the loop, but during scanning some entries do not have all required keys that results in unstable results).

# Sensors updates
To include new sensor/binary_sensor:
- in `sensor.py`/`binary_sensor.py` include new internal sensor name (`SENSOR_`/`BINARY_SENSOR`) and HA friendly name (`NAME_`). Include new sensor representation data in `SENSORS`/`BINARY_SENSORS` dictionary.
- in `__init__` include import of new internal sensor name (`SENSOR_`/`BINARY_SENSOR`) and add sensor fething within `read_data` method and storing of data under `_sensor_data` dictionary with internal sensor name as a key. Note that if data is not fetched it is preferred to keep the state as `None`, which shall force sensor to be unavailable.
- attributes of a sensor can be included in `_sensor_attrib` dictionary.

# Installation
1. Load folder `rest_sensors` into `custom_components`. 

2. Inlcude following line in `configuration.yaml`:
```
rest_sensors:
```

3. Restart Home Assistant
