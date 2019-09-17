from modules import Refinement
from modules import Utils

urban_atlas_dir = 'data/urban_atlas/poland'
#Utils.unzip(urban_atlas_dir)

ua_files = []
for path in Utils.get_ua_paths(urban_atlas_dir):
    ua_files.append(Refinement.Shapefile(path))

ua = Refinement.VectorContainer(ua_files, 'CODE2012')
#ua.merge()
#ua.rasterize(30)

# raster_files = ['data/clc_30m.tif', 'merge.tif']
# rc = Refinement.RasterContainer(raster_files)
# rc.merge()
