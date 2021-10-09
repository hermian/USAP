#%% markdown
# https://m.blog.naver.com/jwtessa/222029243868

#%%
import pandas as pd
import numpy
#%%
def save_csv(file_name, df):
    df.to_csv(f'{file_name}.csv')#, encoding='ms949')
    print(f'{file_name}.csv 저장 완료')


def read_csv(file_name):
    read_df = pd.read_csv(f'{file_name}.csv')#, encoding='ms949')
    컬럼명_리스트 = list(read_df.columns)
    read_df = read_df.set_index(컬럼명_리스트[0])
    new_index = list(read_df.index.astype(str))
    read_df.index = new_index
    return read_df
#%%
지수모음 = read_csv('raw_utf8')
#%%
def fact_sheet(file_name, date_type):
    print('\nfact_sheet\n')
    back_test_df = read_csv(file_name)

    col_name = back_test_df.columns[0] # 불러올 칼럼값
    date_list = list(back_test_df.index) # y값이 될 날짜 데이터

    ###################  mdd 구하기  ####################
    max_point = 0 # 전고점 지수
    draw_down_list = [] # draw down이 기록될 리스트
    for date in date_list:
        val = back_test_df[col_name][date] # x값으로 칼럼명 y값으로 날짜 데이터가 들어가는 지수의 값 변수 지정
        if val > max_point: # 값이 전고점 지수 (max_point)보다 크다면
            max_point = val # 전고점 지수 현재 지수로 덮어쓰기

        draw_down = ((val / max_point) - 1) # 현재 시점의 draw down은 현재값 / 전고점값 - 1
        draw_down_list.append(draw_down) # 계산된 현재 시점의 draw down을 리스트에 어펜드
        # print(draw_down)

    ###################  연환산 변동성 구하기  ####################
    monthly_return_list = [] # 월간 수익률이 기록될 리스트
    for num in range(1,len(date_list)): # date_list가 아니라 len(날짜리스트)를 사용하며 range 1부터 시작하는 이유는 전월 값이 필요하기 때문에
        front_date = date_list[num - 1] # 전월 date_num
        rear_date = date_list[num] # 현재 반복문으로 조회중인 date_num
        f_val = back_test_df[col_name][front_date] # 전월 값
        r_val = back_test_df[col_name][rear_date] # 현재 반복문으로 조회중인 값
        monthly_return = r_val / f_val # 월간 수익률은 현재 값 / 전월 값
        monthly_return_list.append(monthly_return) # 월간 수익률을 monthly_return_list에 어펜드


    first_val = back_test_df[col_name][date_list[0]]
    last_val = back_test_df[col_name][date_list[-1]]

    cagr = (last_val / first_val) ** (1 / (len(date_list) / date_type))-1 # (마지막 지수값 / 시작 지수값) ** (1 / 년수) -1
    mdd = min(draw_down_list) # draw_down_list의 가장 작은값
    y_vol = numpy.std(monthly_return_list) * numpy.sqrt(date_type) # 모든 수익률의 표준편차 * 제곱근(연간 표본 갯수)
    sharp_ratio = (cagr - 0.03) / y_vol # (cagr - 무위혐수익률) / 연환산변동성

    print('cagr', round(cagr*100,2),'%')
    print('mdd', round(mdd*100,2),'%')
    print('연환산변동성', round(y_vol*100,2),'%')
    print('샤프비율', round(sharp_ratio,2))


    back_test_df['draw down'] = draw_down_list # back_test_df에 draw_down_list를 추가하기. (데이터프레임에 리스트를 추가할때는 길이가 같아야 한다.)
    save_csv(f'{file_name} fact sheet', back_test_df)

#%%
def get_AMS(file_name): # 365일간 매일의 절대 모멘텀 유무를 구하여 평균을 내는 평균 모멘텀스코어
    read_df = read_csv(file_name)
    AMS_dict = {}
    지수명리스트 = read_df.columns
    for 지수명 in 지수명리스트:
        값시리즈 = read_df[지수명] # 지수를 시리즈 타입으로 가져온다
        # print(칼럼)
        date_list = list(read_df.index) # 날짜를 리스트 타입으로 가져온다
        # print(날짜리스트)

        AMS_list = [] # 각각의 평균 모멘텀 스코어가 기록될 리스트

        for date in date_list[365:]: # 과거 365일 값을 조회해야 하기 때문에 365부터 시작
            현재_지수 = 값시리즈[date] # 시리즈 타입으로 만들어진 raw_index에 현재 날짜를 입력하여 현재의 지수 값을 가져온다.
            현재_번호 = date_list.index(date) # 현재 반복중인 날짜가 데이터 리스트의 몇번째 값인지 숫자로 돌려준다.

            절대모멘텀_list = [] # 각각의 절대 모멘텀 유무를 기록할 리스트
            for num in range(1, 366): # num 앞에 -를 붙여 쓰기 때문에 1부터 시작한다.
                N일전_날짜 = date_list[현재_번호 - num] # 현재 시점으로부터 num일 전
                N일전_지수 = 값시리즈[N일전_날짜] # 현재 시점으로부터 num일 전 지수값

                if 현재_지수 > N일전_지수: # 현재 지수값이 n일 전 값보다 크면
                    절대_모멘텀 = 1
                else: # 현재 지수값이 n일 전 값보다 작으면
                    절대_모멘텀 = 0
                절대모멘텀_list.append(절대_모멘텀) # 위에서 구해진 절대 모멘텀을 absolute_momentum_list에 기록한다.

            평균_모멘텀_스코어 = numpy.mean(절대모멘텀_list) # numpy.mean를 사용해 과거 365일간의 절대 모멘텀 유무의 평균을 구한다
            AMS_list.append(평균_모멘텀_스코어) # 현재 현재날짜 시점에 AMS_list에 평균 모멘텀 스코어를 등록한다.
        AMS_dict[지수명] = AMS_list

    df = pd.DataFrame(AMS_dict, index=date_list[365:]) # 데이터 프레임 변환
    print(df)
    save_csv(f"{file_name}_AMS", df) # 입력 받은 파일 이름에 AMS라는 텍스트를 추가하여 저장
