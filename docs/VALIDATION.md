# Reference validation

The delivered source was checked in the build environment using Python 3.12:

- `python -m pytest -q`: 14 passed.
- Actual Uvicorn startup and HTTP health/order requests: passed.
- Seed script and read-only customer/order JOIN: passed.
- SQL benchmark: executed; reference results in `benchmark-results.json`.

The dependency stack emitted a non-failing AnyIO/Starlette deprecation warning during testing. Docker, Windows execution, Postman's UI, and hosted GitHub Actions were not run in this environment. The CI workflow is provided for your repository to run after upload.

These checks validate the supplied project, not completion of the exercises by its future user. Capture your own incident evidence and measurements.
