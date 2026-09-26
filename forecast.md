# OpenMeteo

https://open-meteo.com/en/docs

Geolocation : 
https://geocoding-api.open-meteo.com/v1/search?name=Paris,France&language=en&count=1&format=json

Forecast
https://api.open-meteo.com/v1/forecast?latitude=48.8534&longitude=2.3488&temperature_unit=celsius&wind_speed_unit=ms&precipitation_unit=mm&timezone=auto&start_hour=2026-09-26T03%3A00%3A00&end_hour=2026-10-01T23%3A59%3A59&hourly=temperature_2m_min%2Ctemperature_2m_max%2Ccloud_cover%2Csnowfall%2Cprecipitation_probability%2Crain%2Cweather_code&temporal_resolution=hourly_6


# WeatherUnderground

# AccuWeather
Go to https://developer.accuweather.com/, create an account.
NOT FREE

# OpenWeatherMap
Go to https://home.openweathermap.org/
Then into API keys

Geolocation :
curl -s "http://api.openweathermap.org/geo/1.0/direct?q=Paris,France&limit=1&appid=$APIKEY"

Forecast :
https://openweathermap.org/api/forecast5?collection=current_forecast
curl -s "https://api.openweathermap.org/data/2.5/forecast?lat=48.8566&lon=2.3522&units=metric&appid=$APIKEY"