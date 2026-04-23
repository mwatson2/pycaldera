Changelog
=========

All notable changes to pycaldera will be documented here.

The format is based on `Keep a Changelog`_, and this project adheres to `Semantic Versioning`_.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

Categories for changes are: Added, Changed, Deprecated, Removed, Fixed, Security.


Version `0.1.3 <https://github.com/mwatson2/pycaldera/tree/v0.1.3>`__
---------------------------------------------------------------------

Release date: 2026-04-22.

Changed
~~~~~~~
- ``DEFAULT_TIMEOUT`` raised from 10 to 30 seconds. The Caldera cloud API
  periodically returns in 10+ seconds under normal conditions; the old
  timeout caused ~5% of requests to fail with ``ConnectionError`` and
  flipped downstream Home Assistant entities to unavailable and back every
  few minutes.


Version `0.1.2 <https://github.com/mwatson2/pycaldera/tree/v0.1.2>`__
---------------------------------------------------------------------

Release date: 2026-04-15.

Fixed
~~~~~
- Off-by-one pump speed encoding. The Caldera API uses wire values
  1=off, 2=low, 3=high, but the public ``PUMP_OFF/LOW/HIGH`` constants
  are 0/1/2. ``set_pump`` now translates internally via a private
  ``_PUMP_API_OFFSET`` so the public API values match user expectations.

Added
~~~~~
- ``LiveSettings.get_pump_speed()`` helper.
- ``SpaResponseDato.pumps`` property, which parses the spa's ``JET_PUMPS``
  configuration.


Version `0.1.1 <https://github.com/mwatson2/pycaldera/tree/v0.1.1>`__
---------------------------------------------------------------------

Release date: 2026-04-08.

Added
~~~~~
- ``SpaResponseDato.water_temperature`` and ``SpaResponseDato.set_temperature``
  convenience properties that read the current and target temperatures from
  the embedded ``isConnectedData.liveSettings.rows[0]`` payload. Both return
  ``None`` if no live-settings row is available.
- Unit tests for the synchronous ``CalderaClient`` covering ``get_spa_status``,
  ``get_live_settings``, ``set_pump``, ``set_temp_lock``, ``set_spa_lock`` and
  the ``close()`` paths.

Fixed
~~~~~
- README quickstart examples referenced ``status.ctrl_head_water_temperature``,
  which is not a field on the spa-status response. They now use the new
  ``status.water_temperature`` property and actually work.
- ``requirements.txt`` no longer pins development tooling (``black``,
  ``isort``, ``mypy``, ``pylint``, ``pytest`` and friends) as runtime
  dependencies. Plain ``pip install pycaldera`` now installs only ``aiohttp``
  and ``pydantic``.
- ``requirements-test.txt`` now contains the async test plugins
  (``pytest-asyncio``, ``pytest-aiohttp``) that the test suite actually
  requires, so the ``[test]`` extra is self-sufficient.

Added (release tooling)
~~~~~~~~~~~~~~~~~~~~~~~
- GitHub Actions ``release`` workflow that triggers on ``v*`` tags, runs the
  test suite, builds sdist + wheel and publishes to PyPI via
  `trusted publishing <https://docs.pypi.org/trusted-publishers/>`__
  (no API tokens stored in the repository).


Version `0.1.0 <https://github.com/mwatson2/pycaldera/tree/v0.1.0>`__
---------------------------------------------------------------------

Release date: 2026-03-13.

Initial release. Async and synchronous clients for the Caldera Connected Spa
cloud API, with support for authentication, status / live-settings retrieval,
temperature / pump / light / lock control, and an acknowledgment-polling
helper for temperature changes.
