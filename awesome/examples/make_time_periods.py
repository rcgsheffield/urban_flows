import datetime

import ufdex

START = datetime.datetime(2020, 1, 1, 10, 1, 3)
END = datetime.datetime(2020, 1, 5, 10, 1, 4)

if __name__ == '__main__':
    query = ufdex.UrbanFlowsQuery(time_period=[START, END])

    for time_period in query.time_periods(freq=datetime.timedelta(days=1)):
        print(*(t.isoformat() for t in time_period), sep='\t')
