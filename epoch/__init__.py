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

import time
from datetime import datetime, timedelta, tzinfo
import calendar
import re
import math

import pytz

#------------------------------------------------------------------------------

DEFAULT_TZ              = pytz.UTC
DAYSPERYEAR             = 365.2422

#------------------------------------------------------------------------------
def setDefaultTz(tz):
  global DEFAULT_TZ
  DEFAULT_TZ = getTz(tz)

#------------------------------------------------------------------------------
def getDefaultTz():
  return getTz()

#------------------------------------------------------------------------------
def getTz(tz=None):
  '''
  Returns the `datetime.tzinfo` object for timezone `tz`. If `tz` is
  None or not specified, returns the package-default timezone, which
  defaults to UTC.
  '''
  # todo: should `tz` default to the machines default locale? this is
  #       good for client-side programs, but not for server-side
  #       applications...
  tz = tz or DEFAULT_TZ
  if isinstance(tz, tzinfo):
    return tz
  return pytz.timezone(tz)

#------------------------------------------------------------------------------
def now():
  return time.time()

#------------------------------------------------------------------------------
def zulu(ts=None, ms=True):
  '''
  Returns the specified epoch time `ts` (or current time if None or
  not provided) as an ISO 8601 Combined string in zulu time (with
  millisecond precision), e.g. ``epoch.zulu(1362187446.553)`` =>
  ``'2013-03-02T01:24:06.553Z'``. If `ms` is True (the default),
  milliseconds will be included, otherwise truncated. If `ts` has
  beyond-millisecond precision, it will be truncated to
  millisecond-level precision.
  '''
  if ts is None:
    ts = now()
  ms = '.%03dZ' % (round(ts * 1000) % 1000,) if ms else 'Z'
  return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(ts)) + ms
z = zulu

#------------------------------------------------------------------------------
def parse(text):
  '''
  Tries the following methods of extracting an epoch timestamp from `text`:

  * Checks for None, integer, or float type (and returns that as-is)
  * Checks for an all-digits text, and casts that to float
  * Fallsback to parsing via :func:`parseZulu`

  Note that this function is intended to be used with code-generated
  strings (such as those generated by `epoch.zulu`), and is therefore
  not very forgiving. For a much more human-friendly parser, see the
  example in :func:`parseZulu`.
  '''

  if text is None or isinstance(text, (float, int)):
    return text
  try:
    return float(text)
  except ValueError:
    pass
  return parseZulu(text)

#------------------------------------------------------------------------------
_zulu_cre = re.compile(r'^(\d{4})-?(\d{2})-?(\d{2})T(\d{2}):?(\d{2}):?(\d{2})(\.\d{1,3})?Z$')
def parseZulu(text):
  '''
  Parses an ISO 8601 Combined string into an epoch timestamp. Note
  that this function is intended to be used with strings generated by
  `epoch.zulu`, and is therefore not very forgiving. For a much more
  human-friendly parser, try::

    import dateutil.parser
    result = dateutil.parser.parse(text, tzinfos = {'UTC': 0}))

  but please note that it does not properly warn about ambiguities;
  for example ``01/02/03`` gets interpreted without hesitation as
  ``2003/01/02``... ugh.
  '''
  res = _zulu_cre.match(text)
  if not res:
    raise SyntaxError(
      '%r is not a valid ISO 8601 Combined date/time string' % (text,))
  res = res.groups()
  res = res[:6] + ('{:0<3}'.format((res[6] or '.0')[1:]),)
  return dt2ts(pytz.UTC.localize(datetime(*[int(x) for x in res])))

#------------------------------------------------------------------------------
def dt2ts(dt):
  '''
  Returns a UNIX epoch timestamp for the specified `tz` `datetime.datetime`
  object.
  '''
  return float(calendar.timegm(dt.utctimetuple()))

#------------------------------------------------------------------------------
def ts2dt(ts, tz=None):
  '''
  Returns a timezone-aware `datetime.datetime` object for the
  specified UNIX epoch timestamp `ts` object. The `tz` object can be
  anything accepted by :func:`getTz`.
  '''
  return datetime.fromtimestamp(ts, getTz(tz))

#------------------------------------------------------------------------------
def dtreplace(dt, *args, **kw):
  '''
  A version of :meth:`datetime.datetime.replace()` that properly
  maintains the `dt.tzinfo` if the replace will cause DST boundary
  switching.
  '''
  if 'tzinfo' in kw:
    raise TypeError('dtreplace cannot be used to replace `tzinfo`')
  return dt.tzinfo.localize(dt.replace(tzinfo=None).replace(*args, **kw))

