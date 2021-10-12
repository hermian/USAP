import numpy as np
import pandas as pd
import bt


# 백테스팅을 위한 전략 클래스 작성
class StatIDMomentumScore(bt.Algo):
    def __init__(self, lookback=pd.DateOffset(years=2), #FIXME : 12개월이되어야 하지만 원 알고리즘을 테스트한다.
                 lag=pd.DateOffset(months=1)):
        super(StatIDMomentumScore, self).__init__()
        self.lookback = lookback
        self.lag = lag

    def __call__(self, target):
        selected = target.temp['selected']
        t0 = target.now - self.lag
        # prc = target.universe.loc[(t0 - self.lookback):t0,selected] # FIXME 12개월치의 데이터를 뽑는다.
        prc = target.universe.loc[t0-self.lookback:t0,selected]
        # print(t0, prc.iloc[-365:-30])
        #6, 9, 12개월 평균모멘텀스코어
        # print(prc.iloc[-183:-30])

        #2002.2.1 -> 2002.1.2 -> 2001.8.3 -> 2001.5.4 -> 2001.2.1
        #백테트.py와 맞춘 수익률
        m6_returns = (prc.iloc[-183:-30].calc_total_return()+1) # 1달제외 6개월 수익률 (현재 prices가 공휴일포함 데이터임)
        m9_returns = (prc.iloc[-274:-30].calc_total_return()+1) # 1달제외 9개월 수익률
        m12_returns = (prc.iloc[-366:-30].calc_total_return()+1)  # 1달제외 12개월 수익률
        average_returns = (m6_returns+m9_returns+m12_returns)/3
        # print(f"{t0}\n===average_returns : \n{average_returns}\n")

        # ID 계산 최근 30일 제외
        # dropna에 주의 해야 한다. 조선이 0이 있어 문제가 되므로 모든 column이 nan일 때만 drop한다.
        # print(prc[-(365+30):])
        #print(f"{t0} len {len(prc[-(366+30):].pct_change(30).dropna(how='all'))}")
        pos_percent = np.where(prc[-(366+30):].pct_change(30).dropna(how='all') > 0.0, 1, 0).mean(axis=0)
        neg_percent = 1 - pos_percent
        ID = (neg_percent - pos_percent)
        # print(f"ID===\n{ID}")

        target.temp['stat'] = average_returns * ID * -1
        return True