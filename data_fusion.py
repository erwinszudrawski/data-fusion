from modules import Refinement
from modules import Utils

# ------------------ DATA FUSION STEPS ------------------

urban_atlas_dir = 'data/urban_atlas/poland'
#Utils.unzip(urban_atlas_dir)

ua_files = []
for path in Utils.get_ua_paths(urban_atlas_dir):
    ua_files.append(Refinement.Shapefile(path))

ua = Refinement.VectorContainer(ua_files, 'CODE2012')
ua.merge()
ua.rasterize(30)
merge = Refinement.RasterContainer(['merge.tif'])
# Remove classes from urban atlas that are not used in the refinement process

merge.convert_to_nodata([31000, 12300, 12400, 13400, 14100, 14200, 32000, 33000, 21000, 22000, 23000, 24000, 25000])

raster_files = ['data/clc_30m.tif', 'merge.tif']
rc = Refinement.RasterContainer(raster_files)
rc.merge()
