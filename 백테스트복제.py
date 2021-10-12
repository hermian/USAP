# %%
import numpy as np
import pandas as pd
# %%
prices = pd.read_csv('raw_utf8.csv', index_col=0, parse_dates=True)
# %% [markdown]
# ## 백테스트.py의 평균수익률 계산
# %%
# 백테스트.py의 평균수익률 계산
m6 = (prices.pct_change(182-30) + 1).shift(30)
m9 = (prices.pct_change(273-30) + 1).shift(30)
m12 = (prices.pct_change(365-30) + 1).shift(30)
평균수익률 = (m6+m9+m12)/3
평균수익률
# %% [markdown]
# ## 이산성 및 IDM 계산

# %%
이산성시그널_df = prices.pct_change(30)\
                    .apply(lambda x: pd.Series(np.where(x>0.0, 1, 0), index=x.index))
이산성시그널_df
# %%
상승일비중 = 이산성시그널_df.rolling(366).mean()
상승일비중
# %%
하락일비중 = 1 - 상승일비중
하락일비중
# %%
이산성 = (하락일비중-상승일비중) * -1
이산성
# %%
IDM = 평균수익률 * 이산성
IDM
# %%


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
 # %%     
def bt_SectorIDMomentum(name, n, tickers, prices):
    st = bt.Strategy(name,
                      algos = [
                          bt.algos.RunAfterDate('2002-1-2'),
                          bt.algos.RunMonthly(),
                          bt.algos.SelectAll(),
                          bt.algos.SelectThese(tickers),
                          StatIDMomentumScore(lag=pd.DateOffset(days=0)),
                          bt.algos.SelectN(n=n, sort_descending=True),
                          # bt.algos.PrintDate(),
                          bt.algos.WeighEqually(),
                          # bt.algos.PrintTempData(),
                          bt.algos.Rebalance()
                      ],
                     )
    return bt.Backtest(st, prices)
# %%
tickers = list(prices.columns[:-4])#+['현금']
bt_id1 = bt_SectorIDMomentum("base1.ID상대모멘텀", n=1, tickers=tickers, prices=prices)
bt_id2 = bt_SectorIDMomentum("base2.ID상대모멘텀", n=2, tickers=tickers, prices=prices)
bt_id3 = bt_SectorIDMomentum("base3.ID상대모멘텀", n=3, tickers=tickers, prices=prices)
# %%
r = bt.run(bt_id1, bt_id2, bt_id3)
# %%
r.set_date_range("2002-02-01")
r.display()
