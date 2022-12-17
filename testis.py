import re
import pandas as pd
import folium

datasource_df = pd.read_csv("GasStationData.csv")

lat_long_regex = re.compile(r'[-]?[\d]+[.][\d]*')
lat_long_list = []
for link in datasource_df["Navigation links"]:
    lat_and_long = lat_long_regex.findall(link)
    lat_long_list.append(lat_and_long)
print(lat_long_list)

