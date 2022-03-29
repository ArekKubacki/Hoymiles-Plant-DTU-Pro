[![HACS Custom][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]
[![Buy me a coffee][buy_me_a_coffee_shield]][buy_me_a_coffee]
[![PayPal.Me][paypal_me_shield]][paypal_me]


[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Custom&style=popout&color=orange&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/faq/custom_repositories

[latest_release]: https://github.com/Arek1990/Hoymiles-Plant-DTU-Pro/releases/latest
[releases_shield]: https://img.shields.io/github/release/Arek1990/Hoymiles-Plant-DTU-Pro.svg?style=popout

[releases]: https://github.com/Arek1990/Hoymiles-Plant-DTU-Pro/releases
[downloads_total_shield]: https://img.shields.io/github/downloads/Arek1990/Hoymiles-Plant-DTU-Pro/total

[buy_me_a_coffee_shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy_me_a_coffee]: https://www.buymeacoffee.com/PiotrMachowski

[paypal_me_shield]: https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal
[paypal_me]: https://paypal.me/PiMachowski

# Froggy Sensor

This custom integration retrieves opening status of [Żabka shops](https://www.zabka.pl/).


![example](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Froggy/blob/master/example.png)

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

This integration can be added to HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories):
* URL: `https://github.com/PiotrMachowski/Home-Assistant-custom-components-Froggy`
* Category: `Integration`

After adding a custom repository you can use HACS to install this integration using user interface.

### Manual

To install this integration manually you have to download [*froggy.zip*](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Froggy/releases/latest/download/froggy.zip) and extract its contents to `config/custom_components/froggy` directory:
```bash
mkdir -p custom_components/froggy
cd custom_components/froggy
wget https://github.com/PiotrMachowski/Home-Assistant-custom-components-Froggy/releases/latest/download/froggy.zip
unzip froggy.zip
rm froggy.zip
```

## Configuration

| Key | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | `False` | `Froggy` | Prefix for sensor ids |
| `latitude` | `float` | `False` | Latitude of home | Latitude of point of reference |
| `longitude` | `float` | `False` | Longitude of home | Longitude of of reference |
| `shop_ids` | `list` | `False` | - | List of monitored shop ids ([retrieving id](#retrieving-shop-id)) |

### Example configuration

#### Minimal version - retrieves data for the closest shop

```yaml
binary_sensor:
  - platform: froggy
```

#### Selected list of shops
```yaml
binary_sensor:
  - platform: froggy
    shop_ids:
      - ID02786
      - ID07971  
```

### Retrieving shop id
1. Go to [Lokalizator](https://www.zabka.pl/znajdz-sklep)
1. Find the store
1. Double-click on pin
1. Shop id will be visible in URL address:
   
    `https://www.zabka.pl/znajdz-sklep/sklep/ID02786,ustrzyki-dolne-ul-rynek-25-u2`

<a href="https://www.buymeacoffee.com/PiotrMachowski" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
<a href="https://paypal.me/PiMachowski" target="_blank"><img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg" border="0" alt="PayPal Logo" style="height: auto !important;width: auto !important;"></a>
