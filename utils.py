import numpy as np
import pandas as pd
import bt
import seaborn as sns
import matplotlib.pyplot as plt


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