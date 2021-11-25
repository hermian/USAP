import numpy as np
import pandas as pd
import bt
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings(action='ignore')

def plot_correlations(df, figsize=(11,9)):
    corr = df.to_returns().dropna().corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr, mask=mask, annot=True, fmt='.1g', vmin=-1, vmax=1, center=0, cmap='coolwarm')

def plot_df(df, figsize=(12,9), title="", legend_loc="best", legend_ordered=True, logy=True):
    columns = df.iloc[-1].sort_values(ascending=False).index #마지막값 높은 순서로
    # print(columns)
    df = df[columns] # 데이터프레임 열 순서를 변경
    ax = df.plot(figsize=(12,8), title=title, logy=logy)
    leg = ax.legend(loc=legend_loc)
    if legend_ordered:
        for line, text in zip(leg.get_lines(), leg.get_texts()):
            text.set_color(line.get_color()) # 범례의 글씨 색깔을 범례와 동일하게

def 투자시점별CAGRMDD(backtest):
    """

    Args:
        end : 백테스트기간 종료보다 1년전 날짜 설정, cagr이 연률화이기 때문에 1년 미만은 과대한 수치를 보여준다.
    """
    r = bt.run(backtest)
    cagrs = {}
    mdds = {}
    #for m in pd.date_range(start_date, '2021-10', freq='M'):
    # 전수를 하려면 아래, 월별로 하려면 위의 루프를 실행한다.
    for m in r.prices.index:
        # print(m)
        try:
            cagrs[m] = r.prices[m:].calc_cagr().values[0]
            mdds[m] = r.prices[m:].calc_max_drawdown().values[0]
        except:
            print(m)

    cagr_df = pd.DataFrame([cagrs]).T*100
    mdd_df = pd.DataFrame([mdds]).T*100

    tdf = bt.merge(cagr_df, mdd_df)
    tdf.columns = ['cagr', 'mdd']

    end = r.prices.index[-1] - pd.DateOffset(years=1)

    ####### plot
    # tdf[:end].plot(figsize=(12,6)) # area의 경우 cagr negative문제 있음
    df = tdf[:end]
    fig, ax = plt.subplots(figsize=(12,6))
    # split dataframe df into negative only and positive only values
    df_neg, df_pos = df.clip(upper=0), df.clip(lower=0)
    # stacked area plot of positive values
    df_pos.plot.area(ax=ax, stacked=True, linewidth=0.)
    # reset the color cycle
    ax.set_prop_cycle(None)
    # stacked area plot of negative values, prepend column names with '_' such that they don't appear in the legend
    df_neg.rename(columns=lambda x: '_' + x).plot.area(ax=ax, stacked=True, linewidth=0.)
    # rescale the y axis
    ax.set_ylim([df_neg.sum(axis=1).min(), df_pos.sum(axis=1).max()])