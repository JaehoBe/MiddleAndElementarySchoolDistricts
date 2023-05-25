# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

##################################################
# import modules

import os
import pandas as pd
import requests
# from tqdm import tqdm
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from pyproj import CRS
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.lines as mlines
import matplotlib.ticker as ticker
import seaborn as sns
from collections import Counter
import re

from matplotlib import font_manager, rc
plt.rc('font', family='NanumGothic')
print(plt.rcParams['font.family'])

# Set the max_columns option to None
pd.set_option('display.max_columns', None)

import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'


##################################################
# set working directory

cwd = os.getcwd()
# print(cwd)

base_path = "/Users/USER/PycharmProjects/genderSortingAcrossElementarySchoolInKorea"
path_engineered_data = os.path.join(base_path, r'engineered_data')

if not os.path.exists(path_engineered_data):
   os.makedirs(path_engineered_data)


##################################################
# MiddleSchool: open files

file_name = "data/middleSchool/2022MiddleSchool.csv"
file_path = os.path.join(base_path, file_name)
MiddleSchoolStudentInfo2022 = pd.read_csv(file_path, encoding='utf-8')
for col in MiddleSchoolStudentInfo2022 .columns:
    print(col)
# print(ElementarySchoolStudentInfo2022['시도교육청'].unique())
MiddleSchoolStudentInfo2022_subset = MiddleSchoolStudentInfo2022[MiddleSchoolStudentInfo2022['시도교육청'].str.contains('서울특별시교육청')]

file_name = "data/middleSchool/2022년도_학교기본정보(중등).csv"
file_path = os.path.join(base_path, file_name)
MiddleSchoolInfo2022 = pd.read_csv(file_path, encoding='utf-8')
MiddleSchoolInfo2022_subset = MiddleSchoolInfo2022[MiddleSchoolInfo2022['시도교육청'].str.contains('서울특별시교육청')]

##################################################
# merge two data sets

merged_df = pd.merge(MiddleSchoolStudentInfo2022_subset, MiddleSchoolInfo2022_subset, on='정보공시 학교코드', how='inner', indicator=True, suffixes=('', '_new'))
merged_df = merged_df[merged_df.columns.drop(list(merged_df.filter(regex='_new')))]

merged_df.loc[merged_df['학교명'] == '동덕여자중학교', '위도'] = '37.4762931'
merged_df.loc[merged_df['학교명'] == '동덕여자중학교', '경도'] = '126.9926473'
merged_df.loc[merged_df['학교명'] == '원촌중학교', '위도'] = '37.5059213'
merged_df.loc[merged_df['학교명'] == '원촌중학교', '경도'] = '127.0141459'
merged_df.loc[merged_df['학교명'] == '솔샘중학교', '위도'] = '37.6236568'
merged_df.loc[merged_df['학교명'] == '솔샘중학교', '경도'] = '127.0122142'
merged_df.loc[merged_df['학교명'] == '동성중학교', '위도'] = '37.5852449'
merged_df.loc[merged_df['학교명'] == '동성중학교', '경도'] = '127.0024442'
merged_df.loc[merged_df['학교명'] == '동성중학교', '위도'] = '37.49124'
merged_df.loc[merged_df['학교명'] == '개원중학교', '경도'] = '127.071435'


file_path = os.path.join(base_path + '/engineered_data', 'merged_df_with_coordinates(MiddleSchool).csv')
merged_df.to_csv(file_path, index=False, encoding='utf-8')
# merged_df.to_csv('merged_df_with_coordinates.csv', index=False, encoding='cp949')

# read middle school district shp file and check distribution
file_name = "data/middleSchoolDistrict/중학교학교군.shp"
file_path = os.path.join(base_path, file_name)
shapefileMiddle = gpd.read_file(file_path)
# print(shapefileMiddle.columns)

columns_to_drop = ['CRE_DT', 'UPD_DT', 'BASE_DT']
shapefileMiddle_subset = shapefileMiddle.drop(columns_to_drop, axis=1)
# print(shapefileMiddle_subset.columns)
subsetMiddle = shapefileMiddle_subset[shapefileMiddle_subset['EDU_UP_NM'] == "서울특별시교육청"]
# print(subsetMiddle.shape)
# print(len(subsetMiddle['HAKGUDO_NM']))


# convert merged_df_with_coordinates to a GeoDataFrame
points = gpd.GeoDataFrame(merged_df,
                          geometry=gpd.points_from_xy(merged_df['경도'],
                                                      merged_df['위도']))

# infer CRS from latitude and longitude columns using pyproj
points.crs = CRS.from_user_input('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs').to_wkt()

# convert subset to a GeoDataFrame
polygons = gpd.GeoDataFrame(subsetMiddle)

# reproject points to match the CRS of polygons
points = points.to_crs(polygons.crs)

# perform spatial join
joined = gpd.sjoin(points, polygons, op='within')

# count the number of points for each polygon
counts = joined.groupby('index_right').size()

