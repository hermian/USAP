# %% [markdown]
# pip install -r pykrx
# %%
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import yfinance as yf
import numpy as np
import pandas as pd
from pykrx import stock
import time
# from tqdm import tqdm

# pd.options.display.float_format = '{:.4f}'.format
plt.style.use('ggplot') #ggplot
plt.rcParams['font.family'] = 'nanummyeongjo'
plt.rcParams['figure.figsize'] = (12,8)
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['axes.grid'] = True

plt.rcParams['axes.formatter.useoffset'] = False
# plt.rcParmas['axes.formatter.limits'] = -1000, 1000

plt.rcParams['axes.unicode_minus'] = False
# %matplotlib inline
from IPython.display import display, HTML
"%config InlineBackend.figure_format = 'retina'"

#하나의 cell에서 multiple output을 출력을 가능하게 하는 코드
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
# Pandas Dataframe의 사이즈가 큰 경우, 어떻게 화면에 출력을 할지를 세팅하는 코드
pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('max_columns', None)
# %%
from strategy import*
from utils import *

# %%
def 장중이냐(now):
    return (9 <= now.hour <= 14) or (now.hour == 15 and (now.minute <= 30))

# %%
def AMS(x):
    ''' x : Series (DataFrame의 컬럼)
        x[-1] : 기준일. x의 현재값
        (오늘날짜/과거날짜 - 1) > 0 보다 크면 1, 아니면 0
        => 오늘날짜/과거날짜 > 1 => 오늘날짜 > 과거날짜  => x[-1] > x
    '''
    # print(f"{list(np.where(x[-1]>x, 1, 0)[:-1])}, {len(np.where(x[-1]>x, 1, 0)[:-1])}")
    return np.mean(np.where(x[-1]>x, 1, 0)[:-1]) # 당일 날짜 비교는 제외해준다 [:-1]

# %%
# get_data
# code_list is tickers['code']
# start : before_13months
# end : baseday

def get_data(code_list, start, end):
    df = pd.DataFrame()
    tot = len(code_list)
    count = 0
    for code in code_list: # tqdm(code_list)
        count += 1
        print(f"{count}/{tot} : {code}")
        t = fdr.DataReader(code, start, end)['Close'].rename(code)
        # t = stock.get_market_ohlcv_by_date(start, end, code)['종가'].rename(code)
        df = bt.merge(df, t)
        time.sleep(0.75)

    # 맨마지막 값이 NaN인 컬럼을 삭제한다.
    for c in df.columns:
        if pd.isna(df.iloc[-1][c]):
            print(c)
            df.drop(c, axis=1, inplace=True) 

    return df

# %%
def 종목명(code, df=tickers):
    """ 사용예) 종목명('A153130') or 종목명('153130')
    """
    if code.startswith('A'):
        return df[df['종목코드'] == code]['종목명'].values[0]
    else:
        return df[df['code'] == code]['종목명'].values[0]
def 종목코드(name, df=tickers):
    """ A를 제외한 종목코드를 반환한다. FinanceDataReader에서 사용
    """
    _df = df.copy()
    _df['종목명'] = _df['종목명'].str.replace(' ', '')
    return _df[_df['종목명'] == name.replace(' ', '')]['code'].values[0]        

# %%
def pickup(df, 제외직전개월수=1):
    """df에서 모멘텀이 가장 좋은 3종목을 선택한다.   

    Args :
        - df : 가격 데이터프레임
        - 제외직전개월수 : df에서 제외할 데이터 개월 수
        - now : 가격 데이터프레임의 가장 아래 시간 
    """
    t0 = df.index[-1]
    제외 = t0 - pd.DateOffset(months=제외직전개월수)
    m6 = t0 - pd.DateOffset(months=6)
    m9 = t0 - pd.DateOffset(months=9)
    m12 = t0 - pd.DateOffset(months=12)
    m13 = t0 - pd.DateOffset(months=13)

    m6_returns = (df.loc[m6:제외,:].calc_total_return()+1) # 1달제외 6개월 수익률 (현재 prices가 공휴일포함 데이터임)
    m9_returns = (df.loc[m9:제외,:].calc_total_return()+1) # 1달제외 9개월 수익률
    m12_returns = (df.loc[m12:제외,:].calc_total_return()+1)  # 1달제외 12개월 수익률
    average_returns = (m6_returns+m9_returns+m12_returns)/3

    # ID 계산 최근 30일 제외
    # dropna에 주의 해야 한다. 조선이 0이 있어 문제가 되므로 모든 column이 nan일 때만 drop한다.
    len_m1= round(len(df.loc[m12:,:])/12) # 한달 일수
    # print(f"{t0}, {m1}, {m6}, {m9}, {m12}, {m13}, {len_m1}")
    pos_percent = np.where(df.loc[m13:,:].pct_change(len_m1).dropna(how='all') > 0.0, 1, 0).mean(axis=0)
    neg_percent = 1 - pos_percent
    ID = (neg_percent - pos_percent)

    momentum = average_returns * ID * -1
    
    print(momentum.nlargest(3))

    return list(momentum.nlargest(3).index)

