# Description
Home Assistant integration which fetches data from Ukrainian banks and creates sensors automatically.
Currently data is being fetched from NBU, Kredobank, Monobank, Privatbank.
It also creates binary sensort for Home Assistant updates (docker and Hassio).

# Sensors updates
To include new sensor/binary_sensor:
- in `sensor.py`/`binary_sensor.py` include new internal sensor name (`SENSOR_`/`BINARY_SENSOR`) and HA friendly name (`NAME_`). Update representation data in `SENSORS`/`BINARY_SENSORS` dictionary.
- in `__init__` include import of new internal sensor name (`SENSOR_`/`BINARY_SENSOR`) and add sensor fething within `read_data` method. Note that if data is not fetched it is preferred to keep state `None` which shall make sensor unavailable.

# Installation
1. Load folder `rest_sensors` into `custom_components`. 

2. Inlcude following line in `configuration.yaml`:
```
rest_sensors:
```

3. Restart Home Assistant
