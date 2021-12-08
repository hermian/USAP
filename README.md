# USAP(Upers Sector Alpha Plus)
어퍼스 섹터 알파 플러스

- https://m.blog.naver.com/jwtessa/222029243868

## 참고

- https://m.blog.naver.com/htk1019/221588145775
- https://alphaarchitect.com/2019/07/11/momentum-quality-and-r-code/
- https://docs.google.com/spreadsheets/d/e/2PACX-1vROcemqqycHHpasQLwkYwJClLlvyMFP--2RTFE239pXHnXnNuJA-ey_rUYdEaniMeWPY1HdHiwDvfSG/pubhtml?gid=289693522&single=true
- https://cafe.naver.com/spoonchanger

```python
dollar_assets_weights = r1.get_security_weights()*0.5
kbase123_weights = r2.get_security_weights()*0.5
security_weights = bt.merge(kbase123_weights, dollar_assets_weights)
security_weights = security_weights['2002-02-01':]
security_weights.plot.area(stacked=True, alpha=0.7, legend=False, cmap='jet', figsize=(16,6));
```

## ChangeLog

### 2021/12/8

- 대통합_LAA_Without_IEF.ipynb (https://github.com/hermian/USAP/issues/2) 추가
- 대통합_LAA.ipynb 갱신 (gold_H 를 새로 만들어서 재 테스트 기존 보다 약간 안좋은 듯?)

### 2021/12/5

- 대통합_LAA.ipynb (https://github.com/hermian/USAP/issues/1) 추가

### 2021/11/25

- 미국달러자산_현금추가.ipynb <- 기존대비 더 좋지 않다. MDD(Avg Drawdown) 나 CAGR이나

### 202111-21

- 미국달러레버리지자산.ipynb, 대통합달러레버.ipynb 추가
- 미국달러자산SPY.ipynb, 대통합SPY.ipynb 추가
- ID2 외국인 수급 데이터 오류 정정
  - ID2_외국인수급_데이터수정.ipynb
  - index.go.kr데이터는 외국인 보유 주식수에 현재 주가데이터를 반영한 것이라 백테스트에 맞지 않음
  - 대신증권 HTS에서 투자자별매매동향(거래대금, 순매수) 데이터를 다운로드 후 cumsum한 것으로 테스트 변경
- ID2 외국인수급+개인수급역추종 비중
  - ID2_외국인개인수급.ipynb
  - 대통합외국인개인수급.ipynb

- 대통합외국인수급수정.ipynb !!!
