
# %% [markdown] #
# %% https://www.index.go.kr/potal/main/EachDtlPageDetail.do?idx_cd=1086
# %% 주기를 월호 새서 다운로드한다. (2001년 1월~) # 보유금액 >
# %% 유가증권시장 사용 # (1) 한달 lag(shift(1)) 한다.  # - 1월의
# %% 데이터가 1월 마지막날 데이터이고 2월 1일 리밸런싱시에 사용하기
# %% 위함
외국인수급 = pd.read_csv('data/외국인수급.csv') 외국인수급 =
외국인수급.set_index('Date').T 외국인수급.index =
pd.to_datetime(외국인수급.index, format="%Y%m월")
# 외국인수급 =
# 외국인수급.resample('D').first().fillna(method='ffill')[['유가증권시장']]
외국인수급 = 외국인수급[['유가증권시장']] 외국인수급.columns = ['kospi']
외국인수급['kospi'] = 외국인수급['kospi'].astype('float') 외국인수급 =
외국인수급.shift(1) # --- (1)
# %%
외국인수급['1m'] = 외국인수급['kospi'].pct_change(1) 외국인수급['2m']
= 외국인수급['kospi'].pct_change(1).shift(1) 외국인수급['3m'] =
외국인수급['kospi'].pct_change(1).shift(2) 외국인수급
# %% [markdown] # >외국인 코스피 수급을 이용하여 직전 3개월 **연속**
# %% 상승시 100%, 2개월 연속 상승시 66%, 1개월 연속 상승시 33%
# %% 비중으로 스위칭
#
# 블로그 문서대로 라면 아래처럼 계산해야 한다.
# %%
연속3개월 = ((외국인수급['3m'] > 0) & (외국인수급['2m'] > 0) &
(외국인수급['1m'] > 0)) 연속2개월 = ((외국인수급['2m'] > 0) &
(외국인수급['1m'] > 0)) 연속1개월 = (외국인수급['1m'] > 0)
target_weight = pd.DataFrame(np.where(연속3개월, 1.0,
np.where(연속2개월, 0.66, np.where(연속1개월, 0.33, 0))),
index=외국인수급.index, columns=['ams']) target_weight.head(20)
# %% # 3개월 연속 상승시 1점, 2개월 연속 상승시 1점, 1개월 상승시
# %%1점을 주고 평균으로 비중을 구했다.
tw = pd.DataFrame(np.where((외국인수급['3m']>0) & (외국인수급['2m']>0)
& (외국인수급['1m']>0), 1, 0), index=외국인수급.index, columns=['3m'])
tw['2m'] = np.where((외국인수급['2m']>0) & (외국인수급['1m']>0), 1, 0)
tw['1m'] = np.where(외국인수급['1m']>0, 1, 0) tw['ams'] =
(tw['1m']+tw['2m']+tw['3m']) / 3 tw.head(20)
# %%
ax = tw['ams'].plot(figsize=(16,6)); target_weight.plot(ax=ax);
ax.legend(loc="upper left");
# %%
target_weight['현금'] = 1.0 - target_weight target_weight.columns =
['base2', '현금'] target_weight.to_csv('한국Base2비중.csv')
target_weight['base2'].plot(figsize=(16,6), title='외국인수급 Loss Cut
Signals', legend=True);
# %%
tickers = list(prices.columns[:-4])#+['현금'] tickers
# %%
base2 = bt.Strategy('base2', algos = [
                    bt.algos.RunAfterDate('2002-1-2'),
                    bt.algos.RunMonthly(), bt.algos.SelectAll(),
                    bt.algos.SelectThese(tickers),
                    StatIDMomentumScore(lag=pd.DateOffset(days=0)),
                    bt.algos.SelectN(n=2, sort_descending=True),
                        # bt.algos.PrintDate(),
                        bt.algos.WeighEqually(),
                        # bt.algos.PrintTempData(),
                        bt.algos.Rebalance() ] )
# %%
bt_id2 = bt.Backtest(base2, prices) r_id2 = bt.run(bt_id2)
# %%
kbase2 = bt.Strategy('kbase2', algos = [
                    bt.algos.RunAfterDate('2002-1-2'),
                    bt.algos.RunMonthly(), bt.algos.PrintDate(),
                    bt.algos.SelectAll(),
                        #   bt.algos.SelectThese(tickers), 변동성
                        #   제어한 비중에 대한 dataframe
                          bt.algos.WeighTarget(target_weight),
                          # bt.algos.PrintTempData(),
                          bt.algos.Rebalance()], children = [base2,
                    '현금'] )
# %%
bt_kbase2 = bt.Backtest(kbase2, prices) r = bt.run(bt_id2, bt_kbase2)
# %%
r.set_date_range("2002-02-01") r.display()
# %%
r.get_security_weights('kbase2').plot.area(stacked=True, alpha=0.7,
legend=False, cmap='jet', figsize=(16,6));
# %%
ax = r.plot(figsize=(16,8));
(target_weight['base2']*1000).plot.area(ax=ax, label='signal');
(외국인수급['kospi']*10).plot(ax=ax, label='외국인수급');
plt.legend(loc="upper left");
# %%
r.prices.to_drawdown_series().plot.area(stacked=False, alpha=0.3,
figsize=(16, 6));
# %%
bt_kbase2.positions.to_csv('한국ID2상대모멘텀_포지션.csv')
