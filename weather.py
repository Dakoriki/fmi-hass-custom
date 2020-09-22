"""Support for retrieving meteorological data from FMI (Finnish Meteorological Institute)."""
from dateutil import tz

# Import homeassistant platform dependencies
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    WeatherEntity,
)

from .const import (
    ATTRIBUTION,
    DOMAIN
)

from . import get_weather_symbol


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the FMI weather platform."""
    if discovery_info is None:
        return

    if "data_key" in discovery_info.keys():
        async_add_entities(
            [FMIWeather(DOMAIN, hass.data[DOMAIN][discovery_info["data_key"]])], True
        )


class FMIWeather(WeatherEntity):
    """Representation of a weather condition."""

    def __init__(self, domain, fmi_weather):
        """Initialize FMI weather object."""
        self._fmi = fmi_weather

        self._name = fmi_weather.name

    @property
    def available(self):
        """Return if weather data is available from FMI."""
        if self._fmi is None:
            return False

        return self._fmi.current is not None

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def temperature(self):
        """Return the temperature."""
        if self._fmi is None:
            return None

        return self._fmi.current.data.temperature.value

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        if self._fmi is None:
            return None

        return self._fmi.current.data.temperature.unit

    @property
    def humidity(self):
        """Return the humidity."""
        if self._fmi is None:
            return None

        return self._fmi.current.data.humidity.value

    @property
    def precipitation(self):
        """Return the humidity."""
        if self._fmi is None:
            return None

        return self._fmi.current.data.precipitation_amount.value

    @property
    def wind_speed(self):
        """Return the wind speed."""
        if self._fmi is None:
            return None

        return round(
            self._fmi.current.data.wind_speed.value * 3.6, 1
        )  # Convert m/s to km/hr

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        if self._fmi is None:
            return None

        return self._fmi.current.data.wind_direction.value

    @property
    def pressure(self):
        """Return the pressure."""
        if self._fmi is None:
            return None

        return self._fmi.current.data.pressure.value

    @property
    def condition(self):
        """Return the condition."""
        if self._fmi is None:
            return None

        return get_weather_symbol(self._fmi.current.data.symbol.value, self._fmi.hass)

    @property
    def forecast(self):
        """Return the forecast array."""
        if self._fmi is None:
            return None

        if self._fmi.hourly is None:
            return None

        data = None

        data = [
            {
                ATTR_FORECAST_TIME: forecast.time.astimezone(tz.tzlocal()),
                ATTR_FORECAST_CONDITION: get_weather_symbol(forecast.symbol.value),
                ATTR_FORECAST_TEMP: forecast.temperature.value,
                ATTR_FORECAST_PRECIPITATION: forecast.precipitation_amount.value,
                ATTR_FORECAST_WIND_SPEED: forecast.wind_speed.value,
                ATTR_FORECAST_WIND_BEARING: forecast.wind_direction.value,
                ATTR_WEATHER_PRESSURE: forecast.pressure.value,
                ATTR_WEATHER_HUMIDITY: forecast.humidity.value,
            }
            for forecast in self._fmi.hourly.forecasts
        ]

        return data

    def update(self):
        """Get the latest data from FMI."""
        if self._fmi is None:
            return None

        self._fmi.update()
