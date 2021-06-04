import pandas as pd

# Google Sheet URL
DATA_URL = "https://docs.google.com/spreadsheets/d/{}/export?gid={}&format=csv"

columns = ['日期', '檢驗人數', '確診人數', '居檢送驗', '居檢送驗累計', 
		'武肺通報', '武肺通報累計', '擴大監測', '擴大監測累計']

tests = (
	pd.read_csv(DATA_URL.format(
		"1Kp5IC5IEI2ffaOSZY1daYoi2u50bjUHJW-IgfHoEq8o", # Sheet ID
		1173642744 # Test Pop Table GID
	))
	.loc[:, columns] # Formatting
)

# Fill in NULL values
tests.fillna(value={col: 0 for col in tests.columns[1:]}, inplace=True)

for col in tests.columns[1:]:
	try:
		tests[col] = tests[col].astype(int)
	except:
		print(col)


# Display Recent Data
tests.tail()

import pendulum

# Include Date
na = (tests['日期'].isna())
prev = tests.loc[~na].tail(1)['日期'].iloc[0]
prev_dt = pendulum.date(2020, *[int(s) for s in prev.split("/")])
latest_dt = prev_dt.add(days=1)
tests.loc[na, ['日期']] = f"{latest_dt.month}/{latest_dt.day}"

# Formatting Date
tests['日期'] = tests['日期'].str.split('/')\
    .apply(lambda x: pendulum.date(2020, int(x[0]), int(x[1])).format("YYYY-MM-DD"))

(tests.tail(5)
    .style
    .applymap(lambda x: 'background-color: rgb(153, 255, 51)', 
              subset=['日期']))

pd.DataFrame({
    '送驗': [tests['檢驗人數'].sum()],
    '確診': [tests['確診人數'].sum()],    
})

yesterday_dt = pendulum.yesterday(tz="Asia/Taipei").format("YYYY-MM-DD")
tests[tests['日期'] == yesterday_dt].loc[:, ['日期', '檢驗人數', '確診人數']]\
    .rename({'檢驗人數': "送驗", '確診人數': '確診'}, axis=1)


data = (
    tests
    .rename({  # 用跟疾管署一致的 naming convention
        '擴大監測': '擴大監測送驗',
        '居檢送驗': '居家檢驗送驗',
        '武肺通報': '法定傳染病通報',
    }, axis=1)  # 這邊的關鍵是使用 `melt` 來建立 `通報來源` 變數
    .melt('日期', ['擴大監測送驗', '居家檢驗送驗', '法定傳染病通報'], 
        var_name='通報來源', value_name="通報數")
    .fillna(0)
)
data.tail()

import altair as alt  # 使用 altair 的標準起手式
_ = alt.renderers.set_embed_options(actions=False)  # 隱藏下載圖片的按鈕以節省空間

alt.Chart(data).mark_bar(  # 繪製柱狀圖
# 將數據變數編碼（encode）到視覺變數上
).encode(  
    x="日期:T",  # 將日期對應到 x 軸上
    y="通報數:Q",  # 將通報數對應到 y 軸上
    color="通報來源:N"  # 將通報來源對應到顏色
# 設置整個圖的屬性
).properties(  
    width=700  # 圖表寬度
)

# 去除註解的最簡 Altair 繪圖呼叫方式
alt.Chart(data).mark_bar().encode(
    x="日期:T",
    y="通報數:Q",
    color="通報來源:N"
)

chart_title = "COVID-19（武漢肺炎）監測趨勢圖 - 依通報來源"
alt.Chart(data, title=chart_title).mark_bar()\
.encode(
    x=alt.X('日期:T', title="通報日", axis=alt.Axis(
        grid=False,  # 去除縱軸的格線
        format="%m/%d",  # 自定義日期格式
    )),
    y="通報數:Q",
    color='通報來源:O',  # 將通報來源視為有序類別
    tooltip=['日期:T', '通報來源', '通報數']  # 加上提示框
).properties(
    width=700
)

cases = (
    pd.read_csv(DATA_URL.format(
        "1Kp5IC5IEI2ffaOSZY1daYoi2u50bjUHJW-IgfHoEq8o",
        0  # `臺灣武漢肺炎病例` 工作表的 gid
    ))
    .loc[:, ['出現症狀日期', '案例', '來源', '性別', '年齡']]
)

# 這邊忽略沒有記載出現症狀日期的案例
cases = cases.loc[~cases['出現症狀日期'].isna()]
cases = cases.loc[cases['出現症狀日期'].apply(lambda x: not 'x' in x)]

# 處理時間欄位的字串讓 Altair 等等可以正確解析日期
cases['出現症狀日期'] = cases['出現症狀日期']\
    .apply(lambda x: '-'.join(['2020', *x.split("/")]))

cases.tail()

data = (
    cases
    .groupby(['出現症狀日期', '來源'])['案例']
    .count()
    .reset_index()
)
data.tail()

title = "嚴重特殊性傳染性肺炎確診個案趨勢圖 - 依發病日"
alt.Chart(data, title=title).mark_bar()\
.encode(
    x=alt.X('出現症狀日期:T', title="發病日", axis=alt.Axis(
        grid=False,
        format="%m/%d")),
    y='案例:Q',
    color='來源:N',
    tooltip=['出現症狀日期:T', '來源', '案例']
).properties(
    width=700
)
