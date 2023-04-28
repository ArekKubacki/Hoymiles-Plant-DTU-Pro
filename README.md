[![HACS Custom][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]
[![Buy me a coffee][buy_me_a_coffee_shield]][buy_me_a_coffee]
[![PayPal.Me][paypal_me_shield]][paypal_me]


[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Custom&style=popout&color=orange&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/faq/custom_repositories

[latest_release]: https://github.com/ArekKubacki/Hoymiles-Plant-DTU-Pro/releases/latest
[releases_shield]: https://img.shields.io/github/release/ArekKubacki/Hoymiles-Plant-DTU-Pro.svg?style=popout

[releases]: https://github.com/ArekKubacki/Hoymiles-Plant-DTU-Pro/releases
[downloads_total_shield]: https://img.shields.io/github/downloads/ArekKubacki/Hoymiles-Plant-DTU-Pro/total

[buy_me_a_coffee_shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy_me_a_coffee]: https://www.buymeacoffee.com/ArekKubacki

[paypal_me_shield]: https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal
[paypal_me]: https://paypal.me/ArekKubacki

# Hoymiles Plant DTU-Pro Sensor

This integration retrieves data from Hoymiles DTU-Pro using Modbus TCP do Home Assistant


![example](https://github.com/ArekKubacki/Hoymiles-Plant-DTU-Pro/blob/main/images/pv.png)

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

This integration can be added to HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories):
* URL: `https://github.com/ArekKubacki/Hoymiles-Plant-DTU-Pro`
* Category: `Integration`

After adding a custom repository you can use HACS to install this integration using user interface.

### Manual

To install this integration manually you have to download [*hoymiles_dtu.zip*](https://github.com/ArekKubacki/Hoymiles-Plant-DTU-Pro/releases/latest/download/hoymiles_dtu.zip) and extract its contents to `config/custom_components/hoymiles_dtu` directory:
```bash
mkdir -p custom_components/hoymiles_dtu
cd custom_components/hoymiles_dtu
wget https://github.com/ArekKubacki/Hoymiles-Plant-DTU-Pro/releases/latest/download/hoymiles_dtu.zip
unzip hoymiles_dtu.zip
rm hoymiles_dtu.zip
```

## Configuration options

| Key | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | `False` | `Hoymiles PV` | Name of sensor |
| `host` | `string` | `True` | - | Local DTU-Pro host |
| `dtu_type` | `int` | `False` | 0 | 0 - Hoymiles DTU, 1 - OpenDTU |
| `monitored_conditions` | `list` | `True` | - | List of conditions to monitor |
| `monitored_conditions_pv` | `list` | `True` | - | List of conditions for pv to monitor |
| `panels` | `float` | `True` | - | Number of PV panels |
| `scan_interval` | `time period` | `False` | `00:02:00` | Interval between sensor updates |

### Possible monitored conditions

| Key | Description |
| --- | --- | 
| `pv_power` | The current power of the photovoltaic power plant |
| `today_production` | Production of a photovoltaic power plant today |
| `total_production` | Total production of a photovoltaic power plant |
| `alarm_flag` | Alarm flag of a photovoltaic power plant |

### Possible PV monitored conditions

| Key | Description |
| --- | --- | 
| `pv_power` | The current power of the photovoltaic panel |
| `today_production` | Production of a photovoltaic panel today |
| `total_production` | Total production of a photovoltaic panel plant |
| `pv_voltage` | The current voltage of the photovoltaic panel |
| `pv_current` | The current current of the photovoltaic panel |
| `grid_voltage` | The current voltage of the electricity grid |
| `grid_frequency` | The current frequency of the electricity grid |
| `temperature` | The temperature of a photovoltaic panel plant |
| `operating_status` | The operating status of a photovoltaic panel plant |
| `alarm_code` | The alarm code of a photovoltaic panel plant |
| `alarm_count` | The alarm count of a photovoltaic panel plant |
| `link_status` | The link status of a photovoltaic panel plant |

### Example configuration

```yaml
sensor:
  - platform: hoymiles_dtu
    host: 192.168.x.xxx
    name: Hoymiles PV
    dtu_type: 0
    monitored_conditions:
      - 'pv_power'
      - 'today_production'
      - 'total_production'
      - 'alarm_flag'
    monitored_conditions_pv:
      - 'pv_power'
      - 'today_production'
      - 'total_production'
      - 'pv_voltage'
      - 'pv_current'
      - 'grid_voltage'
      - 'temperature'
      - 'operating_status'
      - 'alarm_code'
      - 'alarm_count'
      - 'link_status'
    panels: 16
```

### Dashboard example

This example needs custom:bar-card form HACS

```
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: custom:bar-card
        direction: up
        rounding: 5px
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 6.4
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv_pv_power
      - type: vertical-stack
        cards:
          - type: sensor
            entity: sensor.hoymiles_pv_today_production
            name: Today
            hold_action: more-info
          - type: sensor
            entity: sensor.hoymiles_pv_total_production
            name: Total
            hold_action: more-info
  - type: horizontal-stack
    cards:
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_4_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_1_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_3_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_4_pv_power
  - type: horizontal-stack
    cards:
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_3_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_2_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_1_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_2_pv_power
  - type: horizontal-stack
    cards:
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_4_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_1_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_3_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_4_pv_power
  - type: horizontal-stack
    cards:
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_3_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_2_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_1_pv_power
      - type: custom:bar-card
        direction: up
        rounding: 5px
        height: 100
        positions:
          icon: 'off'
          indicator: 'off'
          name: none
        style:
          top: 0%
          left: 0%
          transform: none
          overflow: hidden
          border-radius: 8px
          width: 100%
          '--paper-card-background-color': rgba(84, 95, 108, 0.7)
        min: 0
        max: 400
        saturation: 50%
        stack: horizontal
        entities:
          - entity: sensor.hoymiles_pv__pv_2_pv_power
```


<a href="https://www.buymeacoffee.com/ArekKubacki" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
<a href="https://paypal.me/ArekKubacki" target="_blank"><img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg" border="0" alt="PayPal Logo" style="height: auto !important;width: auto !important;"></a>
