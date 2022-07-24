from datetime import timedelta, datetime
import logging

import voluptuous as vol

from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA, STATE_CLASS_MEASUREMENT, STATE_CLASS_TOTAL, STATE_CLASS_TOTAL_INCREASING, SensorEntity
from homeassistant.const import (CONF_HOST, CONF_NAME, CONF_MONITORED_CONDITIONS, CONF_SCAN_INTERVAL)
from homeassistant.const import POWER_KILO_WATT, POWER_WATT, ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY, ELECTRIC_CURRENT_AMPERE, ELECTRIC_POTENTIAL_VOLT, DEVICE_CLASS_VOLTAGE, DEVICE_CLASS_CURRENT, TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from hoymiles_modbus.client import HoymilesModbusTCP
from hoymiles_modbus.datatypes import MicroinverterType

from pymodbus.constants import Defaults
Defaults.RetryOnEmpty = True
Defaults.Timeout = 5
Defaults.Retries = 5


CONF_MONITORED_CONDITIONS_PV = "monitored_conditions_pv"
CONF_MICROINVERTERS = "microinverters"
CONF_PANELS = "panels"

_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = 'Hoymiles DTU'
DEFAULT_SCAN_INTERVAL = timedelta(minutes=2)

# opis, jednostka, urzadzenie, klasa, reset, mnoznik, utrzymanie wartosci (0-brak, 1-tak, 2-do polnocy)
SENSOR_TYPES = {
    'pv_power': ['Aktualna moc', POWER_KILO_WATT, DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT, False, 1000, 0],
    'today_production': ['Energia dzisiaj', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING, False, 1000, 2],
    'total_production': ['Energia od początku', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL, False, 1000, 1],
    'alarm_flag': ['Flaga alarmu', ' ', 'alarm_flag', STATE_CLASS_MEASUREMENT, False, 1, 0]
}

PV_TYPES = {
    'pv_voltage': [3, 'Napięcie', ELECTRIC_POTENTIAL_VOLT, DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT, False, 1, 0],
    'pv_current': [4, 'Prąd', ELECTRIC_CURRENT_AMPERE, DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT, False, 1, 0],
    'grid_voltage': [5, 'Napięcie sieci', ELECTRIC_POTENTIAL_VOLT, DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT, False, 1, 0],
    'pv_power': [7, 'Aktualna moc', POWER_WATT, DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT, False, 1, 0],
    'today_production': [8, 'Energia dzisiaj', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING, False, 1000, 2],
    'total_production': [9, 'Energia od początku', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL, False, 1000, 1],
    'temperature': [10, 'Temperatura', TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE, STATE_CLASS_MEASUREMENT, False, 1, 0],
    'operating_status': [11, 'Status', ' ', 'operating_status', STATE_CLASS_MEASUREMENT, False, 1, 0],
    'alarm_code': [12, 'Kod alarmu', ' ', 'alarm_code', STATE_CLASS_MEASUREMENT, False, 1, 0],
    'alarm_count': [13, 'Wystąpienia alarmu', ' ', 'alarm_count', STATE_CLASS_MEASUREMENT, False, 1, 0],
    'link_status': [14, 'Status połączenia', ' ', 'link_status', STATE_CLASS_MEASUREMENT, False, 1, 0]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_MONITORED_CONDITIONS_PV, default=[]):
        vol.All(cv.ensure_list, [vol.In(PV_TYPES)]),
    vol.Optional(CONF_PANELS, default=0): cv.byte,    
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    panels = config.get(CONF_PANELS)
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    updater = HoymilesDTUUpdater(host, scan_interval)
    updater.update()
    if updater.data is None:
        raise Exception('Invalid configuration for Hoymiles DTU platform')
    dev = []
    for variable in config[CONF_MONITORED_CONDITIONS]:
        dev.append(HoymilesDTUSensor(hass, name, variable, panels, updater))
    for variable in config[CONF_MONITORED_CONDITIONS_PV]:
        i = 1
        while i<=panels:
          dev.append(HoymilesPVSensor(name, updater.data.microinverter_data[i-1].serial_number, i, updater.data.microinverter_data[i-1].port_number, variable, updater))
          i+=1
    add_entities(dev, True)

class HoymilesDTUSensor(SensorEntity):
    def __init__(self, hass, name, sensor_type, panels, updater):
        self._hass = hass
        self._client_name = name
        self._type = sensor_type
        self._updater = updater
        self._name = SENSOR_TYPES[sensor_type][0]
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._state_old = 0
        self._panels = panels
        
    @property
    def name(self):
        return '{} {}'.format(self._client_name, self._type)

    @property
    def state(self):
        if self._updater.data is not None and self._updater.data.total_production>0:
            temp = vars(self._updater.data)
            self._state = temp[self._type]/SENSOR_TYPES[self._type][5]
        elif self._updater.data is not None and self._updater.data.total_production==0:
            if SENSOR_TYPES[self._type][6]==0:
                self._state = 0
            elif SENSOR_TYPES[self._type][6]==2 and datetime.now().hour==0:
                self._state = 0
            if self._updater.data is not None and self._type=='total_production':
                i = 1
                licz_total = 0
                while i<=self._panels:
                    temp2 = self._updater.data.microinverter_data[i-1]
                    licz_total = licz_total + temp2[PV_TYPES[self._type][0]]/PV_TYPES[self._type][6]
                    i+=1
                if licz_total>0:
                    self._state = licz_total
            if self._updater.data is not None and self._type=='today_production':
                i = 1
                licz_total = 0
                while i<=self._panels:
                    temp2 = self._updater.data.microinverter_data[i-1]
                    licz_total = licz_total + temp2[PV_TYPES[self._type][0]]/PV_TYPES[self._type][6]
                    i+=1
                if licz_total>0:
                    self._state = licz_total
        if self._state is not None and self._state < self._state_old and self._type=='total_production':
            self._state = self._state_old
        elif self._state is not None and self._state > self._state_old and self._type=='total_production':
            self._state_old = self._state
        return self._state
        

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
			
    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    def update(self):
        self._updater.update()

class HoymilesPVSensor(SensorEntity):
    def __init__(self, name, serial_number, panel_number, panel, sensor_type, updater):
        self._client_name = name +' '+ serial_number +' PV '+str(panel)
        self._serial_number = serial_number
        self._panel_number = panel_number
        self._panel = panel
        self._type = sensor_type
        self._updater = updater
        self._name = PV_TYPES[sensor_type][1]
        self._state = None
        self._unit_of_measurement = PV_TYPES[sensor_type][2]

    @property
    def name(self):
        return '{} {}'.format(self._client_name, self._type)

    @property
    def state(self):
        if self._updater.data is not None and self._updater.data.total_production>0:
            temp = self._updater.data.microinverter_data[self._panel_number-1]
            self._state = temp[PV_TYPES[self._type][0]]/PV_TYPES[self._type][6]
        elif self._updater.data is not None and self._updater.data.total_production==0:
            if PV_TYPES[self._type][7]==0:
                self._state = 0
            elif PV_TYPES[self._type][7]==2 and datetime.now().hour==0:
                self._state = 0
        return self._state

    @property
    def device_class(self):
        return PV_TYPES[self._type][3]

    @property
    def state_class(self):
        return PV_TYPES[self._type][4]

    @property
    def last_reset(self):
        if PV_TYPES[self._type][5]:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

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
          self.data = plant_data
        except:
          self.data = None
