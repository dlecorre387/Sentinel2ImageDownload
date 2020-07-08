# How to Use Sentinel 2 Satellite Image Download Script:

The above python script allows you to find Sentinel 2 images in two different ways:
- You can either download a specific image (or images) by using its Copernicus Open Access Hub product ID code
- Or you can search for images taken of a certain area within a given timeframe, by inputting a directory for a polygon shapefile (must be a .geojson file)

## Downloading Images Using Product ID(s):

- If you know the product ID(s) of the image(s) you want to download, then copy and paste these IDs into a python list next to 'ID_list' (e.g. ID_list = [ID1, ID2, ID3]). In this instance, you must also make sure that the 'geojson_files_path' input is equal to 'None'.
- Next, you will need to specify the directory of the folder you would like the download to output to. This can be done by copying and pasting the directory within the quotation marks next to 'outputdir'.
- Lastly, in order to connect to the Copernicus Open Access Hub, you will need to input your SciHub username and password into the 'SentinelAPI' function (e.g. SentinelAPI('username','password','https://scihub.copernicus.eu/apihub')).

Assuming these steps have been followed, running the script will start the image download, with the progress being displayed in the console window.

## Downloading Images Taken Within Certain Seasons or Specific Dates:

- The first step here is to ensure that the 'ID_list' variable is equal to 'None'. You can either delete the example list next to it or simply comment it out.
- Once that is done, next to 'geojson_files_path' you will need to give the file location of the polygon shapefile of the area you want to search for images within. If you wish to search for multiple areas, you can either list the directories (e.g. geojson_files_path = ['C:/directory1', 'C:/directory2']) or you can give a .geojson file which has multiple polygons in it (as the script will loop through each polygon).
- Next, you must decide whether to search for images which were taken either within certain seasons, or within a specific set of dates. If you wish to look for seasonal images, then make sure that the 'dates' variable is 'None' and do the same for the keys of the seasons dictionary that you do not want images for (e.g. 'summer': None, 'autumn': [20190901, 20191130], etc).
- As with the product ID method, you will need to state an output directory and give your username and password (details for this step are given in the previous section).

Running this script will download four images containing your each of your polygons (one for each season), with each image having the lowest cloud cover percentage available on those dates.

- If you would rather specify the dates yourself, then simply make 'seasons' equal to 'None' and give your start and end dates. The first element of each of the dictionary values correspond to the start year, month and day - and the second element is for the end year, month and day. If you want to look on an exact date, then make these two elements equal.
- As usual, an output directory, username and password are also required.

Running the script now should download all images taken within your dates which contain your chosen polygons.

### Note

This script was written and tested using python version 3.7 and sentinelsat version 0.14
