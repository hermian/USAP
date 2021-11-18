import numpy as np
import pandas as pd
import bt


# 백테스팅을 위한 전략 클래스 작성
class StatIDAverageMomentumScore(bt.Algo):
    def __init__(self, lookback=pd.DateOffset(months=13), #FIXME : 12개월이되어야 하지만 원 알고리즘을 테스트한다.
                       lag=pd.DateOffset(months=1),
                       cash='현금'):
        super(StatIDAverageMomentumScore, self).__init__()
        self.lookback = lookback
        self.lag = lag
        self.cash = cash

    def __call__(self, target):
        selected = target.temp['selected'].copy()
        if self.cash in selected:
#             print('cash:', self.cash)
            selected.remove(self.cash) # ID Mementum을 구할때 제외하고 구해야 한다.방어코드
        
        t0 = target.now - self.lag
        prc = target.universe.loc[t0-self.lookback:t0,selected]
#         print(prc)

        m1 = t0 - pd.DateOffset(months=1)
        m6 = t0 - pd.DateOffset(months=6)
        m9 = t0 - pd.DateOffset(months=9)
        m12 = t0 - pd.DateOffset(years=1)
        
        m6_returns = (prc.loc[m6:m1,:].calc_total_return()+1) # 1달제외 6개월 수익률 (현재 prices가 공휴일포함 데이터임)
        m9_returns = (prc.loc[m9:m1,:].calc_total_return()+1) # 1달제외 9개월 수익률
        m12_returns = (prc.loc[m12:m1,:].calc_total_return()+1)  # 1달제외 12개월 수익률
        average_returns = (m6_returns+m9_returns+m12_returns)/3

        # ID 계산 최근 30일 제외
        # dropna에 주의 해야 한다. 조선이 0이 있어 문제가 되므로 모든 column이 nan일 때만 drop한다.
        m13 = t0 - pd.DateOffset(months=13)
        len_m1= len(prc.loc[m1:,:])-1
        #print(f"{t0}, {m1}, {m6}, {m9}, {m12}, {m13}")
        pos_percent = np.where(prc.loc[m13:,:].pct_change(len_m1).dropna(how='all') > 0.0, 1, 0).mean(axis=0)
        neg_percent = 1 - pos_percent
        ID = (neg_percent - pos_percent)
        # print(f"ID===\n{ID}")

        target.temp['stat'] = average_returns * ID * -1
        return True
    
class StatIDAverageMomentumScoreOrig(bt.Algo):
    def __init__(self, lookback=pd.DateOffset(years=2), #FIXME : 12개월이되어야 하지만 원 알고리즘을 테스트한다.
                       lag=pd.DateOffset(months=1),
                       cash='현금'):
        super(StatIDAverageMomentumScore, self).__init__()
        self.lookback = lookback
        self.lag = lag
        self.cash = cash

    def __call__(self, target):
        selected = target.temp['selected'].copy()
        if self.cash in selected:
            selected.remove(self.cash) # ID Mementum을 구할때 제외하고 구해야 한다.방어코드

        t0 = target.now - self.lag
        # prc = target.universe.loc[(t0 - self.lookback):t0,selected] # FIXME 12개월치의 데이터를 뽑는다.
        prc = target.universe.loc[t0-self.lookback:t0,selected]
        # print(t0, prc.iloc[-365:-30])
        #6, 9, 12개월 수익률 평균 계산
        # print(prc.iloc[-183:-30])

        #2002.2.1 -> 2002.1.2 -> 2001.8.3 -> 2001.5.4 -> 2001.2.1
        #백테트.py와 맞춘 수익률
        m6_returns = (prc.iloc[-183:-30].calc_total_return()+1) # 1달제외 6개월 수익률 (현재 prices가 공휴일포함 데이터임)
        m9_returns = (prc.iloc[-274:-30].calc_total_return()+1) # 1달제외 9개월 수익률
        m12_returns = (prc.iloc[-366:-30].calc_total_return()+1)  # 1달제외 12개월 수익률
        average_returns = (m6_returns+m9_returns+m12_returns)/3
        # print(f"{t0}\n===average_returns : \n{average_returns}\n")

        # ID 계산
        # dropna에 주의 해야 한다. 조선이 0이 있어 문제가 되므로 모든 column이 nan일 때만 drop한다.
        # print(prc[-(365+30):])
        # print(f"{t0} len {len(prc[-(366+30):].pct_change(30).dropna(how='all'))}")
        pos_percent = np.where(prc[-(366+30):].pct_change(30).dropna(how='all') > 0.0, 1, 0).mean(axis=0)
        neg_percent = 1 - pos_percent
        ID = (neg_percent - pos_percent)
        # print(f"ID===\n{ID}")

        target.temp['stat'] = average_returns * ID * -1
        return True

class WeighEquallyWithoutCash(bt.Algo):
    ''' cash에 대한 비중을 별도로 받아서, cash를 제외한 selected는 cash 비중 빼고 동일 비중으로 할당한다.

    :param cash_weights: 현금 비중 데이터 프레임 (다른 비중이 같이 있어도 된다. cash 변수 값을 열이름으로 사용)
    :param cash: cash 자원의 이름 (ex, '현금', 'AGG', 'SHY'등)
    :param lag: cash_weights 데이터프레임에서 비중을 추출할때 얼마만큼 lag를 할 것인지를 결정
    '''
    def __init__(self,  cash_weights, cash='현금', lag=pd.DateOffset(days=0)):
        super(WeighEquallyWithoutCash, self).__init__()
        self.cash = cash
        self.cash_weights = cash_weights # pd.DataFrame
        self.lag = lag

    def __call__(self, target):
        selected = target.temp['selected']
        if self.cash in selected:
            raise ValueError(f"selected 자산에 {self.cash}는 없어야 합니다.")
            # ID Mementum을 구할때 제외하고 구해야 한다. (방어코드)

        t0 = target.now - self.lag
        cash_weight = self.cash_weights.loc[t0, self.cash]
        others_weights= 1.0 - cash_weight # selected의 비중

        w = others_weights/len(selected) # 동일비중
        weights = {x: w for x in selected}
        weights[self.cash] = cash_weight # 현금비중추가

        target.temp['weights'] = weights
        target.temp['selected'] = selected + [self.cash] #selected에 현금 추가

        return True

