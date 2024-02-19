import asyncio
import gc
from time import time
from unittest.mock import Mock

import pytest

import toga
from toga.style import Pack

from .properties import (  # noqa: F401
    test_flex_widget_size,
)

# MapVierw can't be given focus on mobile
if toga.platform.current_platform in {"android", "iOS"}:
    from .properties import test_focus_noop  # noqa: F401
else:
    from .properties import test_focus  # noqa: F401


# These timeouts are loose because CI can be very slow, especially on mobile.
WINDOWS_INIT_TIMEOUT = 60


@pytest.fixture
async def on_select():
    on_select = Mock()
    return on_select


@pytest.fixture
async def widget(on_select):
    if toga.platform.current_platform == "linux":
        # On Gtk, ensure that any WebViews from a previous test runs have been garbage
        # collected. This prevents a segfault at GC time likely coming from the test
        # suite running in a thread and Gtk WebViews sharing resources between
        # instances. We perform the GC run here since pytest fixtures make earlier
        # cleanup difficult.
        gc.collect()

    widget = toga.MapView(style=Pack(flex=1), on_select=on_select)

    # Some implementations of MapView are a WebView wearing a trenchcoat.
    # Ensure that the webview is fully configured before proceeding.
    if toga.platform.current_platform in {"linux", "windows"}:
        deadline = time() + WINDOWS_INIT_TIMEOUT
        while widget._impl.backlog is not None:
            if time() < deadline:
                await asyncio.sleep(0.05)
            else:
                raise RuntimeError("MapView web canvas didn't initialize")

    yield widget

    if toga.platform.current_platform == "linux":
        # On Gtk, ensure that the MapView is garbage collection before the next test
        # case. This prevents a segfault at GC time likely coming from the test suite
        # running in a thread and Gtk WebViews sharing resources between instances.
        del widget
        gc.collect()


async def test_location(widget, probe):
    """The location of the map can be changed"""
    # Initial location is Perth
    widget.location = (-31.9559, 115.8606)
    await probe.redraw("Map is at initial location", delay=2)
    assert isinstance(widget.location, toga.LatLng)
    assert widget.location == pytest.approx(
        (-31.9559, 115.8606),
        abs=probe.location_threshold,
    )

    # Set location to Margaret River, just south of Perth
    widget.location = (-33.955, 115.075)
    await probe.redraw("Location has panned to Margaret River", delay=2)
    assert isinstance(widget.location, toga.LatLng)
    assert widget.location == pytest.approx(
        (-33.955, 115.075),
        abs=probe.location_threshold,
    )


async def test_zoom(widget, probe):
    """The zoom factor of the map can be changed"""
    await probe.redraw("Map is at initial location", delay=2)

    # We can't read the zoom of a map; but we can probe to get the delta from the
    # minimum to maximum latitude that is currently visible. That delta should be within
    # a broad range at each zoom level.
    for zoom, min_span, max_span in [
        (0, 10, 50),
        (1, 1, 10),
        (2, 0.1, 1),
        (3, 0.01, 0.1),
        (4, 0.004, 0.01),
        (5, 0.001, 0.004),
    ]:
        widget.zoom = zoom
        await probe.redraw(f"Map has been zoomed to level {zoom}", delay=2)

        map_span = await probe.latitude_span()
        assert (
            min_span < map_span < max_span
        ), f"Zoom level {zoom}: failed {min_span} < {map_span} < {max_span}"


async def test_add_pins(widget, probe, on_select):
    """Pins can be added and removed from the map."""

    fremantle = toga.MapPin((-32.05423, 115.74763), title="Fremantle")
    lesmurdie = toga.MapPin((-31.994, 116.05), title="lesmurdie")
    joondalup = toga.MapPin((-31.745, 115.766), title="Joondalup")
    stadium = toga.MapPin((-31.95985, 115.8795), title="WACA Ground", subtitle="Old")

    widget.pins.add(joondalup)
    await probe.redraw("Joondalup pin has been added", delay=2)
    assert probe.pin_count == 1

    widget.pins.add(lesmurdie)
    widget.pins.add(fremantle)
    widget.pins.add(stadium)
    await probe.redraw("Other pins have been added", delay=2)
    assert probe.pin_count == 4

    # Move the sports ground to a new location
    stadium.location = (-31.951111, 115.889167)
    stadium.title = "Perth Stadium"
    stadium.subtitle = "New"
    await probe.redraw("Stadium has been moved and renamed", delay=2)

    widget.pins.remove(stadium)
    await probe.redraw("Stadium has been removed", delay=2)
    assert probe.pin_count == 3

    widget.pins.clear()
    await probe.redraw("All pins have been removed", delay=2)
    assert probe.pin_count == 0


async def test_select_pin(widget, probe, on_select):
    """Pins can be selected."""

    fremantle = toga.MapPin((-32.05423, 115.74763), title="Fremantle")
    lesmurdie = toga.MapPin((-31.994, 116.05), title="lesmurdie")
    joondalup = toga.MapPin((-31.745, 115.766), title="Joondalup")

    widget.pins.add(joondalup)
    widget.pins.add(lesmurdie)
    widget.pins.add(fremantle)
    await probe.redraw("Pins have been added")

    await probe.select_pin(lesmurdie)
    on_select.assert_called_once_with(widget, pin=lesmurdie)
    on_select.reset_mock()

    await probe.select_pin(fremantle)
    on_select.assert_called_once_with(widget, pin=fremantle)
    on_select.reset_mock()
