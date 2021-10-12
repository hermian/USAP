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
