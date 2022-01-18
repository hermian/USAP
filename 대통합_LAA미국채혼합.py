start_date = datetime(1950, 1, 1)
unrate = web.DataReader("UNRATE","fred",start_date)#,end_date)
unrate['12ma'] = unrate.rolling(12).mean()
unrate_shifted = unrate.shift(1)
us500 = yf.download('^GSPC')[['Adj Close']]
us500.columns = ['US500']
us500['200ma'] = us500['US500'].rolling(200).mean()
signal = bt.merge(us500, unrate_shifted)
signal = signal.fillna(method='ffill')
signal = signal['1993':].copy()
cond1 = (signal['US500'] < signal['200ma'])
cond2 = (signal['UNRATE'] > signal['12ma'])
signal['berish'] = (cond1 & cond2)
signal = signal.resample('D').fillna('ffill')
#%%
read_df = pd.read_csv('./data/laa_assets.csv', index_col=0, parse_dates=True)
cols = ['kodex200', 'us500_UH', 'gold_UH', 'usbond10y_UH', 'kbond10y', 'nasdaq100_UH', 'usdkrw'] # SHY대용 국내 ETF는?
price_df = read_df.loc[:, cols].dropna().copy()
price_df = price_df['2001':'2020-07-02'].copy()

# %%
class Config:
    ''' 설정
    
    자산군이 될수 있는 것은 stocks와 bonds만이다.
    gold는 gold, gold_H, gold_UH중 하나로 설정한다.
    defense와 offense는 1개 이어야 한다.
    bonds_weight는 dc일때 0.3으로 설정한다.

    KODX200미국채혼합은 안전자산이 되지만...복잡하네...
    '''
    signal_name = 'Growth_Trend'

    def __init__(self, stocks = {'us500_UH':0.25}, gold = {'gold_H': 0.25}, bonds={'usbond10y_UH':0.25}, 
                        defense = 'usdkrw', offense = 'nasdaq100_UH', is_dc=False, safe_limit=None, safe_assets=[]):
        self.stocks = stocks
        # self.stocks_weight = stocks_weight
        self.gold = gold
        self.bonds = bonds
        # self.bonds_weight = bonds_weight
        self.defense = defense
        self.offense = offense
        #-------- is_dc가 True일때만 의미 있음
        self.is_dc = is_dc
        self.safe_limit = safe_limit
        self.safe_assets = safe_assets

        assert(len(gold) == 1)
   
    @property
    def stocks_weight(self):
        w  = 0.0
        for k in self.stocks:
            w += self.stocks[k]
        return w

    @property
    def bonds_weight(self):
        w  = 0.0
        for k in self.bonds:
            w += self.bonds[k]
        return w

    @property
    def gold_weight(self):
        w  = 0.0
        for k in self.gold:
            w += self.gold[k]
        return w

    @property
    def switch_weight(self):
        w = 1 - self.stocks_weight - self.bonds_weight - self.gold_weight
        return w

    @property
    def tickers(self):
        return list(self.stocks) + list(self.gold) + list(self.bonds )+ [self.defense, self.offense]

    @property
    def berish_assets(self):
        return list(self.stocks) + list(self.gold) + list(self.bonds) + [self.defense]

    @property
    def bullish_assets(self):
        return list(self.stocks) + list(self.gold) + list(self.bonds) + [self.offense]

    @property
    def each_weight(self): # stock, bond제외한 2가지 자산 동일 비중
        return (1.0-self.bonds_weight-self.stocks_weight)/2

    @property
    def assets(self):
        dict3 = {**self.stocks, **self.bonds, **self.gold}
        dict3[self.defense] = self.switch_weight
        dict3[self.offense] = self.switch_weight
        return dict3