#%%
get_AMS('raw_utf8')
#%%
fn인덱스 = 지수모음.iloc[:, :-3]
#%%
기타데이터 = 지수모음.iloc[:, -3:]
#%%
'''
이산성시그널_df와 일간수익률_df를 만든다.
이산성시그널_df는 월간(30일로 계산) 수익률이 > 0 면 1이고 아니면 0인 df
'''
정보이산성df = []
날짜리스트 = list(지수모음.index)
지수이름리스트 = list(지수모음.columns)
#%%
수익률딕 = {}
이산성딕 = {}
for 지수명 in 지수이름리스트:
    일간수익률리스트 = [0]
    이산성리스트 = [0]
    for i in range(1, len(날짜리스트)):
        전일날짜 = 날짜리스트[i - 1]
        현재날짜 = 날짜리스트[i]

        전일값 = 지수모음[지수명][전일날짜]
        현재값 = 지수모음[지수명][현재날짜]

        일간수익률 = 현재값 / 전일값
        일간수익률리스트.append(일간수익률)
        if i > 30:
            한달전값 = 지수모음[지수명][날짜리스트[i - 30]]
            월간수익률 = 현재값 / 한달전값

            if 월간수익률 > 1:
                이산성리스트.append(1)
            else:
                이산성리스트.append(0)
        else:
            이산성리스트.append(0)

    수익률딕[지수명] = 일간수익률리스트
    이산성딕[지수명] = 이산성리스트

일간수익률_df = pd.DataFrame(수익률딕, index=날짜리스트)
이산성시그널_df = pd.DataFrame(이산성딕, index=날짜리스트) # 월간 수익률이 양이면 1, 아니면 0이 들어간 데이터프레임

save_csv('일간수익률',일간수익률_df)
save_csv('이산성시그널', 이산성시그널_df)
#%%
수익률딕 = {}
이산성딕 = {}
평균수익률딕 = {}
코스피1년수익률딕 = []
for 지수명 in 지수이름리스트:
    IDM = []
    이산성리스트 = []
    평균수익률_리스트 = []
    코스피1년수익률리스트 = []
    for i in range(365, len(날짜리스트)):
        개월전12 = 날짜리스트[i - 365]
        개월전9 = 날짜리스트[i - 273]
        개월전6 = 날짜리스트[i - 182]
        개월전1 = 날짜리스트[i-30]
        오늘 = 날짜리스트[i]


        개월전12값 = 지수모음[지수명][개월전12]
        개월전9값 = 지수모음[지수명][개월전9]
        개월전6값 = 지수모음[지수명][개월전6]
        개월전1값 = 지수모음[지수명][개월전1]

        개월전12수익률 = 개월전1값 / 개월전12값 # 최근 1개월을 버린다.
        개월전9수익률 = 개월전1값 / 개월전9값
        개월전6수익률 = 개월전1값 / 개월전6값


        상승일비중 = numpy.mean(이산성시그널_df[지수명][개월전12:오늘]) # 1년 평균
        # print(상승일비중)
        하락일비중 = 1-상승일비중

        이산성 = (하락일비중 - 상승일비중) * -1
        이산성리스트.append(이산성)

        평균수익률 = (개월전12수익률 + 개월전9수익률 + 개월전6수익률) / 3
        IDM.append(평균수익률 * 이산성)
        평균수익률_리스트.append(평균수익률)

        # 코스피1년수익률 = 지수모음['코스피200'][오늘] / 지수모음['코스피200'][개월전12]
        # 코스피1년수익률리스트.append(코스피1년수익률)

    수익률딕[지수명] = IDM
    이산성딕[지수명] = 이산성리스트
    평균수익률딕[지수명] = 평균수익률_리스트
    # 코스피1년수익률딕['코스피1년수익률'] = 코스피1년수익률리스트
#%%
IDM_df = pd.DataFrame(수익률딕, index=날짜리스트[365:]) # 평균수익률 * 이산성
이산성_df = pd.DataFrame(이산성딕, index=날짜리스트[365:])
평균수익률_df = pd.DataFrame(평균수익률딕, index=날짜리스트[365:])
코스피_df = pd.DataFrame(코스피1년수익률딕, index=날짜리스트[365:])
#%%
# print(IDM_df)

