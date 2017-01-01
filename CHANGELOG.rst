=========
ChangeLog
=========


v0.1.4
======

* Fixed `epoch.parse` to support long integer types in Python 2
* Fixed `epoch.parse` handling of microseconds


v0.1.3
======

* Added functions `epoch.age2ts` and `epoch.ts2age` for converting
  between years of age and epoch timestamps
* Added `tsreplace` helper function
* Added `replace` parameter to `sod`, `sow`, `som`, and `soy`


v0.1.2
======

* Added `epoch.parse`, a slightly generalized form of
  `epoch.parseZulu`


v0.1.1
======

* First public release