# 예제
# pickup(price_df, 0)


# %%
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def calcOECD시그널비중():
    try:
        df = pd.read_csv("https://stats.oecd.org/sdmx-json/data/DP_LIVE/KOR.CLI.AMPLITUD.LTRENDIDX.M/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod=2021-01")
        oecd = df[['TIME', 'Value']]
        oecd.set_index('TIME', inplace=True)
        oecd.index = pd.to_datetime(oecd.index)
        oecd['전월비'] = oecd.pct_change()+1
        oecd.drop('Value', axis=1, inplace=True)
        target_weight = 1 if oecd.iloc[-1][0] > 1 else 0
        # target_weights['cash'] = 1 - target_weights
        # target_weights.columns = ['base1', cash]
    except:
        raise Exception('OECD 데이터를 못 받아왔습니다.')

    return target_weight

# 예제
# OECD시그널비중()    
# %% [markdown]
# 저녁에 돌리면 다음날 리밸런싱할것이고
# 9시전에 돌리면 오늘 리밸런싱할 비중(어제종가 기준)을 구할려고 하고
# 장중에 돌리면 오늘 리밸런싱할 비중(어제종가 기준)을 구할려고 한다.
# %%
# 외국인 수급 읽어 와야 
# 개인 수급도 읽어 와야 
def calc외국인수급비중(df):
    baseday = df.index[-1]
    before_one_year = baseday - pd.DateOffset(years=1)

    tdf = stock.get_market_trading_value_by_date(before_one_year, baseday, "KOSPI")
    tdf.index.name = 'Date'
    tdf_cumsum = tdf.cumsum()
    외국인수급 = tdf_cumsum[['외국인합계']]

    외국인수급1m = 외국인수급[baseday-pd.DateOffset(months=1):baseday]
    외국인수급2m = 외국인수급[baseday-pd.DateOffset(months=2):baseday-pd.DateOffset(months=1)]
    외국인수급3m = 외국인수급[baseday-pd.DateOffset(months=3):baseday-pd.DateOffset(months=2)]
    
    외국인수급1m증가 = 외국인수급1m.iloc[-1] > 외국인수급1m.iloc[0]
    외국인수급2m증가 = 외국인수급2m.iloc[-1] > 외국인수급2m.iloc[0]
    외국인수급3m증가 = 외국인수급3m.iloc[-1] > 외국인수급3m.iloc[0]
    
    print("외국인수급: ", 외국인수급1m증가, 외국인수급2m증가, 외국인수급3m증가)
    연속3개월 = ((외국인수급3m증가) & (외국인수급2m증가) & (외국인수급1m증가))
    연속2개월 = ((외국인수급2m증가) & (외국인수급1m증가))
    연속1개월 = (외국인수급1m증가)
    print(f"외국인수급 연속증가: 연속1개월({연속1개월.values[0]}), 연속2개월({연속2개월.values[0]}), 연속3개월({연속3개월.values[0]})")
    target_weights2 = pd.DataFrame(np.where(연속3개월, 1.0,
                                            np.where(연속2개월, 0.66,
                                                    np.where(연속1개월, 0.33, 0))),
                                index=[외국인수급.index[-1]], columns=['base2'])
    print(f"target_weights2 :\n{target_weights2}")
    return target_weights2['base2'].values[0]

# %%
def calc수급스코어비중(df):
    baseday = df.index[-1]
    before_one_year = baseday - pd.DateOffset(years=1)

    tdf = stock.get_market_trading_value_by_date(before_one_year, baseday, "KOSPI")
    tdf.index.name = 'Date'
    tdf_cumsum = tdf.cumsum()

    외인추종스코어 = np.where(tdf_cumsum['외국인합계'][-1] > tdf_cumsum['외국인합계'], 1, 0).mean()
    개인역추종스코어 = np.where(tdf_cumsum['개인'][-1] < tdf_cumsum['개인'], 1, 0).mean()

    평균수급스코어 = (외인추종스코어 + 개인역추종스코어) / 2
    return 평균수급스코어

