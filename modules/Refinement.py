'''
    Description:
        This module encapsulates classes used for refinement of the Corine Land Cover map.
    Classes:
        - Shapefile
        - VectorContainer
'''
import os, ogr, osr, gdal, gdalconst

class File():
    '''
        Description:
            An instance of this class is a representation of a file in the file system.
    '''
    def __init__(self, path):
        # Input variables: path - absolute path to the file
        self.path = path

    # Input variables: None
    # Output: Absolute path of this file
    def get_path(self):
        return self.path

class Shapefile(File):
    '''
        Description:
            An instance of this class is a representation of a shape file in the file system.
    '''
    def __init__(self, path):
        self.path = path
        assert path[-3:] == 'shp'

class Rasterfile(File):
    '''
        Description:
            An instance of this class is a representation of a raster file in the file system.
    '''
    def __init__(self, path):
        self.path = path
        assert path[-3:] == 'tif'

class VectorContainer():
    '''
        Description:
            An instance of this class is a container for Shapefiles.
    '''

    def __init__(self, shapefiles, field_name):
        # Input variables: shapefiles - list of Shapefile
        #                  field_name - name of the attribute that stores the class code
        self.shapefiles = shapefiles
        self.field_name = field_name

    # Input variables: None
    # After: Contents of this container have been merged into a single Shapefile
    # and saved as a new file, merged.shp in the scripts directory.
    def merge(self):
        outputMergefn = 'merge.shp'
        driverName = 'ESRI Shapefile'
        geometryType = ogr.wkbPolygon

        out_driver = ogr.GetDriverByName(driverName)
        if os.path.exists(outputMergefn):
            out_driver.DeleteDataSource(outputMergefn)
        out_ds = out_driver.CreateDataSource(outputMergefn)
        out_layer = out_ds.CreateLayer(outputMergefn, geom_type=geometryType)
        out_layer.CreateField(ogr.FieldDefn('code', ogr.OFTInteger))

        for i in range(len(self.shapefiles)):
            file = self.shapefiles[i]
            print('File: '+str(i)+' of '+str(len(self.shapefiles)))
            print('Current file: '+file.get_path())
            ds = ogr.Open(file.get_path())
            lyr = ds.GetLayer()
            for feat in lyr:
                out_feat = ogr.Feature(out_layer.GetLayerDefn())
                out_feat.SetField('code', feat.GetFieldAsInteger(self.field_name))
                out_feat.SetGeometry(feat.GetGeometryRef().Clone())
                out_layer.CreateFeature(out_feat)
                out_feat = None
                out_layer.SyncToDisk()

    # Input variables: resolution - integer resolution in meters
    # After: The file 'merged.shp' has been rasterized to a tif format with the specified resolution.
    def rasterize(self, resolution):
        assert os.path.exists('merge.shp'), "You need to merge the container first."
        pixel_size = resolution
        NoData_value = 0
        raster_fn = 'merge.tif'
        source_ds = ogr.Open('merge.shp')
        source_layer = source_ds.GetLayer()
        x_min, x_max, y_min, y_max = source_layer.GetExtent()
        x_res = int((x_max - x_min) / pixel_size)
        y_res = int((y_max - y_min) / pixel_size)
        target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32)
        target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
        band = target_ds.GetRasterBand(1)
        band.SetNoDataValue(NoData_value)
        gdal.RasterizeLayer(target_ds, [1], source_layer, options=["ATTRIBUTE=code"])
        target_dsSRS = osr.SpatialReference()
        target_dsSRS.ImportFromEPSG(3035)
        target_ds.SetProjection(target_dsSRS.ExportToWkt())
        target_ds = None

class RasterContainer():
    '''
        Description:
            An instance of this class is a container for raster files.
            This class requires gdal_merge.py installed on the system.
    '''
    def __init__(self, rasterfiles):
        # Input variables: rasterfiles - list of rasters
        self.rasterfiles = rasterfiles

    # Input variables: None
    # After: Files in this container have been merged into one raster file.
    def merge(self):
        os.system('gdal_merge.py -n 0 -o out.tif '+' '.join(self.rasterfiles))
