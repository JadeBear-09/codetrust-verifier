from codetrust.weather_dashboard import render_weather_dashboard


def test_weather_dashboard_formats_forecast() -> None:
    assert render_weather_dashboard("Pune", 27.25) == "Pune: 27.2°C · forecast dashboard"


def test_weather_dashboard_handles_blank_city() -> None:
    assert render_weather_dashboard("  ", 18) == "Unknown city: 18.0°C · forecast dashboard"