# %%
def calc코스피모멘텀스코어비중(df):
    baseday = df.index[-1]
    before_one_year = baseday - pd.DateOffset(years=1)

    kospi = fdr.DataReader('KS11', before_one_year, baseday)[['Close']]
    momentumscore = kospi['Close'].rolling(len(kospi)).apply(AMS).iloc[-1]

    return momentumscore
#%%
if __name__ == '__main__':
    #######################################
    tickers = pd.read_csv('매매종목.csv')
    tickers['code'] = tickers['종목코드'].str.replace('A', '')
    cash = '153130'# ['KODEX단기채권']
    dollar = '261250' #,KODEX 미국달러선물레버리지
    #######################################

    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d')

    # baseday, baseday_str
    # kospi = fdr.DataReader('005930', now-pd.DateOffset(days=5), now)
    samsung = stock.get_market_ohlcv_by_date(now-pd.DateOffset(days=5), now, "005930")
    if 장중이냐(now): # 09-15:30사이
        baseday = samsung.index[-2]
    elif 16 <= now.hour <= 23:
        baseday = samsung.index[-1] # 장마감으로 종가가 취득됨. 오늘자 기준
    else:
        baseday = samsung.index[-2]
    baseday_str = baseday.strftime('%Y-%m-%d')
    #최근 30일 제외를 한다.
    before_13months = baseday.replace(year=now.year - 1) - timedelta(days=50) # 1년전에 10일치를 더 읽어 온다

    # 데이터를 읽어온다.
    # price_df = pd.read_csv('sectors.csv', index_col=0, parse_dates=True)
    price_df = get_data(tickers['code'], before_13months, baseday)

    OECD시그널비중 = calcOECD시그널비중()
    수급스코어비중 = calc수급스코어비중(price_df)
    코스피모멘텀스코어비중 = calc코스피모멘텀스코어비중(price_df)
    탑픽종목코드 = pickup(price_df, 제외직전개월수=1)

    국내비중 = 0.5
    OECD매매총비중 = 국내비중 * 0.33
    OECD섹터비중 = OECD매매총비중 * OECD시그널비중
    OECD채권비중 = OECD매매총비중 * (1 - OECD시그널비중)

    수급매매총비중 = 국내비중 * 0.33
    수급섹터비중 = 수급매매총비중 * 수급스코어비중
    수급채권비중 = 수급매매총비중 * (1-수급스코어비중)

    모멘텀스코어매매총비중 = 국내비중 * 0.34
    모멘텀섹터비중 = 모멘텀스코어매매총비중 * 코스피모멘텀스코어비중
    모멘텀채권비중 = 모멘텀스코어매매총비중 * (1-코스피모멘텀스코어비중)

    섹터비중 = {}
    섹터비중[탑픽종목코드[0]] = OECD섹터비중 + 수급섹터비중/2 + 모멘텀섹터비중/3
    섹터비중[탑픽종목코드[1]] = 수급섹터비중/2 + 모멘텀섹터비중/3
    섹터비중[탑픽종목코드[2]] = 모멘텀섹터비중/3

    채권비중 = OECD채권비중+수급채권비중+모멘텀채권비중

    ############ 나스닥, 다우
    before_one_year = baseday - pd.DateOffset(years=1)
    나스닥 = yf.download("^IXIC", before_one_year, baseday)[['Adj Close']]
    다우 = yf.download("^DJI", before_one_year, baseday)[['Adj Close']]
    나스닥모멘텀스코어비중 = 나스닥['Adj Close'].rolling(len(나스닥)).apply(AMS).iloc[-1]
    다우모멘텀스코어비중 = 다우['Adj Close'].rolling(len(다우)).apply(AMS).iloc[-1]

    해외비중 = 0.5
    나스닥매매총비중 = 해외비중 * 0.5 
    나스닥비중 = 나스닥매매총비중 * 나스닥모멘텀스코어비중
    나스닥해외채권비중 = 나스닥매매총비중 * (1-나스닥모멘텀스코어비중)

    다우매매총비중 = 해외비중 * 0.5 
    다우비중 = 다우매매총비중 * 다우모멘텀스코어비중
    다우해외채권비중 = 다우매매총비중 * (1-다우모멘텀스코어비중)
    
    해외채권비중 = 나스닥해외채권비중 + 다우해외채권비중

    ############ 비중 출력
    print("="*80)
    print(f"비중 계산 기준 일자 : {baseday_str}")
    print(f"섹터 비중: {섹터비중}")
    print(f"채권비중({cash}):{채권비중}")
    print(f"나스닥비중(133690): {나스닥비중}") # A133690,TIGER 미국나스닥100
    print(f"다우비중(245340): {다우비중}") #A245340,TIGER 미국다우존스30
    print(f"해외채권비중({dollar}): {해외채권비중}")
