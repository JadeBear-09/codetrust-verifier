"""Unrelated weather feature used to demonstrate CodeTrust scope rejection."""

from __future__ import annotations


def render_weather_dashboard(city: str, temperature_c: float) -> str:
    """Render a compact weather forecast dashboard card."""
    safe_city = city.strip() or "Unknown city"
    return f"{safe_city}: {temperature_c:.1f}°C · forecast dashboard"
