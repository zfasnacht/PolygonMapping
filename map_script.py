import numpy as np
import matplotlib
import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import NaturalEarthFeature
from matplotlib.patches import Polygon
from pylab import *

#Function for creating blank map with cartopy
def create_map(projection=ccrs.PlateCarree()):
	fig, ax = plt.subplots(1,figsize=(10,17),
		           subplot_kw=dict(projection=projection))

	gl = ax.gridlines(draw_labels=True)
	gl.ylabels_right = False
	gl.xlabels_top = False
	gl.xformatter = LONGITUDE_FORMATTER
	gl.yformatter = LATITUDE_FORMATTER
	
	return fig, ax

#Function for making colormap used for plotting polygons. Colorbar type (continuous vs discrete) is user input. 
def make_colormap(lower,upper,step,types):

	#If continuous colorbar is chosen a simple jet colorbar is used	
	if (types == 'continuous') |(types == 'Continuous'):
		cmap = plt.cm.jet
	#If discrete colorbar is chosen a colorbar that ranges from darkblue to cyan is created 
	elif (types == 'discrete') | (types == 'Discrete'):
		cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["darkblue","blue","cyan"])
	#If user inputs custom list of colors a custom colorbar is created, if none of the above arguments was given 
	#by user or a list of colors was not inputted, the code returns error message to user 
	else:
		try:
			cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", types)		
		except:
			print "ERROR with colormap type"
			STOP
	cmaplist = [cmap(i) for i in range(cmap.N)]
	cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)
	if (np.abs(lower) < 5.) & (np.abs(upper) < 5.):
		bounds = np.linspace(np.round(lower,2),np.round(upper,2),step)
	else:
		bounds = np.linspace(lower,upper,step)

	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	return norm, cmap,bounds

#For polygons that overlap, determining whether polygon is closest to 180E or 0E for longitude or -90S or Equator for latitude, used 
#for splitting up polygons that stretch across the globe 
def closest(lon_min,val):
	if np.abs(0-lon_min) < np.abs(val-lon_min):
		return 0
	else:
		return val

#Plotting individual polygon on map for given color based on colormap created 
def plot_poly(lon_corner,lat_corner,data,axes,cmap,norm):
	
	x1,y1 = (lon_corner[0],lat_corner[0])
	x2,y2 = (lon_corner[1],lat_corner[1])
	x3,y3 = (lon_corner[2],lat_corner[2])
	x4,y4 = (lon_corner[3],lat_corner[3])

	
	if (~np.isnan(data)):
		p = Polygon(np.vstack((lon_corner,lat_corner)).T,facecolor=cmap(norm(data)),linewidth=0,edgecolor="black") 
		axes.add_patch(p)
				
