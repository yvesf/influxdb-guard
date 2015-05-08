#!/usr/bin/env python3
import itertools
from multiprocessing.pool import ThreadPool as Pool
from pyinflux.client import InfluxDB, Line


class TwoWayInfluxDB(InfluxDB):
    def __init__(self, write_url):
        super().__init__('test', 'localhost')
        self._write_url = write_url

influxdb = TwoWayInfluxDB('http://localhost:8001/write/test?')
value_generator = itertools.count()

def test(number):
    for value in value_generator:
        if value > 200:
            return
        if (value + 1) % 50 == 0:
            print("thread {} at {}".format(number, value))
        expected = "value{value}".format(value=value)
        line = Line('series' + str(value),
                    {'tag': 'tag' + expected},
                    {'field': 'field' + expected})

        try:
            influxdb.write([line])
        except:
            print(line)
            raise

        query = """\
    SELECT *
    FROM "series{value}"
    WHERE time >= now() - 2s""".format(value=value)
        try:
            results = influxdb.query(query).as_json()['results']
        except:
            print("""\
    Failure. With the following INSERT:
    {line}""".format(line=line))
            raise
        try:
            assert len(results) == 1
            series = results[0]['series']
            assert len(series) == 1
            series_result = series[0]
            assert series_result['name'] == 'series' + str(value)
            assert len(series_result['values']) == 1
            values = series_result['values']
            assert len(values) == 1
            assert len(values[0]) == 3
            columns = series_result['columns']
            assert columns == ['time', 'field', 'tag']

            assert values[0][columns.index('field')] == 'fieldvalue' + str(value)
            assert values[0][columns.index('tag')] == 'tagvalue' + str(value)
        except:
            print("""\
    Failure. With the following INSERT:
    {line}

    Got this result:
    {results}""".format(line=line, results=results))
            raise


print(influxdb.query('DROP DATABASE test').as_text())
print(influxdb.query('CREATE DATABASE test').as_text())

N_PROC = 1
with Pool(processes=N_PROC) as pool:
    for res in pool.imap_unordered(test, range(1, N_PROC + 1)):
        # they are suppossed to run endlessly, if one returns then there was a failure
        pool.terminate()
print('Done')
