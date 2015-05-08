# influxdb guard

Simple *firewall* for influxdb database

## Running

Requires [pyinflux](https://github.com/yvesf/pyinflux) library.

### development

```
# ./run.py
... prints default config
# ./run.py <path-to-config>
```

### gunicorn/waitress

```
# waitress-serve run:application
# gunicorn3 run
```
Searches for a file called `config` in current working directory.