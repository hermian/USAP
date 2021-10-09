# %% [markdown]
# # Momentum, Quality, and R Code
# https://alphaarchitect.com/2019/07/11/momentum-quality-and-r-code/

# %%
import bt
import FinanceDataReader as fdr
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import quantstats as qs
import seaborn as sns

# pd.options.display.float_format = '{:.4f}'.format
plt.style.use('default') #ggplot
plt.rcParams['font.family'] = 'nanummyeongjo'
plt.rcParams['figure.figsize'] = [12,8]
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['axes.grid'] = True

plt.rcParams['axes.formatter.useoffset'] = False
# plt.rcParmas['axes.formatter.limits'] = -1000, 1000

plt.rcParams['axes.unicode_minus'] = False
# %matplotlib inline
from IPython.display import display, HTML
"%config InlineBackend.figure_format = 'retina'"
# %%
tickers = ["SPY", "XLF", "XLE"]
start_date = "2000-01-03"
end_date = "2018-12-31"
# %%
spy = yf.download('SPY', start=start_date, end=end_date)
# %%
spy = spy.resample("M").last()
# %%
spy["mom_return"] = spy['Adj Close'] / spy['Adj Close'].shift(1) - 1
# %%
spy["skip_mon_return"] = spy["mom_return"].shift(1) #왜 할까?
# %%
# spy["twelve_mon_return"] = spy['Adj Close'].shift(1) / spy['Adj Close'].shift(13) - 1
spy["twelve_mon_return"] = spy['Adj Close'].pct_change(12).shift(1)
# %%
spy["pos_months"] = np.where(spy["skip_mon_return"] > 0, 1, 0)
# %%
spy["neg_months"] = np.where(spy["skip_mon_return"] < 0, 1, 0)
# %%
spy["pos_percent"] = spy["pos_months"].rolling(12).mean()
# %%
spy["neg_percent"] = spy["neg_months"].rolling(12).mean()
# %%
spy["perc_diff"] = spy["neg_percent"] - spy["pos_percent"]
# %%
spy["pret"] = np.sign(spy["twelve_mon_return"])
# %%
spy["inf_discr"] = spy["pret"] * spy["perc_diff"]
# %%
spy["inf_discr"].mean()
# %%
spy["id_label"] = np.where(spy["inf_discr"] < 0, "continuous", "discrete")

# %%