save_csv('이산성',이산성_df)
save_csv('IDM', IDM_df)
save_csv('평균수익률', 평균수익률_df)
save_csv('코스피1년수익률', 코스피_df)
#%%
모멘텀 = read_csv('IDM')
평수 = read_csv('평균수익률')
AMS = read_csv('raw_utf8_AMS')
일간수익률 = read_csv('일간수익률')
OECD = read_csv('OECD')
외인수급_AMS = read_csv('외인코스피보유 AMS')
#%%
모멘텀_날짜리스트 = list(모멘텀.index)

인덱스포인트 = 100
인덱스포인트_리스트 = [인덱스포인트]

for num in range(1, len(모멘텀_날짜리스트)):
    날짜 = 모멘텀_날짜리스트[num - 1]
    수익률_날짜 = 모멘텀_날짜리스트[num]
    if num == 1 or 날짜[-2:] == '01': # 매월 1일 리밸런싱

        내림차순정렬 = 모멘텀.loc[날짜].sort_values(ascending=False)
        상위3종목 = list(내림차순정렬[:3].index)


        코스피AMS = AMS['코스피200'][날짜]
        외인AMS = 외인수급_AMS['외국인수급 AMS'][날짜]
        # 코스피AMS = 외인AMS
        OECD전월비 = OECD['전월비'][날짜]
        # if OECD전월비 > 1:
        #    pass
        # else:
        #     코스피AMS *= 0

        종목당_비중 = 인덱스포인트 * 코스피AMS / 3
        첫번째종목비중 = 종목당_비중
        두번째종목비중 = 종목당_비중
        세번째종목비중 = 종목당_비중

        현금비중 = 인덱스포인트 * (1-코스피AMS)

    첫번째종목수익률 = 일간수익률[상위3종목[0]][수익률_날짜]
    두번째종목수익률 = 일간수익률[상위3종목[1]][수익률_날짜]
    세번째종목수익률 = 일간수익률[상위3종목[2]][수익률_날짜]


    첫번째종목비중 *= 첫번째종목수익률
    두번째종목비중 *= 두번째종목수익률
    세번째종목비중 *= 세번째종목수익률
    현금비중 *= 1.0000548 # 이자율 2% 가정

    인덱스포인트 = 현금비중 + 첫번째종목비중 + 두번째종목비중 + 세번째종목비중
    # print(인덱스포인트)
    인덱스포인트_리스트.append(인덱스포인트)
#%%
섹터듀얼 = pd.DataFrame({'인덱스' : 인덱스포인트_리스트}, index=모멘텀_날짜리스트)

save_csv('섹터듀얼', 섹터듀얼)
fact_sheet('섹터듀얼',365)
#%%
'''
로직
6, 9, 12 개윌 -1개월 모멘텀에 월간 이산성 평균을 곱한다
평균수익률이 0 이하인건 현금보유
'''
fact_sheet('3개 전략 통합',365)
#%%
get_AMS('달러자산utf8')
#%%
달러자산 = read_csv('달러자산utf8')
#%%
달러자산AMS = read_csv('달러자산utf8_AMS')
#%%
달러자산일간수익률 = read_csv('달러자산 일간수익률')

#%%
인덱스포인트 = 100
인덱스포인트_리스트 = [인덱스포인트]
for num in range(1, len(모멘텀_날짜리스트)):
    날짜 = 모멘텀_날짜리스트[num - 1]
    수익률_날짜 = 모멘텀_날짜리스트[num]

    if num == 1 or 날짜[-2:] == '01': # 매월 1일 리밸런싱

        나스닥AMS = 달러자산AMS['나스닥100'][날짜]
        다우AMS = 달러자산AMS['다우'][날짜]

        종목당_비중 = 인덱스포인트 / 3
        첫번째종목비중 = 종목당_비중 * 나스닥AMS
        두번째종목비중 = 종목당_비중 * 다우AMS


        현금비중 = 인덱스포인트 -첫번째종목비중 -두번째종목비중

    첫번째종목수익률 = (((달러자산일간수익률['나스닥100'][수익률_날짜]-1)*3)+1) * 달러자산일간수익률['달러'][수익률_날짜]
    두번째종목수익률 = (((달러자산일간수익률['다우'][수익률_날짜]-1)*3)+1) * 달러자산일간수익률['달러'][수익률_날짜]


    첫번째종목비중 *= 첫번째종목수익률
    두번째종목비중 *= 두번째종목수익률

    현금비중 *=달러자산일간수익률['달러'][수익률_날짜]
    인덱스포인트 = 첫번째종목비중 + 두번째종목비중 + 현금비중
    # print(인덱스포인트)
    인덱스포인트_리스트.append(인덱스포인트)
#%%
나스닥다우월간 = pd.DataFrame({'인덱스' : 인덱스포인트_리스트}, index=모멘텀_날짜리스트)
save_csv('나스닥다우월간', 나스닥다우월간)
fact_sheet('나스닥다우월간',365)
fact_sheet('미국한국2',365)
# %%
