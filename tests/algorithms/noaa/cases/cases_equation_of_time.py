from pandas import DatetimeIndex, Timestamp
from numpy import array as numpy_array

from pvgisprototype import EquationOfTime
from pvgisprototype.constants import MINUTES

cases = [
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2024, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2023, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2022, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2021, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2018, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2017, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2016, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2015, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2014, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2013, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2012, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2011, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2010, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=0, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.228653953567693], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=23, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.661151242990388], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=1, day=1, hour=0, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=0, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=1, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=2, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=3, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=4, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=5, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=6, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=7, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=8, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=9, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=10, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=11, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=12, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=13, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.9228681040071374], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=18, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-3.016262676320302], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=14, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.941560545255244], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=15, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.9602462534168086], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=16, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.9789251981785085], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=17, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-2.997597349241264], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=18, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-3.016262676320302], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=19, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-3.034921149145207], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-3.053572737459987], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-3.053572737459987], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20, minute=0, second=0)]),
    },
     EquationOfTime(value=numpy_array([-3.053572737459987], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=1990, month=2, day=5, hour=9, minute=24, second=16)]),
    },
     EquationOfTime(value=numpy_array([-13.722002783024868], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=1990, month=3, day=3, hour=18, minute=17, second=6)]),
    },
     EquationOfTime(value=numpy_array([-12.487510992053137], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=1997, month=3, day=5, hour=17, minute=0, second=28)]),
    },
     EquationOfTime(value=numpy_array([-12.087579478519087], dtype='float32'), unit=MINUTES)),
]
cases_ids = [
    'Input: 2024-6-21 12:0:0',
    'Input: 2023-6-21 12:0:0',
    'Input: 2022-6-21 12:0:0',
    'Input: 2021-6-21 12:0:0',
    'Input: 2020-6-21 12:0:0',
    'Input: 2019-6-21 12:0:0',
    'Input: 2018-6-21 12:0:0',
    'Input: 2017-6-21 12:0:0',
    'Input: 2016-6-21 12:0:0',
    'Input: 2015-6-21 12:0:0',
    'Input: 2014-6-21 12:0:0',
    'Input: 2013-6-21 12:0:0',
    'Input: 2012-6-21 12:0:0',
    'Input: 2011-6-21 12:0:0',
    'Input: 2010-6-21 12:0:0',
    'Input: 2020-12-31 0:0:0',
    'Input: 2020-12-31 23:0:0',
    'Input: 2020-1-1 0:0:0',
    'Input: 2019-1-1 0:0:0',
    'Input: 2019-1-1 1:0:0',
    'Input: 2019-1-1 2:0:0',
    'Input: 2019-1-1 3:0:0',
    'Input: 2019-1-1 4:0:0',
    'Input: 2019-1-1 5:0:0',
    'Input: 2019-1-1 6:0:0',
    'Input: 2019-1-1 7:0:0',
    'Input: 2019-1-1 8:0:0',
    'Input: 2019-1-1 9:0:0',
    'Input: 2019-1-1 10:0:0',
    'Input: 2019-1-1 11:0:0',
    'Input: 2019-1-1 12:0:0',
    'Input: 2019-1-1 13:0:0',
    'Input: 2019-1-1 18:0:0',
    'Input: 2019-1-1 14:0:0',
    'Input: 2019-1-1 15:0:0',
    'Input: 2019-1-1 16:0:0',
    'Input: 2019-1-1 17:0:0',
    'Input: 2019-1-1 18:0:0',
    'Input: 2019-1-1 19:0:0',
    'Input: 2019-1-1 20:0:0',
    'Input: 2019-1-1 20:0:0',
    'Input: 2019-1-1 20:0:0',
    'Input: 1990-2-5 9:24:16',
    'Input: 1990-3-3 18:17:6',
    'Input: 1997-3-5 17:0:28',
]
