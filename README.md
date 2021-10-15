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