# print the number of points in each polygon
for index, count in counts.items():
    polygon_name = subsetMiddle.loc[index, 'HAKGUDO_NM']
    print(f"Polygon '{polygon_name}' has {count} points.")


# ##################################################
# # plot points and polygon (simple overlay)
#
# fig, ax = plt.subplots(figsize=(10,10))
#
# polygons.plot(ax=ax, alpha=0.5, edgecolor='black')
# joined.plot(ax=ax, color='red', markersize=5)
#
# plt.show()
#
#
# # count the number of points for each polygon
# counts = joined.index.value_counts()
#
# # select polygons with more than one point
# multi_point_polygons = counts[counts > 1].index.tolist()
#
# # print the list of polygons with more than one point
# print(multi_point_polygons)


'''
##################################################
# ElementarySchool: open files
file_name = "engineered_data/merged_df_with_coordinates.csv"
file_path = os.path.join(base_path, file_name)
merged_df = pd.read_csv(file_path, encoding='utf-8')
for col in merged_df .columns:
    print(col)


# elementary school
# read school district shp file

file_name = "data/elementarySchooldistrict/초등학교통학구역.shp"
file_path = os.path.join(base_path, file_name)
shapefile = gpd.read_file(file_path)
# print(shapefile.columns)

columns_to_drop = ['CRE_DT', 'UPD_DT', 'BASE_DT']
shapefile_subset = shapefile.drop(columns_to_drop, axis=1)
print(shapefile_subset.columns)
subset = shapefile_subset[shapefile_subset['EDU_UP_NM'] == "서울특별시교육청"]


# convert merged_df_with_coordinates to a GeoDataFrame
points = gpd.GeoDataFrame(merged_df,
                          geometry=gpd.points_from_xy(merged_df['longitude'],
                                                      merged_df['latitude']))

# infer CRS from latitude and longitude columns using pyproj
points.crs = CRS.from_user_input('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs').to_wkt()

# convert subset to a GeoDataFrame
polygons = gpd.GeoDataFrame(subsetMiddle)

# reproject points to match the CRS of polygons
points = points.to_crs(polygons.crs)

# perform spatial join
joined = gpd.sjoin(points, polygons, op='within')

# count the number of points for each polygon
counts = joined.groupby('index_right').size()

# print the number of points(elementary school) in each polygon
for index, count in counts.items():
    polygon_name = subsetMiddle.loc[index, 'HAKGUDO_NM']
    print(f"Polygon '{polygon_name}' has {count} points.")


# Create a new plot
fig, ax = plt.subplots(figsize=(10, 10))
'''


'''
# Plot shapefile A
subsetMiddle.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2, label='Middle School Districts')

# Plot shapefile B
subset.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1, linestyle='dotted', label='Elementary School Districts')
'''
'''
# 지도: 중학교 학교군 + 초등학교 학교군
# Plot shapefile A
subsetMiddle.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2, label='중학교 학군')
line_A = mlines.Line2D([], [], color='black', linewidth=2, label='Shapefile A (Bold Line)')

# Plot shapefile B
subset.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1, linestyle='dotted', label='초등학교 학군')
line_B = mlines.Line2D([], [], color='black', linewidth=1, linestyle='dotted', label='Shapefile B (Dotted Line)')

# Set the aspect ratio to 'equal' for a proper spatial representation
ax.set_aspect('equal')

# Format tick labels
ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))

# Remove tick labels
ax.set_xticklabels([])
ax.set_yticklabels([])

# Create custom legend handles
handles = [line_A, line_B]
labels = ['중학교 학군', '초등학교 학군']

# Set labels for custom legend handles
for handle, label in zip(handles, labels):
    handle.set_label(label)

# Add legend
plt.legend(handles=handles)

# Add any additional customization as needed (title, legend, etc.)
ax.set_title('Middle and Elementary School Districts of Seoul')

# Specify the file path for saving the figure
file_path = os.path.join(base_path, 'schoolDistricts(MiddleElementarySchool.png')

# Save the figure
plt.savefig(file_path)

# Display the plot
plt.show()
'''


# read high school district shp file and check distribution
file_name = "data/highSchoolDistrict/고등학교학교군.shp"
file_path = os.path.join(base_path, file_name)
shapefileHigh = gpd.read_file(file_path)
# print(shapefileMiddle.columns)

columns_to_drop = ['CRE_DT', 'UPD_DT', 'BASE_DT']
shapefileHigh_subset = shapefileHigh.drop(columns_to_drop, axis=1)
# print(shapefileHigh_subset.columns)
subsetHigh = shapefileHigh_subset[shapefileHigh_subset['EDU_UP_NM'] == "서울특별시교육청"]
# print(subsetHigh.shape)
# print(len(subsetHigh['HAKGUDO_NM']))



# 지도: 고등학교 학교군 + 초등학교 학교군
# Plot shapefile A
subsetHigh.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2, label='고등학교 학군')
line_A = mlines.Line2D([], [], color='black', linewidth=2, label='Shapefile A (Bold Line)')

