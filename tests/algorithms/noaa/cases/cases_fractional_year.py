from pandas import DatetimeIndex, Timestamp
from numpy import array as numpy_array

from pvgisprototype import FractionalYear
from pvgisprototype.constants import RADIANS

cases = [
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2024, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2023, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2022, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2021, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2018, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2017, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2016, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2015, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2014, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2013, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2012, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2011, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2010, month=6, day=21, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=0, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([6.257434547723932], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=23, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([6.2738864218206], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=1, day=1, hour=0, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=0, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=1, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=2, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=3, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=4, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=5, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=6, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=7, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=8, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=9, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=10, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=11, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=12, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=13, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0007172585967099984], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=18, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.00430355158025999], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=14, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0014345171934199968], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=15, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.002151775790129995], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=16, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.0028690343868399935], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=17, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.003586292983549992], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=18, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.00430355158025999], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=19, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.005020810176969989], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.005738068773679987], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.005738068773679987], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20, minute=0, second=0)]),
    },
     FractionalYear(value=numpy_array([0.005738068773679987], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=1990, month=2, day=5, hour=9, minute=24, second=16)]),
    },
     FractionalYear(value=numpy_array([0.6003454454462687], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=1990, month=3, day=3, hour=18, minute=17, second=6)]),
    },
     FractionalYear(value=numpy_array([1.0543701371636975], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=1997, month=3, day=5, hour=17, minute=0, second=28)]),
    },
     FractionalYear(value=numpy_array([1.0880812912090676], dtype='float32'), unit=RADIANS)),
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