#Main function for creating polygons on map
def make_map(data,lat_corner,lon_corner,fig_name,geo_bounds=[-180,180,-90,90],cbar_bounds=[],cbar_type='continuous',cbar_label=''):
	
	#Checking if colorbar bounds exist and creating colorbar bounds if they are no given as input. Default color bar used the 
	#10th percentile of data for the cbar min, 90th percentile for cbar max, and assumes 10 incremental steps in the colorbar.
	#If only one data point was given as input a colorbar is made with a range +/- 10% of that data point (planning to change to solid color). 
	if (not cbar_bounds) & (isinstance(data,(list, np.ndarray))):
		cbar_min = (np.nanpercentile(data, 10))
		cbar_max = (np.nanpercentile(data, 90))
		cbar_bounds = [cbar_min,cbar_max,11]
	elif (not colorbar_bounds) & (~isinstance(data,(list, np.ndarray))):
		cbar_min = data - (data * 0.1)
		cbar_max = data + (data * 0.1)
		cbar_bounds = [cbar_min,cbar_max,11]
	print np.shape(data)
	#If a single scalar data point is given for plotted it is converted into a list since code loops through polygons 
	if not isinstance(data,(list, np.ndarray)):
		data = np.array([data])
	print np.shape(data)
	#If a single vector of one polygon is given the corners are converted to 2d arrays (corners,1) so that code can 
	#loop through polygons 
	if len(np.shape(lat_corner)) ==1:
		lat_corner = np.array(lat_corner).reshape(len(lat_corner),1)
		lon_corner = np.array(lon_corner).reshape(len(lon_corner),1)


	#If orbital data that is 2 dimensional is provided it is flattened to 1-d so that code can plot both 1-d and 2-d data given
	#as input by user 
	if len(np.shape(data)) == 2:
		data_len = len(data[:,0])*len(data[0,:])
		data = np.array(data).flatten()
		lat_corner = np.array(lat_corner).reshape(len(lat_corner[:,0,0]),data_len)
		lon_corner = np.array(lon_corner).reshape(len(lon_corner[:,0,0]),data_len)
	print np.shape(data)
	#Creating a blank map for mapping polygons
	fig, axes = create_map()
	
	#Setting the bounds of the map
	axes.set_extent(geo_bounds)

	#Setting the bounds of the colorbar
	print cbar_bounds[0],cbar_bounds[1],cbar_bounds[2]+1
	norm, cmap,bounds = make_colormap(cbar_bounds[0],cbar_bounds[1],cbar_bounds[2]+1,cbar_type)

	#Looping through polygons and plotting them on map
	print np.shape(data)
	for i in range(len(data[:])):
	
		#As we loop through the polygons the code checks to make sure the polygons do not stretch across the globe (ie polygon stretches 
		#across the dateline) as python will not stretch them over the map but instead strectch across the map (so polygon across dateline 
		#would typically in python be plotted as stretching across the globe over the prime meridian). This piece of code looks for these 
		#polygons and breaks them into smaller polygons that do not stretch across the globe in order to properly plot these polygons and 
		#then is maps the polygons on the plot...plan to try to simplify this code snippet eventually 
		if ((np.nanmin(lon_corner[:,i]) * np.nanmax(lon_corner[:,i])) < 0) & ((np.nanmin(lat_corner[:,i]) * np.nanmax(lat_corner[:,i])) < 0):
			
			lon_cross = closest(np.nanmin(lon_corner[:,i]),-180)
			lat_cross = closest(np.nanmin(lat_corner[:,i]),-90)

			temp_lat = np.array(lat_corner)
			temp_lat[temp_lat > 0] =lat_cross
			temp_lon = np.array(lon_corner)
			temp_lon[temp_lon > 0] = lon_cross
			plot_poly(temp_lon[:,i],temp_lat[:,i],data[i],axes,cmap,norm)

			temp_lat = np.array(lat_corner)
			temp_lat[temp_lat < 0] = np.abs(lat_cross)
			temp_lon = np.array(lon_corner)
			temp_lon[temp_lon < 0] = np.abs(lon_cross)
			plot_poly(temp_lon[:,i],temp_lat[:,i],data[i],axes,cmap,norm)

			temp_lat = np.array(lat_corner)
			temp_lat[temp_lat > 0] = lat_cross
			temp_lon = np.array(lon_corner)
			temp_lon[temp_lon < 0] = np.abs(lon_cross)
			plot_poly(temp_lon[:,i],temp_lat[:,i],data[i],axes,cmap,norm)

			temp_lat = np.array(lat_corner)
			temp_lat[temp_lat < 0] = np.abs(lat_cross)
			temp_lon = np.array(lon_corner)
			temp_lon[temp_lon > 0] = lon_cross
			plot_poly(temp_lon[:,i],temp_lat[:,i],data[i],axes,cmap,norm)

		elif (np.nanmin(lon_corner[:,i]) * np.nanmax(lon_corner[:,i])) < 0:
			
			lon_cross = closest(np.nanmin(lon_corner[:,i]),-180)

			temp_lon = np.array(lon_corner)
			temp_lon[temp_lon < 0] = np.abs(lon_cross)
			plot_poly(temp_lon[:,i],lat_corner[:,i],data[i],axes,cmap,norm)

			temp_lon = np.array(lon_corner)
			temp_lon[temp_lon > 0] = lon_cross
			plot_poly(temp_lon[:,i],lat_corner[:,i],data[i],axes,cmap,norm)
			
		elif (np.nanmin(lat_corner[:,i]) * np.nanmax(lat_corner[:,i])) < 0:
			lat_cross = closest(np.nanmin(lat_corner[:,i]),-90)

			temp_lat = np.array(lat_corner)
			temp_lat[temp_lat < 0] = np.abs(lat_cross)
			plot_poly(lon_corner[:,i],temp_lat[:,i],data[i],axes,cmap,norm)

			temp_lat = np.array(lat_corner)
			temp_lat[temp_lat > 0] = lat_cross
			plot_poly(lon_corner[:,i],temp_lat[:,i],data[i],axes,cmap,norm)
		else:			
			plot_poly(lon_corner[:,i],lat_corner[:,i],data[i],axes,cmap,norm)

	#Making fake scatterplot and using it to display colorbar on map because pythons polygon function only displays one colorbar 
	#and therefore cannot be used for making a colorbar
	grid_lat = np.arange(-90,90,1)
	grid_lon = np.arange(-180,180,1)
	grid_data = np.zeros((180,360),dtype=np.float)
	grid_lon, grid_lat = np.meshgrid(np.array(grid_lon), np.array(grid_lat))
	im = axes.scatter(grid_lon,grid_lat,c=grid_data,s=0,cmap=cmap,norm=norm)
	cb=fig.colorbar(im,ax=axes,boundaries=bounds,fraction=0.03,orientation='vertical')
	cb.ax.tick_params(labelsize=20)
	cb.set_label(cbar_label,fontsize=25)
	coast = NaturalEarthFeature(category='physical', scale='10m',
			            facecolor='none', name='coastline')	
	feature = axes.add_feature(coast, edgecolor='black')	


	#Saving the colorbar with the user given filename 
	plt.savefig(fig_name,bbox_inches='tight')