# %%
# signal은 해당 달은 모두 동일하다.
class WeighLAA(bt.Algo):
    def __init__(self, config):
        super(WeighLAA, self).__init__()
        self.signal_name = config.signal_name
        self.config = config
        print(self.config.bonds)

    def is_berish_and_depression(self, signal):
        return signal == True

    def is_dc(self):
        return self.config.is_dc

    def current_weights(self, target):
        weights = pd.Series()
        for cname in target.children:
            c = target.children[cname]
            weights[cname] = c.weight
        return weights

    def set_switching_weights(self, weights):
        ''' bonds 자산을 안전 자산으로 취급한다.'''
        안전자산비중 = 0.0
        for asset in self.config.safe_assets:
            안전자산비중 += weights[asset]

        print(f"안전자산비중 : {안전자산비중}, {self.config.safe_limit}")
        if 안전자산비중 < self.config.safe_limit: # fixme
            print(f"@@@@@@ {안전자산비중*100:.2f}% 반드시 안전자산 30% 만들어야 한다 {weights.sum()}@@@@@@")
            필요안전자산 = self.config.safe_limit - 안전자산비중 
            전체자산개수 = len(weights)
            안전자산개수 = len(self.config.safe_assets)
            차감할자산비중 = 필요안전자산/(전체자산개수 - 안전자산개수-1) # -1은 offense, defense가 1개
            print(f"필요({필요안전자산}), 전체({전체자산개수}), 안전({안전자산개수}), 차감({차감할자산비중})")

            # 안전자산 비중으로 설정
            # 기존비중에 1/n로 더해준다. => 이 경우 원래 안전자산의 비중이 동일비중이 아니라면 의도한바가 아닐수도 
            # => 비중만큼 증가 시켜준다.
            for ticker in self.config.safe_assets:
                weights[ticker] += (필요안전자산 * self.config.assets[ticker]/self.config.safe_limit)

            # 나머지 자산군에서 뺀다. 
            for ticker in weights.index:
                if ticker not in self.config.safe_assets:
                    weights[ticker] -= 차감할자산비중

    def __call__(self, target):
        t0 = target.now
        weights = self.current_weights(target) # 한국형으로 가지고 있다.
        # print(t0, weights.index, weights.values)
        signal = target.get_data(self.signal_name)
        if self.is_berish_and_depression(signal.loc[t0].values[0]): # SHY
            if self.config.offense in weights.index:
                if weights[self.config.offense] != 0.0: # QQQ에 투자중이라면
                    weights[self.config.defense] = weights[self.config.offense]
                    if self.is_dc():
                        print("나는 DC다 SHY")
                        self.set_switching_weights(weights)

                weights.drop(labels=[self.config.offense], inplace=True)
        else: # QQQ
            if self.config.defense in weights.index:
                if weights[self.config.defense] != 0: # SHY에 투자 중이라면
                    weights[self.config.offense] = weights[self.config.defense]
                    if self.is_dc():
                        print("나는 DC다 QQQ")
                        self.set_switching_weights(weights)

                weights.drop(labels=[self.config.defense], inplace=True)

        # 1년 한번 전체 비중을 맞춘다.
        if t0.month == 12:
            print("=======> 연말리밸런싱")
            for name in weights.index:
                weights[name] = self.config.assets[name]

        target.temp['weights'] = weights
        print(f"{target.now} ", end =" ")
        for i, v in weights.items():
            print(f"{i}:{v:.3f}", end=" ")
        print("")

        return True
#%%
class SelectAsset(bt.Algo):
    def __init__(self, config):
        super(SelectAsset, self).__init__()
        self.signal_name = config.signal_name
        self.config = config
        print(self.config.bonds)

    def is_berish_and_depression(self, signal):
        return signal == True

    def __call__(self, target):
        t0 = target.now
        signal = target.get_data(self.signal_name)

        if self.is_berish_and_depression(signal.loc[t0].values[0]):
            target.temp["selected"] = self.config.berish_assets
        else:
            target.temp["selected"] = self.config.bullish_assets

        # 최조 할당.
        weights = pd.Series()  
        for name in target.temp["selected"]:
            weights[name] = self.config.assets[name]

        target.temp['weights'] = weights

        return True
# %%
# START_DATE='1993-01-29'#'2004-11-18'
# once = bt.AlgoStack(#bt.algos.RunAfterDate('2004-11-29'),
#                     bt.algos.RunAfterDate('2002-1-2'),
#                     bt.algos.RunOnce(),
#                     bt.algos.PrintDate(),
#                     # bt.algos.SelectThese(['IWD', 'GLD', 'IEF', 'QQQ']), # FIXME: 2004-11-29일 하락장아님 QQQ선택 (signal을 보고 미리 선택했음)
#                     SelectAsset('Growth_Trend'),
#                     bt.algos.WeighEqually(),
#                     bt.algos.PrintTempData(),
#                     bt.algos.Rebalance())
# laa = bt.AlgoStack(
#     bt.algos.RunAfterDate('2002-1-2'),
#     bt.algos.RunMonthly(run_on_first_date=False, run_on_end_of_period=True),
#     bt.algos.PrintDate(),
#     bt.algos.SelectAll(),
#     WeighLAA('Growth_Trend'),
#     # bt.algos.PrintTempData(),
#     bt.algos.Rebalance()
# )

# st = bt.Strategy("LAA",
#     [
#         bt.algos.Or([once, laa])
#     ])        
START_DATE = '2002-1-2'
config = Config(
                stocks = {'kodex200': 0.12, 'us500_UH': 0.13},
                bonds={'usbond10y_UH':0.18, 'kbond10y': 0.07}, 
                gold = {'gold_UH':0.25}, 
                is_dc=True,
                safe_assets=['kodex200', 'usbond10y_UH'], 
                safe_limit=0.30
)

once = bt.AlgoStack(bt.algos.RunAfterDate(START_DATE),
                    bt.algos.RunOnce(),
                    SelectAsset(config),
                    bt.algos.PrintInfo("{now} {name} {temp}"),
                    bt.algos.Rebalance())
laa = bt.AlgoStack(
    bt.algos.RunAfterDate(START_DATE),
    bt.algos.RunMonthly(run_on_first_date=False, run_on_end_of_period=True),
    # bt.algos.PrintDate(),
    bt.algos.SelectAll(),
    WeighLAA(config),
    # bt.algos.PrintTempData(),
    bt.algos.Rebalance()
)
st = bt.Strategy('LAADCMixedUSBond10y',
    [
        bt.algos.Or([once, laa])
    ])
