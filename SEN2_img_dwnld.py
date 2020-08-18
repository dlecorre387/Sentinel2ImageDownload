import os

# connect to API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

# please input your SciHub username and password
api = SentinelAPI('username', 'password', 'https://scihub.copernicus.eu/apihub')

# state image ID(s) if a specific image is required
ID_list = None
#['ProductID']

# or copy and paste the file path to your chosen area of interest (in .geojson format)
geojson_files_path = None
#['C:/Users/User/Documents/AreaOfInterest.geojson']

# in either case, make sure the other variable is equal to None

# define your prefered downolad output directory
output_dir = "C:/Users/User/Documents/DowloadedImages"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# if downloading images of an AOI, specify the dates you would like to search between
dates = None
        #{
        #'year': ['2019','2019'],
        #'month': ['01','12'],
        #'day': ['01','31']
        #}

# or you can download four seasonal images for a specific year
seasons = None
        #{
        #'spring': [0301,0531],
        #'summer': [0601,0831],
        #'autumn': [0901,1130],
        #'winter': [1201,0228]
        #}

# delete the None and uncomment the dictionary as needed
# but again, in either case make sure that the other variable between dates/seasons is set to None

# input your chosen year as an integer
year = 2019

# and your desired cloud cover tolerance
cloud_cover_percentage = 10

# detect chosen download method
if ID_list is None and geojson_files_path is not None:
    
    # iterate through file paths
    for i, path in enumerate(geojson_files_path):
        
        # loop through features within the same file
        for j, geometry in enumerate(read_geojson(path)["features"]):
            
            # converts to well-kown text
            footprint = geojson_to_wkt(geometry)
            
            # determine if searching by dates or by seasons
            if dates is not None and seasons is None:
                
                # find products within dates and suitable cloud cover
                products = api.query(footprint,
                                     date=('{}{}{}'.format(dates['year'][0], dates['month'][0], dates['day'][0]),
                                           '{}{}{}'.format(dates['year'][1], dates['month'][1], dates['day'][1])),
                                     platformname='Sentinel-2',
                                     processinglevel='Level-2A',
                                     cloudcoverpercentage=(0, cloud_cover_percentage))
                
                # print error message if there are no images which fit the requirements
                if len(list(products)) == 0:
                    print("There are no Sentinel-2 images for this AOI taken within the specified dates")
                    break
                
                # convert from dictionary to Pandas dataframe
                products_df = api.to_dataframe(products)
                
                # sort products by their cloud cover percentages
                products_df_sorted = products_df.sort_values(['cloudcoverpercentage'], ascending=[True])
                
                # keep only the three with the lowest cloud cover %s
                products_df_sorted = products_df_sorted.head(3)
                
                # loop through the products to find the images with best cloud covers
                for productkey in list(products.keys()):
                    
                    # find products that are not those three
                    if productkey == any(products_df_sorted.index) is False:
                        
                        # delete those products
                        del products[productkey]
                
                # print downloading message
                print("Downloading the three least cloudy images covering AOI {} taken between {}/{}/{} and {}/{}/{}".format(j+1,dates['day'][0],dates['month'][0],dates['year'][0],dates['day'][1],dates['month'][1],dates['year'][1]))
                
                # start product download to output directory
                api.download_all(products,output_dir)
                
            elif dates is None and seasons is not None:
                        
                    # loop through seasons in dictionary
                    for season in list(seasons.keys()):
                            
                        # skip downloading images taken during unwanted season(s)
                        if seasons[season] is None:
                            continue
                            
                        # search by AOI, season, and SciHub query keywords
                        products = api.query(footprint,
                                             date=('{}{}'.format(year,seasons[season][0]),'{}{}'.format(year,seasons[season][1])),
                                             platformname='Sentinel-2',
                                             processinglevel='Level-2A',
                                             cloudcoverpercentage=(0, cloud_cover_percentage))
                        
                        # 'if' statement to avoid download error due to zero porducts
                        if len(list(products)) == 0:
                            print("There are no Sentinel-2 images taken of this AOI during the {} of {} within the specified cloud cover tolerance".format(season,year))
                            continue       
                        
                        # convert from dictionary to Pandas dataframe
                        products_df = api.to_dataframe(products)
                        
                        # sort by cloud cover %s in ascending order
                        products_df_sorted = products_df.sort_values(['cloudcoverpercentage'], ascending=[True])
                        
                        # pick the image with the best cloud cover
                        products_df_sorted = products_df_sorted.head(1)
                        
                        # loop through products to find the image
                        for productkey in list(products.keys()):
                            
                            # find all other products with worse cloud covers
                            if productkey != products_df_sorted.index:
                                
                                # delete all other products
                                del products[productkey]
                        
                        # download image with least cloud cover
                        api.download_all(products,output_dir)
                        
                        # print download message for each product
                        print("Downloading the image with the least cloud cover taken of AOI {} taken during the {} of {}".format(j+1,season,year))
                            
                        # download the image with the best cloud cover for that season
                        api.download_all(products,output_dir)
            else:
                        
                    # print error message if too many or too few inputs are given
                    print("Sensing interval dates not specified, or inputs have been given for both 'seasons' and 'dates' (please make one None)")

# determine if ID(s) have been give instead
elif ID_list is not None and geojson_files_path is None:
    
    # loop through elements in ID list
    for i, ID in enumerate(ID_list):

        try:
            
            # find product using known ID
            products = api.query(identifier=ID)
            
            # print download message for each product
            print("Downloading image ID: {} ({} of {})".format(ID, i+1, len(ID_list)))
            
            # download single image by known product ID
            api.download(products,output_dir)

        except:

            # print error message if download fails
            print("Could not download Sentinel-2 image with ID {}.".format(ID))
            
else:
    # print error message if none or both of ID_list and geojson_files_path have been set to equal None
    print("Product ID(s) and file path(s) have been provided. Please make either 'ID_list' or 'geojson_files_path' equal to None.")