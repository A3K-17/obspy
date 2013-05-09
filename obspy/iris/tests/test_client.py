# -*- coding: utf-8 -*-
"""
The obspy.iris.client test suite.
"""

from obspy.core.utcdatetime import UTCDateTime
from obspy.core.util import NamedTemporaryFile
from obspy.iris import Client
import filecmp
import numpy as np
import os
import StringIO
import unittest
import urllib
import warnings


class ClientTestCase(unittest.TestCase):
    """
    Test cases for obspy.iris.client.Client.
    """
    def setUp(self):
        # directory where the test files are located
        self.path = os.path.dirname(__file__)

    def test_getWaveform(self):
        """
        Testing simple waveform request method.
        """
        # simple example
        client = Client()
        start = UTCDateTime("2010-02-27T06:30:00.019538Z")
        end = start + 20
        stream = client.getWaveform("IU", "ANMO", "00", "BHZ", start, end)
        self.assertEqual(len(stream), 1)
        self.assertEqual(stream[0].stats.starttime, start)
        self.assertEqual(stream[0].stats.endtime, end)
        self.assertEqual(stream[0].stats.network, 'IU')
        self.assertEqual(stream[0].stats.station, 'ANMO')
        self.assertEqual(stream[0].stats.location, '00')
        self.assertEqual(stream[0].stats.channel, 'BHZ')
        # no data raises an exception
        self.assertRaises(Exception, client.getWaveform, "YY", "XXXX", "00",
                          "BHZ", start, end)

    def test_saveWaveform(self):
        """
        Testing simple waveform file save method.
        """
        # file identical to file retrieved via web interface
        client = Client()
        start = UTCDateTime("2010-02-27T06:30:00")
        end = UTCDateTime("2010-02-27T06:31:00")
        origfile = os.path.join(self.path, 'data', 'IU.ANMO.00.BHZ.mseed')
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.saveWaveform(tempfile, "IU", "ANMO", "00", "BHZ", start,
                                end)
            self.assertTrue(filecmp.cmp(origfile, tempfile))
        # no data raises an exception
        self.assertRaises(Exception, client.saveWaveform, "YY", "XXXX", "00",
                          "BHZ", start, end)

    def test_saveWaveformToStringIO(self):
        """
        Same as test_saveWaveform but saves to a StringIO.
        """
        # file identical to file retrieved via web interface
        client = Client()
        start = UTCDateTime("2010-02-27T06:30:00")
        end = UTCDateTime("2010-02-27T06:31:00")
        memfile = StringIO.StringIO()
        client.saveWaveform(memfile, "IU", "ANMO", "00", "BHZ", start, end)
        memfile.seek(0, 0)
        new_data = memfile.read()
        origfile = os.path.join(self.path, 'data', 'IU.ANMO.00.BHZ.mseed')
        with open(origfile, "rb") as fh:
            org_data = fh.read()
        self.assertEqual(new_data, org_data)

    def test_saveResponse(self):
        """
        Fetches and stores response information as SEED RESP file.
        """
        client = Client()
        start = UTCDateTime("2005-001T00:00:00")
        end = UTCDateTime("2008-001T00:00:00")
        # RESP, single channel
        origfile = os.path.join(self.path, 'data', 'RESP.ANMO.IU.00.BHZ')
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.saveResponse(tempfile, "IU", "ANMO", "00", "BHZ", start,
                                end)
            self.assertTrue(filecmp.cmp(origfile, tempfile))
        # RESP, multiple channels
        origfile = os.path.join(self.path, 'data', 'RESP.ANMO.IU._.BH_')
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.saveResponse(tempfile, "IU", "ANMO", "*", "BH?", start, end)
            self.assertTrue(filecmp.cmp(origfile, tempfile))
        # StationXML, single channel
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.saveResponse(tempfile, "IU", "ANMO", "00", "BHZ", start,
                                end, format="StationXML")
            data = open(tempfile).read()
        self.assertTrue('<Station net_code="IU" sta_code="ANMO">' in data)
        # SACPZ, single channel
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.saveResponse(tempfile, "IU", "ANMO", "00", "BHZ", start,
                                end, format="SACPZ")
            data = open(tempfile).read()
        self.assertTrue('NETWORK   (KNETWK): IU' in data)
        self.assertTrue('STATION    (KSTNM): ANMO' in data)

    def test_saveResponseToStringIO(self):
        """
        Same as test_saveResponse but saves to a StringIO.
        """
        client = Client()
        start = UTCDateTime("2005-001T00:00:00")
        end = UTCDateTime("2008-001T00:00:00")
        # RESP, single channel
        origfile = os.path.join(self.path, 'data', 'RESP.ANMO.IU.00.BHZ')
        with open(origfile, "rb") as fh:
            org_data = fh.read()
        memfile = StringIO.StringIO()
        client.saveResponse(memfile, "IU", "ANMO", "00", "BHZ", start, end)
        memfile.seek(0, 0)
        new_data = memfile.read()
        self.assertEqual(new_data, org_data)
        # RESP, multiple channels
        origfile = os.path.join(self.path, 'data', 'RESP.ANMO.IU._.BH_')
        with open(origfile, "rb") as fh:
            org_data = fh.read()
        memfile = StringIO.StringIO()
        client.saveResponse(memfile, "IU", "ANMO", "*", "BH?", start, end)
        memfile.seek(0, 0)
        new_data = memfile.read()
        self.assertEqual(new_data, org_data)
        # StationXML, single channel
        memfile = StringIO.StringIO()
        client.saveResponse(memfile, "IU", "ANMO", "00", "BHZ", start, end,
                format="StationXML")
        memfile.seek(0, 0)
        data = memfile.read()
        self.assertTrue('<Station net_code="IU" sta_code="ANMO">' in data)
        # SACPZ, single channel
        memfile = StringIO.StringIO()
        client.saveResponse(memfile, "IU", "ANMO", "00", "BHZ", start, end,
                format="SACPZ")
        memfile.seek(0, 0)
        data = memfile.read()
        self.assertTrue('NETWORK   (KNETWK): IU' in data)
        self.assertTrue('STATION    (KSTNM): ANMO' in data)

    def test_getEvents(self):
        """
        Tests getEvents method.
        """
        client = Client()
        dt = UTCDateTime("2012-03-13T04:49:38")
        # 1
        cat = client.getEvents(mindepth=34.9, maxdepth=35.1, magtype="MB",
                               catalog="NEIC PDE", lat=-56.1, lon=-26.7,
                               maxradius=2, starttime=dt, endtime=dt + 10)
        self.assertEqual(len(cat), 1)
        ev = cat[0]
        self.assertEqual(len(ev.origins), 1)
        self.assertEqual(len(ev.magnitudes), 1)
        self.assertEqual(ev.origins[0].depth, 35.0)
        self.assertEqual(ev.origins[0].latitude, -55.404)
        self.assertEqual(ev.origins[0].longitude, -27.895)
        self.assertEqual(ev.magnitudes[0].magnitude_type, 'MB')

    def test_sacpz(self):
        """
        Fetches SAC poles and zeros information.
        """
        client = Client()
        # 1
        t1 = UTCDateTime("2005-01-01")
        t2 = UTCDateTime("2008-01-01")
        result = client.sacpz("IU", "ANMO", "00", "BHZ", t1, t2)
        # drop lines with creation date (current time during request)
        result = result.splitlines()
        sacpz_file = os.path.join(self.path, 'data', 'IU.ANMO.00.BHZ.sacpz')
        expected = open(sacpz_file, 'rt').read().splitlines()
        result.pop(5)
        expected.pop(5)
        self.assertEqual(result, expected)
        # 2 - empty location code
        dt = UTCDateTime("2002-11-01")
        result = client.sacpz('UW', 'LON', '', 'BHZ', dt)
        self.assertTrue("* STATION    (KSTNM): LON" in result)
        self.assertTrue("* LOCATION   (KHOLE):   " in result)
        # 3 - empty location code via '--'
        result = client.sacpz('UW', 'LON', '--', 'BHZ', dt)
        self.assertTrue("* STATION    (KSTNM): LON" in result)
        self.assertTrue("* LOCATION   (KHOLE):   " in result)

    def test_distaz(self):
        """
        Tests distance and azimuth calculation between two points on a sphere.
        """
        client = Client()
        # normal request
        result = client.distaz(stalat=1.1, stalon=1.2, evtlat=3.2, evtlon=1.4)
        self.assertAlmostEqual(result['distance'], 2.09554)
        self.assertAlmostEqual(result['backazimuth'], 5.46946)
        self.assertAlmostEqual(result['azimuth'], 185.47692)
        # w/o kwargs
        result = client.distaz(1.1, 1.2, 3.2, 1.4)
        self.assertAlmostEqual(result['distance'], 2.09554)
        self.assertAlmostEqual(result['backazimuth'], 5.46946)
        self.assertAlmostEqual(result['azimuth'], 185.47692)
        # missing parameters
        self.assertRaises(Exception, client.distaz, stalat=1.1)
        self.assertRaises(Exception, client.distaz, 1.1)
        self.assertRaises(Exception, client.distaz, stalat=1.1, stalon=1.2)
        self.assertRaises(Exception, client.distaz, 1.1, 1.2)

    def test_flinnengdahl(self):
        """
        Tests calculation of Flinn-Engdahl region code or name.
        """
        client = Client()
        # code
        result = client.flinnengdahl(lat=-20.5, lon=-100.6, rtype="code")
        self.assertEqual(result, 683)
        # w/o kwargs
        result = client.flinnengdahl(-20.5, -100.6, "code")
        self.assertEqual(result, 683)
        # region
        result = client.flinnengdahl(lat=42, lon=-122.24, rtype="region")
        self.assertEqual(result, 'OREGON')
        # w/o kwargs
        result = client.flinnengdahl(42, -122.24, "region")
        self.assertEqual(result, 'OREGON')
        # both
        result = client.flinnengdahl(lat=-20.5, lon=-100.6, rtype="both")
        self.assertEqual(result, (683, 'SOUTHEAST CENTRAL PACIFIC OCEAN'))
        # w/o kwargs
        result = client.flinnengdahl(-20.5, -100.6, "both")
        self.assertEqual(result, (683, 'SOUTHEAST CENTRAL PACIFIC OCEAN'))
        # default rtype
        result = client.flinnengdahl(lat=42, lon=-122.24)
        self.assertEqual(result, (32, 'OREGON'))
        # w/o kwargs
        # outside boundaries
        self.assertRaises(Exception, client.flinnengdahl, lat=-90.1, lon=0)
        self.assertRaises(Exception, client.flinnengdahl, lat=90.1, lon=0)
        self.assertRaises(Exception, client.flinnengdahl, lat=0, lon=-180.1)
        self.assertRaises(Exception, client.flinnengdahl, lat=0, lon=180.1)

    def test_traveltime(self):
        """
        Tests calculation of travel-times for seismic phases.
        """
        client = Client()
        result = client.traveltime(evloc=(-36.122, -72.898), evdepth=22.9,
            staloc=[(-33.45, -70.67), (47.61, -122.33), (35.69, 139.69)])
        self.assertTrue(result.startswith('Model: iasp91'))

    def test_evalresp(self):
        """
        Tests evaluating instrument response information.
        """
        client = Client()
        dt = UTCDateTime("2005-01-01")
        # plot as PNG file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='plot',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rb').read(4)[1:4], 'PNG')
        # plot-amp as PNG file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='plot-amp',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rb').read(4)[1:4], 'PNG')
        # plot-phase as PNG file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='plot-phase',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rb').read(4)[1:4], 'PNG')
        # fap as ASCII file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='fap',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rt').readline(),
                             '1.000000E-05  1.202802E+04  1.792007E+02\n')
        # cs as ASCII file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='cs',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rt').readline(),
                             '1.000000E-05 -1.202685E+04 1.677835E+02\n')
        # fap & def as ASCII file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='fap', units='def',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rt').readline(),
                             '1.000000E-05  1.202802E+04  1.792007E+02\n')
        # fap & dis as ASCII file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='fap', units='dis',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rt').readline(),
                             '1.000000E-05  7.557425E-01  2.692007E+02\n')
        # fap & vel as ASCII file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='fap', units='vel',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rt').readline(),
                             '1.000000E-05  1.202802E+04  1.792007E+02\n')
        # fap & acc as ASCII file
        with NamedTemporaryFile() as tf:
            tempfile = tf.name
            client.evalresp(network="IU", station="ANMO", location="00",
                            channel="BHZ", time=dt, output='fap', units='acc',
                            filename=tempfile)
            self.assertEqual(open(tempfile, 'rt').readline(),
                             '1.000000E-05  1.914318E+08  8.920073E+01\n')
        # fap as NumPy ndarray
        data = client.evalresp(network="IU", station="ANMO", location="00",
                               channel="BHZ", time=dt, output='fap')
        np.testing.assert_array_equal(data[0],
            [1.00000000e-05, 1.20280200e+04, 1.79200700e+02])
        # cs as NumPy ndarray
        data = client.evalresp(network="IU", station="ANMO", location="00",
                               channel="BHZ", time=dt, output='cs')
        np.testing.assert_array_equal(data[0],
            [1.00000000e-05, -1.20268500e+04, 1.67783500e+02])

    def test_event(self):
        """
        Tests event Web service interface.

        Examples are inspired by http://www.iris.edu/ws/event/.
        """
        client = Client()
        # 1
        url = "http://www.iris.edu/ws/event/query?mindepth=34.9&" + \
            "maxdepth=35.1&catalog=NEIC%20PDE&contributor=NEIC%20PDE-Q&" + \
            "magtype=MB&lat=-56.1&lon=-26.7&maxradius=1"
        # direct call
        doc1 = urllib.urlopen(url).read()
        # using client
        doc2 = client.event(mindepth=34.9, maxdepth=35.1, catalog="NEIC PDE",
                            contributor="NEIC PDE-Q", magtype="MB", lat=-56.1,
                            lon=-26.7, maxradius=1)
        self.assertEqual(doc1, doc2)
        client = Client()
        # 2
        url = "http://www.iris.edu/ws/event/query?eventid=3316989"
        # direct call
        doc1 = urllib.urlopen(url).read()
        # using client
        doc2 = client.event(eventid=3316989)
        self.assertEqual(doc1, doc2)
        # 2
        url = "http://www.iris.edu/ws/event/query?eventid=3316989"
        # direct call
        doc1 = urllib.urlopen(url).read()
        # using client
        doc2 = client.event(eventid=3316989)
        self.assertEqual(doc1, doc2)
        # 3
        url = "http://www.iris.edu/ws/event/query?minmag=8.5"
        # direct call
        doc1 = urllib.urlopen(url).read()
        # using client
        doc2 = client.event(minmag=8.5)
        self.assertEqual(doc1, doc2)
        # 4
        url = "http://www.iris.edu/ws/event/query?starttime=2011-01-07T" + \
            "14%3A00%3A00&endtime=2011-02-07&minlat=15&maxlat=40&" + \
            "minlon=-170&maxlon=170&preferredonly=yes&" + \
            "includeallmagnitudes=yes&orderby=magnitude"
        # direct call
        doc1 = urllib.urlopen(url).read()
        # using client
        doc2 = client.event(starttime=UTCDateTime(2011, 1, 7, 14),
                            endtime=UTCDateTime('2011-02-07'), minlat=15.0,
                            maxlat=40.0, minlon=-170, maxlon=170,
                            preferredonly=True, includeallmagnitudes=True,
                            orderby='magnitude')
        self.assertEqual(doc1, doc2)

    def test_availability(self):
        """
        Tests availability of waveform data at the DMC.

        Examples are inspired by http://www.iris.edu/ws/availability/.
        """
        client = Client()
        # 1
        t1 = UTCDateTime("2010-02-27T06:30:00.000")
        t2 = UTCDateTime("2010-02-27T10:30:00.000")
        result = client.availability('IU', channel='B*', starttime=t1,
                                     endtime=t2)
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('IU YSS 00 BHZ' in result)
        # 2
        dt = UTCDateTime("2011-11-13T07:00:00")
        result = client.availability(network='GE', starttime=dt,
                                     endtime=dt + 10)
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('GE DAG -- BHE' in result)
        # 3 - unknown network results in empty string
        dt = UTCDateTime(2011, 11, 16)
        result = client.availability(network='XX', starttime=dt,
                                     endtime=dt + 10)
        # 4 - location=None
        t1 = UTCDateTime("2010-02-27T06:30:00")
        t2 = UTCDateTime("2010-02-27T06:40:00")
        result = client.availability("IU", "K*", starttime=t1, endtime=t2)
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('IU KBL -- BHZ' in result)
        self.assertTrue('IU KBS 00 BHE' in result)
        # 5 - empty location
        result = client.availability("IU", "K*", "", starttime=t1, endtime=t2)
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('IU KBL -- BHZ' in result)
        self.assertFalse('IU KBS 00 BHE' in result)
        # 6 - empty location code via '--'
        result = client.availability("IU", "K*", "--", starttime=t1,
                                     endtime=t2)
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('IU KBL -- BHZ' in result)
        self.assertFalse('IU KBS 00 BHE' in result)

    def test_resp(self):
        """
        Tests resp Web service interface.

        Examples are inspired by http://www.iris.edu/ws/resp/.
        """
        client = Client()
        # 1
        t1 = UTCDateTime("2005-001T00:00:00")
        t2 = UTCDateTime("2008-001T00:00:00")
        result = client.resp("IU", "ANMO", "00", "BHZ", t1, t2)
        self.assertTrue('B050F03     Station:     ANMO' in result)
        # 2 - empty location code
        result = client.resp("UW", "LON", "", "EHZ")
        self.assertTrue('B050F03     Station:     LON' in result)
        self.assertTrue('B052F03     Location:    ??' in result)
        # 3 - empty location code via '--'
        result = client.resp("UW", "LON", "--", "EHZ")
        self.assertTrue('B050F03     Station:     LON' in result)
        self.assertTrue('B052F03     Location:    ??' in result)
        # 4
        dt = UTCDateTime("2010-02-27T06:30:00.000")
        result = client.resp("IU", "ANMO", "*", "*", dt)
        self.assertTrue('B050F03     Station:     ANMO' in result)

    def test_timeseries(self):
        """
        Tests timeseries Web service interface.

        Examples are inspired by http://www.iris.edu/ws/timeseries/.
        """
        client = Client()
        # 1
        t1 = UTCDateTime("2005-001T00:00:00")
        t2 = UTCDateTime("2005-001T00:01:00")
        # no filter
        st1 = client.timeseries("IU", "ANMO", "00", "BHZ", t1, t2)
        # instrument corrected
        st2 = client.timeseries("IU", "ANMO", "00", "BHZ", t1, t2,
                                filter=["correct"])
        # compare results
        self.assertEqual(st1[0].stats.starttime, st2[0].stats.starttime)
        self.assertEqual(st1[0].stats.endtime, st2[0].stats.endtime)
        self.assertEqual(st1[0].data[0], 24)
        self.assertAlmostEqual(st2[0].data[0], -2.4910707e-06)

    def test_issue419(self):
        """
        obspy.iris.Client.availability should work with output='bulkdataselect'
        """
        client = Client()
        # 1 - default output ('bulkdataselect')
        t1 = UTCDateTime("2010-02-27T06:30:00.000")
        t2 = UTCDateTime("2010-02-27T10:30:00.000")
        result = client.availability('IU', channel='B*', starttime=t1,
                                     endtime=t2)
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('IU YSS 00 BHZ' in result)
        # 2 - explicit set output 'bulkdataselect'
        t1 = UTCDateTime("2010-02-27T06:30:00.000")
        t2 = UTCDateTime("2010-02-27T10:30:00.000")
        result = client.availability('IU', channel='B*', starttime=t1,
                                     endtime=t2, output='bulkdataselect')
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('IU YSS 00 BHZ' in result)
        # 3 - output 'bulk' (backward compatibility)
        t1 = UTCDateTime("2010-02-27T06:30:00.000")
        t2 = UTCDateTime("2010-02-27T10:30:00.000")
        with warnings.catch_warnings(record=True):
            warnings.simplefilter('ignore', DeprecationWarning)
            result = client.availability('IU', channel='B*', starttime=t1,
                                         endtime=t2, output='bulk')
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('IU YSS 00 BHZ' in result)
        # 4 - output 'xml'
        t1 = UTCDateTime("2010-02-27T06:30:00.000")
        t2 = UTCDateTime("2010-02-27T10:30:00.000")
        result = client.availability('IU', channel='B*', starttime=t1,
                                     endtime=t2, output='xml')
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue('<?xml' in result)


def suite():
    return unittest.makeSuite(ClientTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
