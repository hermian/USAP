prices = pd.read_csv('data/assets.csv', index_col=0, parse_dates=True)
tickers = list(prices.columns[:-4])+['현금']
#--
oecd = pd.read_csv("data/OECD.csv", index_col=0, parse_dates=True).rename_axis("Date")
oecd_MOM = oecd.resample('D').first().fillna(method='ffill') #전월비
target_weights1 = pd.DataFrame(np.where(oecd_MOM > 1, 1, 0), index=oecd_MOM.index)
target_weights1['현금'] = 1 - target_weights1
target_weights1.columns = ['base1', '현금'] # 'base1'은 위의 전략과 이름을 맞추어야 한다. '현금'도 prices의 컬럼이름과 맞추어야 한다.


kbase1 = bt.Strategy('kbase1',
                    algos = [
                        bt.algos.RunAfterDate('2002-1-2'),
                        bt.algos.RunMonthly(),
                        bt.algos.SelectAll(),
                        bt.algos.SelectThese(tickers),
                        StatIDAverageMomentumScore(lag=pd.DateOffset(days=0), cash='현금'),
                        bt.algos.SelectN(n=1, sort_descending=True),
                        # bt.algos.PrintDate(),
                        WeighEquallyWithoutCash(target_weights1, cash='현금'),
                        # bt.algos.PrintTempData(),
                        bt.algos.Rebalance()
                    ],
                     children=tickers,
                     # parent=kbase123
                    )
#--
외국인수급 = pd.read_csv('data/외국인수급.csv')
외국인수급 = 외국인수급.set_index('Date').T
외국인수급.index = pd.to_datetime(외국인수급.index, format="%Y%m월")
# 외국인수급 = 외국인수급.resample('D').first().fillna(method='ffill')[['유가증권시장']]
# 외국인수급.columns = ['kospi']
외국인수급 = 외국인수급[['유가증권시장']]
외국인수급.columns = ['kospi']
외국인수급['kospi'] = 외국인수급['kospi'].astype('float')
외국인수급 = 외국인수급.shift(1)
외국인수급['1m'] = 외국인수급['kospi'].pct_change(1)
외국인수급['2m'] = 외국인수급['kospi'].pct_change(1).shift(1)
외국인수급['3m'] = 외국인수급['kospi'].pct_change(1).shift(2)
연속3개월 = ((외국인수급['3m'] > 0) & (외국인수급['2m'] > 0) & (외국인수급['1m'] > 0))
연속2개월 = ((외국인수급['2m'] > 0) & (외국인수급['1m'] > 0))
연속1개월 = (외국인수급['1m'] > 0)
target_weights2 = pd.DataFrame(np.where(연속3개월, 1.0, 
                                      np.where(연속2개월, 0.66, 
                                               np.where(연속1개월, 0.33, 0))), 
                             index=외국인수급.index, columns=['base2'])
target_weights2['현금'] = 1.0 - target_weights2
target_weights2.columns = ['base2', '현금']

kbase2 = bt.Strategy('kbase2',
                    algos = [
                        bt.algos.RunAfterDate('2002-1-2'),
                        bt.algos.RunMonthly(),
                        bt.algos.SelectAll(),
                        bt.algos.SelectThese(tickers),
                        StatIDAverageMomentumScore(lag=pd.DateOffset(days=0), cash='현금'),
                        bt.algos.SelectN(n=2, sort_descending=True),
                        # bt.algos.PrintDate(),
                        WeighEquallyWithoutCash(target_weights2, cash='현금'),
                        # bt.algos.PrintTempData(),
                        bt.algos.Rebalance()
                    ],
                    children=tickers,
                    # parent=kbase123
                    )
#--                                        
def AMS(x):
    ''' x : Series (DataFrame의 컬럼)
        x[-1] : 기준일. x의 현재값
        (오늘날짜/과거날짜 - 1) > 0 보다 크면 1, 아니면 0
        => 오늘날짜/과거날짜 > 1 => 오늘날짜 > 과거날짜  => x[-1] > x
    '''
    # print(f"{list(np.where(x[-1]>x, 1, 0)[:-1])}, {len(np.where(x[-1]>x, 1, 0)[:-1])}")
    return np.mean(np.where(x[-1]>x, 1, 0)[:-1]) # 당일 날짜 비교는 제외해준다 [:-1]    