# Plot shapefile B
subset.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1, linestyle='dotted', label='초등학교 학군')
line_B = mlines.Line2D([], [], color='black', linewidth=1, linestyle='dotted', label='Shapefile B (Dotted Line)')

# Set the aspect ratio to 'equal' for a proper spatial representation
ax.set_aspect('equal')

# Format tick labels
ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))

# Remove tick labels
ax.set_xticklabels([])
ax.set_yticklabels([])

# Create custom legend handles
handles = [line_A, line_B]
labels = ['고등학교 학군', '초등학교 학군']

# Set labels for custom legend handles
for handle, label in zip(handles, labels):
    handle.set_label(label)

# Add legend
plt.legend(handles=handles)

# Add any additional customization as needed (title, legend, etc.)
ax.set_title('High and Elementary School Districts of Seoul')

# Specify the file path for saving the figure
file_path = os.path.join(base_path, 'schoolDistricts(HighElementarySchool.png')

# Save the figure
plt.savefig(file_path)

# Display the plot
plt.show()


# convert subset to a GeoDataFrame
polygons = gpd.GeoDataFrame(subsetHigh)

# reproject points to match the CRS of polygons
points = points.to_crs(polygons.crs)

# perform spatial join
joined = gpd.sjoin(points, polygons, op='within')

# count the number of points for each polygon
counts = joined.groupby('index_right').size()

# print the number of points(elementary school) in each polygon
for index, count in counts.items():
    polygon_name = subsetHigh.loc[index, 'HAKGUDO_NM']
    print(f"Polygon '{polygon_name}' has {count} points.")



# 지도: 고등학교 학교군 + 중학교 학교군
# Plot shapefile A
subsetHigh.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2, label='고등학교 학군')
line_A = mlines.Line2D([], [], color='black', linewidth=2, label='Shapefile A (Bold Line)')

# Plot shapefile B
subsetMiddle.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1, linestyle='dotted', label='중학교 학군')
line_B = mlines.Line2D([], [], color='black', linewidth=1, linestyle='dotted', label='Shapefile B (Dotted Line)')

# Set the aspect ratio to 'equal' for a proper spatial representation
ax.set_aspect('equal')

# Format tick labels
ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))

# Remove tick labels
ax.set_xticklabels([])
ax.set_yticklabels([])

# Create custom legend handles
handles = [line_A, line_B]
labels = ['고등학교 학군', '중학교 학군']

# Set labels for custom legend handles
for handle, label in zip(handles, labels):
    handle.set_label(label)

# Add legend
plt.legend(handles=handles)

# Add any additional customization as needed (title, legend, etc.)
ax.set_title('High and Middle School Districts of Seoul')

# Specify the file path for saving the figure
file_path = os.path.join(base_path, 'schoolDistricts(HighMiddleSchool.png')

# Save the figure
plt.savefig(file_path)

# Display the plot
plt.show()


# convert subset to a GeoDataFrame
polygons = gpd.GeoDataFrame(subsetHigh)

# reproject points to match the CRS of polygons
points = points.to_crs(polygons.crs)

# perform spatial join
joined = gpd.sjoin(points, polygons, op='within')

# count the number of points for each polygon
counts = joined.groupby('index_right').size()

# print the number of points(elementary school) in each polygon
for index, count in counts.items():
    polygon_name = subsetHigh.loc[index, 'HAKGUDO_NM']
    print(f"Polygon '{polygon_name}' has {count} points.")



# middle school
# MiddleSchool: open files(합치기 필요)
file_name = "engineered_data/merged_df_with_coordinates(MiddleSchool).csv"
file_path = os.path.join(base_path, file_name)
middleSchool = pd.read_csv(file_path, encoding='utf-8')
# for col in middleSchool .columns:
#     print(col)

middleSchoolSubset = middleSchool[middleSchool['설립구분'] == '공립']
print(middleSchoolSubset['남녀공학 구분'].unique())
middleSchoolSubset = middleSchoolSubset[middleSchoolSubset['남녀공학 구분'] == '남녀공학']

# convert merged_df_with_coordinates to a GeoDataFrame
points = gpd.GeoDataFrame(middleSchoolSubset,
                          geometry=gpd.points_from_xy(middleSchoolSubset['경도'],
                                                      middleSchoolSubset['위도']))

# infer CRS from latitude and longitude columns using pyproj
points.crs = CRS.from_user_input('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs').to_wkt()

# convert subset to a GeoDataFrame
polygons = gpd.GeoDataFrame(subsetHigh)

# reproject points to match the CRS of polygons
points = points.to_crs(polygons.crs)

# perform spatial join
joined = gpd.sjoin(points, polygons, op='within')

# count the number of points for each polygon
counts = joined.groupby('index_right').size()

# print the number of points(elementary school) in each polygon
for index, count in counts.items():
    polygon_name = subsetHigh.loc[index, 'HAKGUDO_NM']
    print(f"Polygon '{polygon_name}' has {count} points.")
