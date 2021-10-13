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
c='코스피200'
target_weight = pd.DataFrame()
target_weight['base3'] = prices[c].rolling(365).apply(AMS)
# %%
target_weight['현금'] = 1.0 - target_weight
target_weight.columns = ['base3', '현금']
target_weight['base3'].plot(figsize=(16,6), title='코스피200 AMS 절대모멘텀 비중', legend=True);