c='코스피200'
target_weights3 = pd.DataFrame()
target_weights3['base3'] = prices[c].rolling(365).apply(AMS)
target_weights3['현금'] = 1.0 - target_weights3
target_weights3.columns = ['base3', '현금']

kbase3 = bt.Strategy('kbase3',
                    algos = [
                        bt.algos.RunAfterDate('2002-1-2'),
                        bt.algos.RunMonthly(),
                        bt.algos.SelectAll(),
                        bt.algos.SelectThese(tickers),
                        StatIDAverageMomentumScore(lag=pd.DateOffset(days=0), cash='현금'),
                        bt.algos.SelectN(n=3, sort_descending=True),
                        # bt.algos.PrintDate(),
                        WeighEquallyWithoutCash(target_weights3, cash='현금'),
                        # bt.algos.PrintTempData(),
                        bt.algos.Rebalance()
                    ],
                    children=tickers,
                    # parent = kbase123
                    )
# --
kbase123 = bt.Strategy('kbase123', 
                    algos = [
                          bt.algos.RunAfterDate('2002-1-2'),
                          bt.algos.RunMonthly(),
                          # bt.algos.PrintDate(),
                          bt.algos.SelectAll(),
                        #   bt.algos.SelectThese(tickers),
                        # 변동성 제어한 비중에 대한 dataframe
                          bt.algos.WeighEqually(),
                          # bt.algos.PrintTempData(),
                          bt.algos.Rebalance()],
                    children = [kbase1, kbase2, kbase3]
                       # children = ['현금']
                   )

#--
target_weights4 = pd.DataFrame()
for c in ["나스닥100", "다우"]:
    target_weights4[c] = prices[c].rolling(365).apply(AMS)
target_weights4 = target_weights4*0.5    
target_weights4['달러'] = 1.0 - target_weights4.sum(axis=1)

나스닥다우동일비중AMS = bt.Strategy('나스닥다우동일비중AMS',
                    algos = [
                        bt.algos.RunAfterDate('2002-1-2'),
                        bt.algos.RunMonthly(),
                        bt.algos.SelectThese(['나스닥100', '다우', '달러']),
                        bt.algos.WeighTarget(target_weights4),
                        # WeighEquallyWithoutCash(target_weights, cash='현금'),
                        # bt.algos.PrintTempData(),
                        bt.algos.Rebalance()
                    ]
                    )
# --                                                               
통합 = bt.Strategy('통합', 
                    algos = [
                          bt.algos.RunAfterDate('2002-1-2'),
                          bt.algos.RunMonthly(),
                          # bt.algos.PrintDate(),
                          bt.algos.SelectAll(),
                        #   bt.algos.SelectThese(tickers),
                        # 변동성 제어한 비중에 대한 dataframe
                          bt.algos.WeighEqually(),
                          # bt.algos.PrintTempData(),
                          bt.algos.Rebalance()],
                    # children = [kbase123, 나스닥다우동일비중AMS]
) 
#--
bt_kbase1 = bt.Backtest(kbase1, prices)
bt_kbase2 = bt.Backtest(kbase2, prices)
bt_kbase3 = bt.Backtest(kbase3, prices)

prices_dollar = pd.read_csv('data/dollar_assets.csv', index_col=0, parse_dates=True)
bt_나스닥다우동일비중AMS = bt.Backtest(나스닥다우동일비중AMS, prices_dollar)

bt_kbase123 = bt.Backtest(kbase123, prices)

r1 = bt.run(bt_나스닥다우동일비중AMS)
r2 = bt.run(bt_kbase123)
#--
data = bt.merge(r1['나스닥다우동일비중AMS'].prices, r2['kbase123'].prices)
data.head()
#--
bt_통합 = bt.Backtest(통합, data)
r3 = bt.run(bt_통합)
r3.set_date_range("2002-02-01")
r3.display()
#--
r_all = bt.run(bt_kbase1, bt_kbase2, bt_kbase3, bt_통합)
r_all.set_date_range("2002-02-01")
r_all.display()