#------------------------------------------------------------------------------
def tsreplace(ts=None, tz=None, *args, **kw):
  '''
  An epoch timestamp-oriented version of `dtreplace`. Example:

  .. code:: python

    import epoch

    ts = epoch.parse('2015-12-08T14:56:33Z')
    # ts == 1449586593.0

    ts = epoch.tsreplace(ts, hour=9, minute=30)
    # ts == 1449567033.0
    s = epoch.zulu(ts)
    # s == '2015-12-08T09:30:33.000Z'

    ts = epoch.tsreplace(ts, tz='Europe/Paris', hour=9, minute=30)
    # ts == 1449563433.0
    s = epoch.zulu(ts)
    # s == '2015-12-08T08:30:33.000Z'

  '''
  if ts is None:
    ts = now()
  return dt2ts(dtreplace(ts2dt(ts, tz=tz), *args, **kw))

#------------------------------------------------------------------------------
def tzcorrect(dt):
  '''
  Forces a "re-timezoning" of the `dt` object. This is necessary when
  working with `datetime.datetime` objects because they behave
  incorrectly when they are forced to cross DST boundaries during
  calls to `datetime.datetime.replace(...)` or adjustments via
  `datetime.timedelta` objects.
  '''
  if not dt.tzinfo:
    raise TypeError('tzcorrect cannot be used with naive datetimes')
  return dt.tzinfo.localize(dt.replace(tzinfo=None))

#------------------------------------------------------------------------------
def sod(ts=None, tz=None, offset=None, replace=None):
  '''
  Returns the epoch timestamp of the start of the current day relative
  to the timezone `tz`. If `ts` is specified, the start of the day
  containing `ts` is returned. If `offset` is specified, it is taken
  to be an integral number of days to offset the returned value by.
  Note that due to leap seconds, daylight savings, etc, this is more
  complex than just 60 seconds * 60 minutes * 24 hours. If `replace`
  is specified, it is a dictionary of datetime attributes to replace
  after all other modifications have been made.

  For example, the following will return the epoch timestamp in
  Anchorage, AK, USA for tomorrow at 3 PM local time:

  .. code:: python

    epoch.sod(offset=1, tz='America/Anchorage', replace=dict(hour=15))

  '''
  tz = getTz(tz)
  if ts is None:
    ts = now()
  offset = int(offset or 0)
  ret = dtreplace(ts2dt(ts, tz=tz), hour=0, minute=0, second=0, microsecond=0)
  if offset:
    ret = tzcorrect(ret + timedelta(days=offset))
  if replace:
    ret = dtreplace(ret, **replace)
  return dt2ts(ret)

#------------------------------------------------------------------------------
def sow(ts=None, tz=None, offset=None, day=None, replace=None):
  '''
  Returns the epoch timestamp of the start of the current Gregorian
  week relative to the timezone `tz`. If `ts` is specified, the start
  of the week containing `ts` is returned. If `offset` is specified,
  it is taken to be an integral number of weeks to offset the returned
  value by. Note that due to leap days, leap seconds, daylight
  savings, etc, this is more complex than just 60 seconds * 60 minutes
  * 24 hours * 7 days. If `day` is specified, it specifies which day
  is defined to be the "first" day of the week, where ``0`` (the
  default) is Monday through ``6`` being Sunday. If `replace` is
  specified, it is a dictionary of datetime attributes to replace
  after all other modifications have been made (see `sod` for
  examples).
  '''
  tz = getTz(tz)
  if ts is None:
    ts = now()
  offset = int(offset or 0)
  ret = dtreplace(ts2dt(ts, tz=tz), hour=0, minute=0, second=0, microsecond=0)
  day = min(max(int(day or 0), 0), 6)
  if day <= ret.weekday():
    doff = day - ret.weekday()
  else:
    doff = day - ret.weekday() - 7
  if doff:
    ret += timedelta(days=doff)
  if offset:
    ret += timedelta(weeks=offset)
  if doff or offset:
    # NOTE: this call to `dtreplace` causes a dt.tzinfo correction
    #       because `datetime.datetime` behaves incorrectly when it is
    #       forced to cross DST boundaries...
    ret = tzcorrect(ret)
  if replace:
    ret = dtreplace(ret, **replace)
  return dt2ts(ret)

