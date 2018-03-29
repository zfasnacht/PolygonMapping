import argparse
from map_script import make_map
import h5py
import numpy as np
from pyhdf.HDF import *
from pyhdf.V   import *
from pyhdf.SD  import *

#Reading data if hdf4 format
def read_hdf4(he4_filename,path):
	temp = path.split('/')[1:]

	hdf = HDF(he4_filename)

	v  = hdf.vgstart()
	refnum = v.find(temp[0]) 
	print refnum
	vg = v.attach(refnum)
	members = vg.tagrefs()
	sd = SD(he4_filename)

	index = refnum
	for tag, ref in members:	
		if tag == HC.DFTAG_VG:
			vg0 = v.attach(ref)
			member_new = vg0.tagrefs()
			for tags, refs in member_new:
				print refs
				if tags == HC.DFTAG_NDG:
					sd_name, sd_ndims, sd_dims, sd_type, sd_nattrs=sd.select(index-refnum).info()
					print sd.select(index-refnum).info()
					index = index + 1
					if sd_name == temp[-1]:
						
						return sd.select(index).get()
				
#Reading data if hdf5 format
def print_attrs(name, obj):
	f = h5py.File(data_filename)
        if isinstance(f['/'+name], h5py.Dataset):
        	if fieldname in ('/'+name):
                	return name

def read_hdf5(data_filename):
	#Reading the user given datafield from data file user has chosen 
	f = h5py.File(data_filename)
	#print f['/HDFEOS/SWATHS/OMI Column Amount O3/Data Fields/Reflectivity340'][:]
	dataset = f[f.visititems(print_attrs)][:]
	
	return dataset

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
pixcor_filename = argument.pname
data_filename = argument.fname
fieldname = argument.dfield
geo_bounds = argument.geobounds
cbar_bounds = argument.cbarbounds
cbar_type = argument.cbartype
output_filename = argument.outfile

#Checking whether file is hdf4 or hdf5 
try:
	dataset = read_hdf5(data_filename)
except:
	dataset = read_hdf4(data_filename,fieldname)

#Changing Fill Values to NaN for plotting purposes 
dataset[dataset < -999] = np.nan


print cbar_bounds
#Readingin lat/lon corners for PIXCOR file that user has chosen 
data = h5py.File(pixcor_filename)

lat_corner = data['/HDFEOS/SWATHS/OMI Ground Pixel Corners UV-2/Data Fields/FoV75CornerLatitude'][:,:,:]
lon_corner = data['/HDFEOS/SWATHS/OMI Ground Pixel Corners UV-2/Data Fields/FoV75CornerLongitude'][:,:,:]

#Running the function make_map which is imported from the file map_script.py 
make_map(dataset,lat_corner,lon_corner,output_filename,geo_bounds,cbar_bounds,cbar_type,fieldname.split('/')[-1])

