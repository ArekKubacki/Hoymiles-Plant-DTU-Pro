from datetime import timedelta, datetime
import logging

import voluptuous as vol

from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA, STATE_CLASS_MEASUREMENT, STATE_CLASS_TOTAL_INCREASING, SensorEntity
from homeassistant.const import (CONF_HOST, CONF_NAME, CONF_MONITORED_CONDITIONS, CONF_SCAN_INTERVAL)
#from homeassistant.components.sensor import  STATE_CLASS_MEASUREMENT, STATE_CLASS_TOTAL_INCREASING, SensorEntity, SensorEntityDescription
from homeassistant.const import POWER_KILO_WATT, ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY
#from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from hoymiles_modbus.client import HoymilesModbusTCP
from hoymiles_modbus.datatypes import MicroinverterType

#DEPENDENCIES = ['hoymiles_dtu']
_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = 'Hoymiles DTU'
DEFAULT_SCAN_INTERVAL = timedelta(minutes=2)
#ENERGY_SENSORS = [
#    SensorEntityDescription(
#        key="power",
#        native_unit_of_measurement=POWER_WATT,
#        device_class=DEVICE_CLASS_POWER,
#        state_class=STATE_CLASS_MEASUREMENT,
#        name="Current Consumption",
#    ),
#    SensorEntityDescription(
#        key="energy",
#        native_unit_of_measurement=ENERGY_WATT_HOUR,
#        device_class=DEVICE_CLASS_ENERGY,
#        state_class=STATE_CLASS_TOTAL_INCREASING,
#        name="Total Consumption",
#    )
#]

SENSOR_TYPES = {
    'pv_power': ['Aktualna moc', POWER_KILO_WATT, DEVICE_CLASS_ENERGY, STATE_CLASS_MEASUREMENT, False],
    'today_production': ['Energia dzisiaj', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING, True],
    'total_production': ['Energia od początku', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING, False]
}
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period
})

data_DTU = {
    'pv_power': None,
    'today_production': None,
    'total_production': None
}



def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    updater = HoymilesDTUUpdater(host, scan_interval)
    updater.update()
    if updater.data is None:
        raise Exception('Invalid configuration for Hoymiles DTU platform')
    dev = []
    for variable in config[CONF_MONITORED_CONDITIONS]:
        dev.append(HoymilesDTUSensor(name, variable, updater))
    add_entities(dev, True)

class HoymilesDTUSensor(SensorEntity):
    def __init__(self, name, sensor_type, updater):
        self._client_name = name
        self._type = sensor_type
        self._updater = updater
        self._name = SENSOR_TYPES[sensor_type][0]
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
#        self._attr_state_class = STATE_CLASS_TOTAL_INCREASING #SENSOR_TYPES[sensor_type][3]

    @property
    def name(self):
        return '{} {}'.format(self._client_name, self._type)

    @property
    def state(self):
        if self._updater.data is not None:
            self._state = self._updater.data[self._type]
        return self._state

#    @property
#    def extra_state_attributes(self):
#        output = dict()
#        if self._updater.data is not None:
#            for sensor_type in SENSOR_TYPES:
#                output[SENSOR_TYPES[sensor_type][0]] = self._updater.data[sensor_type]
#                if SENSOR_TYPES[sensor_type][1] is not None:
#                    output[SENSOR_TYPES[sensor_type][0]] = str(output[SENSOR_TYPES[sensor_type][0]]) + ' ' + SENSOR_TYPES[sensor_type][1]
#        return output

    @property
    def device_class(self):
        return SENSOR_TYPES[self._type][2]

    @property
    def state_class(self):
        return SENSOR_TYPES[self._type][3]

    @property
    def last_reset(self):
        if SENSOR_TYPES[self._type][4]:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not SENSOR_TYPES[self._type][4]:
            return datetime.now().replace(year = 1970, month = 1, day = 1, hour=0, minute=0, second=0, microsecond=0)

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    def update(self):
        self._updater.update()


class HoymilesDTUUpdater:
    def __init__(self, host, scan_interval):
        self.host = host
        self.update = Throttle(scan_interval)(self._update)
        self.data = None

    def _update(self):
        try:
          plant_data = HoymilesModbusTCP(self.host, microinverter_type=MicroinverterType.HM).plant_data
          data_DTU['pv_power'] = plant_data.pv_power/1000
          data_DTU['today_production'] = plant_data.today_production/1000
          data_DTU['total_production'] = plant_data.total_production/1000
          self.data = data_DTU
        except:
          self.data = None