#------------------------------------------------------------------------------
def som(ts=None, tz=None, offset=None, replace=None):
  '''
  Returns the epoch timestamp of the start of the current Gregorian
  month relative to the timezone `tz`. If `ts` is specified, the start
  of the month containing `ts` is returned. If `offset` is specified,
  it is taken to be an integral number of months to offset the
  returned value by. If `replace` is specified, it is a dictionary of
  datetime attributes to replace after all other modifications have
  been made (see `sod` for examples).
  '''
  tz = getTz(tz)
  if ts is None:
    ts = now()
  offset = int(offset or 0)
  ret = dtreplace(ts2dt(ts, tz=tz), day=1, hour=0, minute=0, second=0, microsecond=0)
  if offset:
    # todo: all of this is because timedelta() does not support
    #       ``months=X``... is there perhaps another alternative?
    sign = 1 if offset > 0 else -1
    offset = abs(offset)
    if offset >= 12:
      ret = dtreplace(ret, year=ret.year + sign * ( offset // 12 ))
      offset %= 12
    if offset:
      year = ret.year
      month = ret.month + ( offset * sign )
      if month < 1:
        year -= 1
        month += 12
      elif month > 12:
        year += 1
        month -= 12
      ret = dtreplace(ret, year=year, month=month)
  if replace:
    ret = dtreplace(ret, **replace)
  return dt2ts(ret)

#------------------------------------------------------------------------------
def soy(ts=None, tz=None, offset=None, replace=None):
  '''
  Returns the epoch timestamp of the start of the current Gregorian
  year relative to the timezone `tz`. If `ts` is specified, the start
  of the year containing `ts` is returned. If `offset` is specified,
  it is taken to be an integral number of years to offset the returned
  value by. If `replace` is specified, it is a dictionary of datetime
  attributes to replace after all other modifications have been made
  (see `sod` for examples).
  '''
  tz = getTz(tz)
  if ts is None:
    ts = now()
  offset = int(offset or 0)
  ret = dtreplace(ts2dt(ts, tz=tz), month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
  if offset:
    ret = dtreplace(ret, year=ret.year + offset)
  if replace:
    ret = dtreplace(ret, **replace)
  return dt2ts(ret)

#------------------------------------------------------------------------------
def ts2age(ts, origin=None, tz=None):
  '''
  Returns the age, expressed as a floating point number of years, of
  timestamp `ts` relative to the starting timestamp `origin` (defaults
  to the current time), and evaluated in timezone `tz` (defaults to
  UTC).

  Example:

  .. code:: python

    >>> import epoch
    >>> epoch.ts2age(epoch.parse('2009-02-13T23:31:30Z'), origin=epoch.parse('2008-02-13T23:31:30Z'))
    1.0

  '''
  if origin is None:
    origin = now()
  if ts is None:
    return None
  tz = getTz(tz)
  ts = ts2dt(ts, tz=tz)
  at = ts2dt(origin, tz=tz)
  ret = 0
  if ts.microsecond != at.microsecond:
    ret += ts.microsecond - at.microsecond
  ret /= 1000000.0
  if ts.second != at.second:
    ret += ts.second - at.second
  ret /= 60.0
  if ts.minute != at.minute:
    ret += ts.minute - at.minute
  ret /= 60.0
  if ts.hour != at.hour:
    ret += ts.hour - at.hour
  ret /= 24.0
  if ts.day != at.day:
    ret += ts.day - at.day
  ret /= ( DAYSPERYEAR / 12.0 )
  if ts.month != at.month:
    ret += ts.month - at.month
  ret /= 12.0
  if ts.year != at.year:
    ret += ts.year - at.year
  return ret

#------------------------------------------------------------------------------
def age2ts(age, origin=None, tz=None):
  '''
  Returns the timestamp of the floating point number of years `age`
  relative to the starting timestamp `origin` (defaults to the current
  time), and evaluated in timezone `tz` (defaults to UTC).

  Example:

  .. code:: python

    >>> import epoch
    >>> epoch.zulu(epoch.age2ts(2.5, origin=epoch.parse('2008-02-13T23:31:30Z')))
    2010-08-13T23:31:30Z

  '''
  if origin is None:
    origin = now()
  if age is None:
    return None
  at = ts2dt(origin, tz=getTz(tz))
  if math.trunc(age) != 0:
    at = at.replace(year=at.year + math.trunc(age))
    age -= math.trunc(age)
  age *= 12.0
  if math.trunc(age) != 0:
    mn = at.month + math.trunc(age)
    yr = at.year
    if mn < 1:
      mn += 12
      yr -= 1
    if mn > 12:
      mn -= 12
      yr += 1
    at = at.replace(year=yr, month=mn)
    age -= math.trunc(age)
  age *= ( DAYSPERYEAR / 12.0 )
  at = at + timedelta(days=age)
  return dt2ts(at)

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
