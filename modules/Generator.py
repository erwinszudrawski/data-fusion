"""
    Description:
        This module encapsulates classes that are used for generating the data in the form
        suited for training the neural network.
"""

import numpy as np
from osgeo import gdal
from osgeo import gdalconst
import os
import tifffile as tf
from modules import Utils


class Tile:
    """
        Description:
            An instance of this class is a representation of a Sentinel-2 tile, which is stored in the file system.
    """

    # Input variables: path String - relative path to the Sentinel-2 tile.
    #                  bands - list of the band names for this tile
    #                  resolution - resolution of the bands, e.g. R10m, R20m, R60m
    def __init__(self, path, bands, resolution):
        self.path = path
        self.bands = bands
        self.resolution = resolution

    # Input variables: bands - A list of bands to convert
    # Output: Numpy array that contains band values in each feature vectors
    def create_rasters(self):
        files = []
        print("Create rasters for: "+self.path)
        for band in self.bands:
            print('Converting band '+band)
            band_file = self.path+'/'+self.resolution+'/'+band
            ds = gdal.Open(band_file+'.jp2')
            if not os.path.isfile(band_file+'.tif'):
                gdal.Translate(band_file+'.tif', ds, outputType=gdalconst.GDT_UInt16, width=5376, height=5376)
            ds = None
            files.append(tf.imread(band_file+'.tif'))
        return np.moveaxis(np.stack(files), 0, 2)

    # Input variables: clc_map_path - String, path to CLC map.
    # Output: Labels have been aligned with the tile and saved as a raster file
    def create_labels(self, labels_path):
        assert len(self.bands) > 0, "Bands may not be empty"
        tile_dir = self.path+'/'+self.resolution
        band_file = tile_dir + '/' + self.bands[0] + '.tif'
        clipper_path = tile_dir + '/clipper.shp'
        assert os.path.isfile(band_file), "You have to rasterize the tile first."
        labels_output = tile_dir+'/labels.tif'
        labels_translated = tile_dir+'/labels_translated.tif'
        projection = tile_dir.split('/')[-2][0:2]
        if not os.path.isfile(labels_output):
            os.system('gdaltindex '+clipper_path+' '+band_file)
            os.system('gdalwarp -t_srs EPSG:326'+projection+' -overwrite -cutline '+clipper_path
                      + ' -crop_to_cutline '+labels_path+' '+labels_output)
            ds = gdal.Open(labels_output)
            gdal.Translate(labels_translated, ds, width=5376, height=5376)
        os.system('rm '+tile_dir+'/labels.tif && '+'mv '+tile_dir+'/labels_translated.tif '+tile_dir+'/labels.tif')
        ds = None
        return tf.imread(labels_output)

    # Input variables: None
    # Output: An absolute path to the tile
    def get_path(self):
        return self.path


class TileContainer:
    """
        Description:
            An instance of this class is a container for zero or more tiles
    """
    # Input variables: tiles - list of tiles
    def __init__(self, tiles):
        self.tiles = tiles

    # Input variables: destination - path to a destination folder,
    #                  class_dict_path - path to class csv file
    #                  labels_path - path to label raster file
    # After: Datasets have been created and saved in the destination folder
    def create_dataset(self, destination, class_dict_path, labels_path):
        feature_arrays = []
        labels_arrays = []
        for tile in self.tiles:
            feature_arrays.append(tile.create_rasters())
            labels_arrays.append(Utils.one_hot_it(tile.create_labels(labels_path)[:, :, :3], class_dict_path))
        x = np.stack(feature_arrays)
        y = np.stack(labels_arrays)
        os.system('rm -rf '+destination+' && mkdir '+destination)
        np.save(destination+'/X.npy', x)
        np.save(destination+'/y.npy', y)

    # Input variables: None
    # After: Path to all tiles in this container has been written out to standard output.
    def print_tile_paths(self):
        for tile in self.tiles:
            print(tile.get_path())


class Cropper:
    """
        Description:
            The purpose of this class is to crop and split an already generated dataset
            into training and validation data sets
    """

    # Input variables: path - absolute path to the dataset folder
    def __init__(self, path):
        self.path = path

    # Input variables: size - crop size in pixels
    # After: The dataset has been split into size x size tiles and saved in self.path directory.
    def crop(self, size):
        x_cropped = []
        y_cropped = []
        x = np.load(self.path+'/X.npy')
        y = np.load(self.path+'/y.npy')

        for i in range(x.shape[0]):
            x_cropped.append(Utils.get_tile_images(x[i], size))
            y_cropped.append(Utils.get_tile_images(y[i], size))

        np.save(self.path+'/X_cropped.npy', np.vstack(x_cropped))
        np.save(self.path+'/y_cropped.npy', np.vstack(y_cropped))

    # Input variables: ratio - float, a ratio of training data. For 80/20 split, ratio would be 0.8
    # After: The datasets have been split and saved  in self.path directory.
    def split(self, ratio):
        x = np.load(self.path+'/X_cropped.npy')
        y = np.load(self.path+'/y_cropped.npy')
        train = np.random.choice(np.arange(x.shape[0]), int(x.shape[0] * ratio), replace=False)
        val = [x for x in range(x.shape[0]) if x not in train]
        x_train = x[train]
        y_train = y[train]
        x_val = x[val]
        y_val = y[val]
        np.save(self.path+'/X_train.npy', x_train)
        np.save(self.path+'/y_train.npy', y_train)
        np.save(self.path+'/X_val.npy', x_val)
        np.save(self.path+'/y_val.npy', y_val)
