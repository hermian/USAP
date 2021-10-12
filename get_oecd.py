import requests

print('Beginning file download with requests')

url = "https://stats.oecd.org/sdmx-json/data/DP_LIVE/KOR.CLI.AMPLITUD.LTRENDIDX.M/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod=2005-01"
r = requests.get(url)

with open('OECD_KOR.csv', 'wb') as f:
    f.write(r.content)

# Retrieve HTTP meta-data
print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)