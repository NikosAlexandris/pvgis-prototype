from pandas import DatetimeIndex, Timestamp
from numpy import array as numpy_array

from pvgisprototype import EquationOfTime
from pvgisprototype.constants import MINUTES

cases = [
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2024, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2023, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2022, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2021, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2018, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2017, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2016, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2015, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2014, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2013, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2012, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.4444366080232545], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2011, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2010, month=6, day=21, hour=12)])
    },
     EquationOfTime(value=numpy_array([-1.3282368002224763], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=0)])
    },
     EquationOfTime(value=numpy_array([-2.228653953567693], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=23)])
    },
     EquationOfTime(value=numpy_array([-2.661151242990388], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=1, day=1, hour=0)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=0)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=1)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=2)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=3)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=4)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=5)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=6)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=7)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=8)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=9)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=10)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=11)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=12)])
    },
     EquationOfTime(value=numpy_array([-2.90416896], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=13)])
    },
     EquationOfTime(value=numpy_array([-2.9228681040071374], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=14)])
    },
     EquationOfTime(value=numpy_array([-2.941560545255244], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=15)])
    },
     EquationOfTime(value=numpy_array([-2.9602462534168086], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=16)])
    },
     EquationOfTime(value=numpy_array([-2.9789251981785085], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=17)])
    },
     EquationOfTime(value=numpy_array([-2.997597349241264], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=18)])
    },
     EquationOfTime(value=numpy_array([-3.016262676320302], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=19)])
    },
     EquationOfTime(value=numpy_array([-3.034921149145207], dtype='float32'), unit=MINUTES)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20)])
    },
     EquationOfTime(value=numpy_array([-3.053572737459987], dtype='float32'), unit=MINUTES)),
]
cases_ids = [
    'Input: 2024-6-21 12:00:00',
    'Input: 2023-6-21 12:00:00',
    'Input: 2022-6-21 12:00:00',
    'Input: 2021-6-21 12:00:00',
    'Input: 2020-6-21 12:00:00',
    'Input: 2019-6-21 12:00:00',
    'Input: 2018-6-21 12:00:00',
    'Input: 2017-6-21 12:00:00',
    'Input: 2016-6-21 12:00:00',
    'Input: 2015-6-21 12:00:00',
    'Input: 2014-6-21 12:00:00',
    'Input: 2013-6-21 12:00:00',
    'Input: 2012-6-21 12:00:00',
    'Input: 2011-6-21 12:00:00',
    'Input: 2010-6-21 12:00:00',
    'Input: 2020-12-31 0:00:00',
    'Input: 2020-12-31 23:00:00',
    'Input: 2020-1-1 0:00:00',
    'Input: 2019-1-1 0:00:00',
    'Input: 2019-1-1 1:00:00',
    'Input: 2019-1-1 2:00:00',
    'Input: 2019-1-1 3:00:00',
    'Input: 2019-1-1 4:00:00',
    'Input: 2019-1-1 5:00:00',
    'Input: 2019-1-1 6:00:00',
    'Input: 2019-1-1 7:00:00',
    'Input: 2019-1-1 8:00:00',
    'Input: 2019-1-1 9:00:00',
    'Input: 2019-1-1 10:00:00',
    'Input: 2019-1-1 11:00:00',
    'Input: 2019-1-1 12:00:00',
    'Input: 2019-1-1 13:00:00',
    'Input: 2019-1-1 14:00:00',
    'Input: 2019-1-1 15:00:00',
    'Input: 2019-1-1 16:00:00',
    'Input: 2019-1-1 17:00:00',
    'Input: 2019-1-1 18:00:00',
    'Input: 2019-1-1 19:00:00',
    'Input: 2019-1-1 20:00:00',
]
