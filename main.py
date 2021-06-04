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



