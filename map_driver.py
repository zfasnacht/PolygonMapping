import argparse
from map_script import make_map
import h5py
import numpy as np

def print_attrs(name, obj):
        if isinstance(f['/'+name], h5py.Dataset):
        	if fieldname in name:
                	return name

#Reading in user given arguments to use in running function make_map
parser = argparse.ArgumentParser(description = "Description for my parser")
parser.add_argument("-fname", "--fname",  required = True)
parser.add_argument("-pname", "--pname",  required = True)
parser.add_argument("-dfield", "--dfield",  required = True)
parser.add_argument("-outfile", "--outfile",  required = True)
parser.add_argument("-geobounds", "--geobounds",  type=int,required = False, nargs='+',default = [-180,180,-90,90])
parser.add_argument("-cbarbounds", "--cbarbounds",  type=int,required = False,nargs=3)
parser.add_argument("-cbartype", "--cbartype",  required = False, default = "continuous")


argument = parser.parse_args()


#Parsing the user given arguments
pixcor_filename = argument.pixcor
data_filename = argument.filename
fieldname = argument.field
geo_bounds = argument.geo_bounds
cbar_bounds = argument.cbar_bounds
cbar_type = argument.cbar_type
output_filename = argument.out_file

#Reading the user given datafield from data file user has chosen 
f = h5py.File(data_filename)
dataset = f[f.visititems(print_attrs)][:]

#Changing Fill Values to NaN for plotting purposes 
dataset[dataset < -999] = np.nan

#Creating colorbar bounds based on 10th and 90th percentiles if user has not given colorbar bounds
if not(cbar_bounds):
	cbar_min = int(np.nanpercentile(dataset, 10))
	cbar_max = int(np.nanpercentile(dataset, 90))
	cbar_bounds = [cbar_min,cbar_max,11]


#Readingin lat/lon corners for PIXCOR file that user has chosen 
data = h5py.File(pixcor_filename)

lat_corner = data['/HDFEOS/SWATHS/OMI Ground Pixel Corners UV-2/Data Fields/FoV75CornerLatitude'][:,:,:]
lon_corner = data['/HDFEOS/SWATHS/OMI Ground Pixel Corners UV-2/Data Fields/FoV75CornerLongitude'][:,:,:]

#Running the function make_map which is imported from the file map_script.py 
make_map(dataset,lat_corner,lon_corner,output_filename,geo_bounds,cbar_bounds,cbar_type,fieldname)

