# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2016/09/19
# copy: (C) Copyright 2016-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import unittest
import time

#------------------------------------------------------------------------------
class TestEpoch(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_now(self):
    import epoch
    self.assertAlmostEqual(epoch.now(), time.time(), delta=0.5)

  #----------------------------------------------------------------------------
  def test_zulu(self):
    import epoch
    self.assertEqual(epoch.zulu(1446303600.4), '2015-10-31T15:00:00.400Z')
    self.assertEqual(epoch.zulu(1446303600.4, ms=False), '2015-10-31T15:00:00Z')
    # todo: when `mocktime` package is available, use:
    # with mocktime.patch(freeze=1446303600.4):
    #   self.assertEqual(epoch.zulu(), '2015-10-31T15:00:00.400Z')
    #   self.assertEqual(epoch.zulu(ms=False), '2015-10-31T15:00:00Z')
    self.assertEqual(len(epoch.zulu()), 24)
    self.assertEqual(len(epoch.zulu(ms=False)), 20)

  #----------------------------------------------------------------------------
  def test_parseZulu(self):
    from epoch import parseZulu as p
    self.assertEqual(p('2015-10-31T15:00:00Z'), 1446303600)
    self.assertEqual(p('2015-11-01T15:00:00Z'), 1446390000)
    self.assertEqual(p('2015-11-02T15:00:00Z'), 1446476400)
    self.assertEqual(p('20151031T150000Z'), 1446303600)
    self.assertEqual(p('20151101T150000Z'), 1446390000)
    self.assertEqual(p('20151102T150000Z'), 1446476400)
    self.assertEqual(p('2015-10-31T15:00:00.6Z'), 1446303600.6)
    self.assertEqual(p('2015-10-31T15:00:00.600Z'), 1446303600.6)
    self.assertEqual(p('2015-10-31T15:00:00.006Z'), 1446303600.006)
    self.assertEqual(p('2015-10-31T15:00:00.0006Z'), 1446303600.0006)
    self.assertEqual(p('20151031T150000.6Z'), 1446303600.6)
    self.assertEqual(p('20151031T150000.600Z'), 1446303600.6)
    self.assertEqual(p('20151031T150000.006Z'), 1446303600.006)
    self.assertEqual(p('20151031T150000.0006Z'), 1446303600.0006)
    self.assertEqual(p('20151031T150000.000600000Z'), 1446303600.0006)
    self.assertEqual(p('20151031T150000.000006000Z'), 1446303600.000006)
    # sub-microsecond accuracy not possible (with current `datetime` sys library)
    self.assertEqual(p('20151031T150000.000000600Z'), 1446303600)

  #----------------------------------------------------------------------------
  def test_parse(self):
    from epoch import parse as p
    self.assertEqual(p(None), None)
    self.assertEqual(p(1446303600), 1446303600)
    self.assertEqual(p(1446303600.7), 1446303600.7)
    self.assertEqual(p('1446303600'), 1446303600)
    self.assertEqual(p('1446303600.7'), 1446303600.7)

  #----------------------------------------------------------------------------
  def test_sod(self):
    import epoch
    self.assertEqual(epoch.sod(ts=1474307548), 1474243200)
    self.assertEqual(epoch.sod(ts=1474307548, offset=2), 1474416000)
    self.assertEqual(epoch.sod(ts=1474307548, offset=-1), 1474156800)
    et = 'America/New_York'
    # test US/EDT
    self.assertEqual(epoch.sod(ts=1474307548, tz=et), 1474257600)
    self.assertEqual(epoch.sod(ts=1474307548, tz=et, offset=2), 1474430400)
    self.assertEqual(epoch.sod(ts=1474307548, tz=et, offset=-1), 1474171200)
    # test US/EST
    self.assertEqual(epoch.sod(ts=1481826792), 1481760000)
    self.assertEqual(epoch.sod(ts=1481826792, tz=et), 1481778000)
    self.assertEqual(epoch.sod(ts=1481826792, tz=et, offset=2), 1481950800)
    self.assertEqual(epoch.sod(ts=1481826792, tz=et, offset=-1), 1481691600)
    # test DST bridging
    #   1446303600 == 2015-10-31T15:00:00Z (sat)
    #   1446390000 == 2015-11-01T15:00:00Z (sun; US/ET: daylight savings ends at 2AM)
    #   1446476400 == 2015-11-02T15:00:00Z (mon)
    self.assertEqual(epoch.sod(ts=1446303600), 1446249600)
    self.assertEqual(epoch.sod(ts=1446303600, offset=1), 1446336000)
    self.assertEqual(epoch.sod(ts=1446303600, offset=2), 1446422400)
    self.assertEqual(epoch.sod(ts=1446390000, offset=-1), 1446249600)
    self.assertEqual(epoch.sod(ts=1446390000), 1446336000)
    self.assertEqual(epoch.sod(ts=1446390000, offset=1), 1446422400)
    self.assertEqual(epoch.sod(ts=1446476400, offset=-2), 1446249600)
    self.assertEqual(epoch.sod(ts=1446476400, offset=-1), 1446336000)
    self.assertEqual(epoch.sod(ts=1446476400), 1446422400)
    self.assertEqual(epoch.sod(ts=1446303600, tz=et), 1446264000)
    self.assertEqual(epoch.sod(ts=1446303600, tz=et, offset=1), 1446350400)
    self.assertEqual(epoch.sod(ts=1446303600, tz=et, offset=2), 1446440400)
    self.assertEqual(epoch.sod(ts=1446390000, tz=et, offset=-1), 1446264000)
    self.assertEqual(epoch.sod(ts=1446350401, tz=et), 1446350400)
    self.assertEqual(epoch.sod(ts=1446390000, tz=et), 1446350400)
    self.assertEqual(epoch.sod(ts=1446390000, tz=et, offset=1), 1446440400)
    self.assertEqual(epoch.sod(ts=1446476400, tz=et, offset=-2), 1446264000)
    self.assertEqual(epoch.sod(ts=1446476400, tz=et, offset=-1), 1446350400)
    self.assertEqual(epoch.sod(ts=1446476400, tz=et), 1446440400)

    # todo: find a leap-second offset wrench and test that...

  #----------------------------------------------------------------------------
  def test_sod_replace(self):
    import epoch
    et = 'America/New_York'
    # 1478037582 == 2016-11-01T21:59:42Z
    #   +5 days is Sunday, and the switch from EDT to EST
    #   hence the weirdness that sod + 16.5 * 3600 == 15:30 !
    self.assertEqual(
      epoch.sod(ts=1478037582, offset=5, tz=et) + 16.5 * 3600,
      1478464200)
    self.assertEqual(
      epoch.sod(ts=1478037582, offset=5, tz=et, replace=dict(hour=15, minute=30)),
      1478464200)

  #----------------------------------------------------------------------------
  def test_sow(self):
    import epoch
    self.assertEqual(epoch.sow(ts=1474307548), 1474243200)
    et = 'America/New_York'
    # test DST bridging (2015/11/01 == sunday)
    #   1446303600 == 2015-10-31T15:00:00Z (sat)
    #   1446390000 == 2015-11-01T15:00:00Z (sun; US/ET: daylight savings ends at 2AM)
    #   1446476400 == 2015-11-02T15:00:00Z (mon)
    self.assertEqual(epoch.sow(ts=1446303600), 1445817600)
    self.assertEqual(epoch.sow(ts=1446303600, offset=1), 1446422400)
    self.assertEqual(epoch.sow(ts=1446303600, offset=2), 1447027200)
    self.assertEqual(epoch.sow(ts=1446303600, offset=-1), 1445212800)
    self.assertEqual(epoch.sow(ts=1446303600, offset=-2), 1444608000)
    self.assertEqual(epoch.sow(ts=1446303600, day=1), 1445904000)
    self.assertEqual(epoch.sow(ts=1446303600, day=5), 1446249600)
    self.assertEqual(epoch.sow(ts=1446303600, day=6), 1445731200)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et), 1445832000)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et, offset=1), 1446440400)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et, offset=2), 1447045200)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et, offset=-1), 1445227200)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et, offset=-2), 1444622400)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et, day=1), 1445918400)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et, day=5), 1446264000)
    self.assertEqual(epoch.sow(ts=1446303600, tz=et, day=6), 1445745600)

    # todo: find a leap-second offset wrench and test that...

  #----------------------------------------------------------------------------
  def test_som(self):
    import epoch
    from epoch import parseZulu as p
    self.assertEqual(epoch.som(ts=p('20151031T150000Z')), p('20151001T000000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), offset=1), p('20151101T000000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), offset=2), p('20151201T000000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), offset=-1), p('20150901T000000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), offset=-2), p('20150801T000000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), offset=28), p('20180201T000000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), offset=-28), p('20130601T000000Z'))
    et = 'America/New_York'
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), tz=et), p('20151001T040000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), tz=et, offset=1), p('20151101T040000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), tz=et, offset=2), p('20151201T050000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), tz=et, offset=-1), p('20150901T040000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), tz=et, offset=28), p('20180201T050000Z'))
    self.assertEqual(epoch.som(ts=p('20151031T150000Z'), tz=et, offset=-28), p('20130601T040000Z'))

    # todo: find a leap-second offset wrench and test that...
    # todo: find a leap-year offset wrench and test that...

  #----------------------------------------------------------------------------
  def test_soy(self):
    import epoch
    from epoch import parseZulu as p
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z')), p('20150101T000000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), offset=1), p('20160101T000000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), offset=4), p('20190101T000000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), offset=-1), p('20140101T000000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), offset=-4), p('20110101T000000Z'))
    et = 'America/New_York'
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), tz=et), p('20150101T050000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), tz=et, offset=1), p('20160101T050000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), tz=et, offset=4), p('20190101T050000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), tz=et, offset=-1), p('20140101T050000Z'))
    self.assertEqual(epoch.soy(ts=p('20151031T150000Z'), tz=et, offset=-4), p('20110101T050000Z'))

    # todo: find a leap-second offset wrench and test that...
    # todo: find a leap-year offset wrench and test that...

  #----------------------------------------------------------------------------
  def test_ts2age(self):
    import epoch
    self.assertEqual(epoch.ts2age(None, origin=1234567890), None)
    self.assertEqual(epoch.ts2age(1202945490, origin=1234567890), -1.0)
    self.assertEqual(epoch.ts2age(1218670290, origin=1234567890), -0.5)
    self.assertEqual(epoch.ts2age(1266103890, origin=1234567890), 1.0)
    self.assertEqual(epoch.ts2age(1344900690, origin=1234567890), 3.5)
    self.assertEqual(epoch.ts2age(2023486290, origin=1234567890), 25)
    self.assertEqual(epoch.ts2age(2654638290, origin=1234567890), 45)
    self.assertEqual(epoch.ts2age(2970171090, origin=1234567890), 55)

  #----------------------------------------------------------------------------
  def test_age2ts(self):
    import epoch
    self.assertEqual(epoch.age2ts(None, origin=1234567890), None)
    self.assertEqual(epoch.age2ts(-1.0, origin=1234567890), 1202945490)
    self.assertEqual(epoch.age2ts(-0.5, origin=1234567890), 1218670290)
    self.assertEqual(epoch.age2ts(1.0,  origin=1234567890), 1266103890)
    self.assertEqual(epoch.age2ts(3.5,  origin=1234567890), 1344900690)
    self.assertEqual(epoch.age2ts(25,   origin=1234567890), 2023486290)
    self.assertEqual(epoch.age2ts(45,   origin=1234567890), 2654638290)
    self.assertEqual(epoch.age2ts(55,   origin=1234567890), 2970171090)

  #----------------------------------------------------------------------------
  def test_tsreplace(self):
    import epoch
    ts = epoch.parse('2015-12-08T14:56:33Z')
    self.assertEqual(ts, 1449586593)
    ts = epoch.tsreplace(ts, hour=9, minute=30)
    self.assertEqual(ts, 1449567033)
    ts = epoch.tsreplace(ts, tz='Europe/Paris', hour=9, minute=30)
    self.assertEqual(ts, 1449563433)


#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
