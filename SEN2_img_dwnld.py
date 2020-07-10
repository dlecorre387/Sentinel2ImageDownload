import os

# improt datetime to convert between date and string format
import datetime as dt
from datetime import timedelta

# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

# specify image ID(s) if certain image (or images) is required, otherwise make equal to None
ID_list = ['Product ID']

# specify GeoJSon file path if looking for images which contain desired polygons, otherwise equal to None
geojson_files_path = ['C:/Users/User/Documents/PolygonFolder/Polygons.geojson']

# make corresponding dictionary values None for unwanted seasons,
# or, if no seasonal images are required, make seasons variable equal to None
seasons = {
            'summer': [20190601,20190831],
            'autumn': [20190901,20191130],
            'winter': [20191201,20200228],
            'spring': [20200301,20200531],
            }

# specify a specific interval or date (make list elements equal in this case)
# or make dates variable equal to None if search for seasons instead
dates = {
        'year': ['2020','2020'],
        'month': ['01','05'],
        'day': ['01','01']
        }

# give your preferred date(s)
optdates = [dt.date(2020,3,31),dt.date(2019,7,31)]


# state the maximum cloud cover percentage you would like images to have
cloud_cover_percentage = 10

# define output directory
output_dir = "C:/Users/User/Documents/DownloadedImagesFolder"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# input SciHub username and password
api = SentinelAPI('username', 'password', 'https://scihub.copernicus.eu/apihub')

# if looking for images containing the given polygons
if geojson_files_path is not None and ID_list is None:
    
    for i, path in enumerate(geojson_files_path):
        
        # search by polygon, time, and SciHub query keywords
        for j, geometry in enumerate(read_geojson(path)["features"]):
            
            # convert to well-known-text
            footprint = geojson_to_wkt(geometry)
                
            # determine if dates or seasonal images are required
            if dates is not None and seasons is None:
                    
                # search by polygon, timeframe, and SciHub query keywords
                products = api.query(footprint,
                                     date=('{}{}{}'.format(dates['year'][0], dates['month'][0], dates['day'][0]),
                                           '{}{}{}'.format(dates['year'][1], dates['month'][1], dates['day'][1])),
                                     platformname='Sentinel-2',
                                     processinglevel='Level-2A',
                                     cloudcoverpercentage=(0, cloud_cover_percentage))
                    
                # form list of image IDs
                product_ids = list(products)
                
                # if statement to avoid downloading error if no products can be found
                if len(product_ids) == 0:
                    print("No images for this polygon could be found for these dates")
                    break
                
                # open empty list to store product sensing dates
                sensingdates = []
                
                # collect sensing dates
                for productkey in list(products.keys()):
                    sensingdates.append(products[productkey]["ingestiondate"].date())
                
                # open empty list for storing sensing dates of products wanted for downloading
                datestodwnld = []
                
                # loop through each inputted optimum date
                for optimumdate in optdates:
                    
                    # find how far each date is from the optimum dates
                    daysaway = [sensingdate - optimumdate for sensingdate in sensingdates]
                    
                    # convert from timedelta to absolute float value
                    daysawayfloat = [abs(dayaway.total_seconds()) for dayaway in daysaway]
                    
                    # find the index of these dates of the best images
                    ind = daysawayfloat.index(min(daysawayfloat))
                    
                    # store list of dates of images to download
                    datestodwnld.append(sensingdates[ind])
                
                # loop through each product
                for productkey in list(products.keys()):
                        
                        # find dates which are not wanted for downloading
                        if products[productkey]["ingestiondate"].date() != datestodwnld[0] and products[productkey]["ingestiondate"].date() != datestodwnld[1]:
                                
                            # remove products that are too far from the optimum dates
                            del products[productkey]
                    
                        else:
                            continue
                
                # print all image IDs which satify conditions
                print(list(products))
                
                # print download message for each product
                print("Downloading images containing polygon #{} of {} found in path #{}: {}".format(j+1, len(read_geojson(path)), i+1, path))
        
                # download single scene by known product ID
                product_info = api.download_all(products, output_dir)
                    
            elif seasons is not None and dates is None:
                    
                # find season given in dictionary
                for season in list(seasons.keys()):
                        
                    # skip downloading images taken during unwanted season(s)
                    if seasons[season] is None:
                        continue
                        
                    # search by polygon, season, and SciHub query keywords
                    products = api.query(footprint,
                                         date=('{}'.format(seasons[season][0]),'{}'.format(seasons[season][1])),
                                         platformname='Sentinel-2',
                                         processinglevel='Level-2A',
                                         cloudcoverpercentage=(0, cloud_cover_percentage))
                            
                    # form list of image IDs
                    product_ids = list(products)
                        
                    # 'if' statement to avoid download error due to zero porducts
                    if len(product_ids) == 0:
                        continue       
                        
                    # open an empty list to store cloud coverage percentages
                    ccp = []
                        
                    # form list of cloud coverages            
                    for productkey in list(products.keys()):
                        ccp.append(products[productkey]["cloudcoverpercentage"])
                        
                    # find the image with the lowest cloud coverage
                    min_ccp = min(ccp)
                            
                    # remove the remaining cloudier images
                    for productkey in list(products.keys()):
                            
                        if products[productkey]["cloudcoverpercentage"] != min_ccp:
                                
                            # remove products that are too cloudy
                            del products[productkey]
                            
                        else:
                            continue
                        
                    # print all image IDs which satify conditions
                    print(list(products))
                        
                    # print download message for each product
                    print("Downloading image containing polygon #{} of {} found in path #{}: {}".format(j+1, len(read_geojson(path)), i+1, path))
                        
                    # download single scene by known product id
                    product_info = api.download_all(products, output_dir)
        
            else:
                    
                # print error message if too many or too few inputs are given
                print("Sensing interval dates not specified, or inputs have been given for both 'seasons' and 'dates' (please make one None)")

#if a specific ID is given rather than a GeoJSon file path
elif ID_list is not None and geojson_files_path is None:
    
    for i, ID in enumerate(ID_list):

        try:
            
            # find product using known ID
            products = api.query(identifier=ID)
            
            # form list with only one element
            product_id = list(products)[0]
            
            # print download message for each product
            print("Downloading image ID: {} ({} of {})".format(ID, i+1, len(ID_list)))
            
            # download single scene by known product id
            product_info = api.download(product_id, output_dir)

        except:

            print("Could not download data for this ID.")
            
else:
    print("Product ID(s) as well as polygons have been provided. Please make one of either 'ID_list' or 'geojson_files_path' equal to None")