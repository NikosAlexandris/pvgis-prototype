from pandas import DatetimeIndex, Timestamp
from numpy import array as numpy_array

from pvgisprototype import FractionalYear
from pvgisprototype.constants import RADIANS

cases = [
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2024, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2023, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2022, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2021, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2018, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2017, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2016, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2015, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2014, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2013, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2012, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.952753750914997], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2011, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2010, month=6, day=21, hour=12)])
    },
     FractionalYear(value=numpy_array([2.9436292808978335], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=0)])
    },
     FractionalYear(value=numpy_array([6.257434547723932], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=12, day=31, hour=23)])
    },
     FractionalYear(value=numpy_array([6.2738864218206], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2020, month=1, day=1, hour=0)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=0)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=1)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=2)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=3)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=4)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=5)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=6)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=7)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=8)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=9)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=10)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=11)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=12)])
    },
     FractionalYear(value=numpy_array([0.0], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=13)])
    },
     FractionalYear(value=numpy_array([0.0007172585967099984], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=14)])
    },
     FractionalYear(value=numpy_array([0.0014345171934199968], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=15)])
    },
     FractionalYear(value=numpy_array([0.002151775790129995], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=16)])
    },
     FractionalYear(value=numpy_array([0.0028690343868399935], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=17)])
    },
     FractionalYear(value=numpy_array([0.003586292983549992], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=18)])
    },
     FractionalYear(value=numpy_array([0.00430355158025999], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=19)])
    },
     FractionalYear(value=numpy_array([0.005020810176969989], dtype='float32'), unit=RADIANS)),
    ({
        "timestamps": DatetimeIndex([Timestamp(year=2019, month=1, day=1, hour=20)])
    },
     FractionalYear(value=numpy_array([0.005738068773679987], dtype='float32'), unit=RADIANS)),
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
