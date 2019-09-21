import csv
import os
import zipfile
import numpy as np


# Input variables: folder - path to a folder to unzip
# After: All zip files in the folder have been unzipped
def unzip(folder):
    for file in [x for x in os.listdir(folder) if x[0] != '.']:
        with zipfile.ZipFile(folder+'/'+file, 'r') as zip_ref:
            zip_ref.extractall(folder)


# Input variables: urban_atlas_dir
# Output: A list with paths to all UA shapefiles.
def get_ua_paths(urban_atlas_dir):
    ua = []
    for dir in [x[0] for x in os.walk(urban_atlas_dir)]:
        if(dir[-10:] == 'Shapefiles'):
            for file in os.listdir(dir):
                if (file[-3:] == 'shp' and file[-5:] != 'y.shp'):
                    ua.append(dir+'/'+file)
    return ua

# Input variables: class_dict_path, a path to a csv file with color values for classes
# Output: List of class names, label values
def get_label_info(class_dict_path):
    class_names = []
    label_values = []
    with open(class_dict_path, 'r') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',')
        header = next(file_reader)
        for row in file_reader:
            class_names.append(row[0])
            label_values.append([int(row[1]), int(row[2]), int(row[3])])
    return class_names, label_values


# Input variables: label, array of rgb values
# Output: one-hot encoded array
def one_hot_it(label, class_dict_path):
    class_names, label_values = get_label_info(class_dict_path)
    semantic_map = []
    for colour in label_values:
        equality = np.equal(label, colour)
        class_map = np.all(equality, axis=-1)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=-1)
    return semantic_map


# Input variables: image - an array to split
#                  size: size in pixels
# Credit: ChoF @ https://stackoverflow.com/questions/48482317/slice-an-image-into-tiles-using-numpy/48483743
def get_tile_images(image, size):

    _nrows, _ncols, depth = image.shape
    _size = image.size
    _strides = image.strides

    nrows, _m = divmod(_nrows, size)
    ncols, _n = divmod(_ncols, size)
    if _m != 0 or _n != 0:
        return None

    return np.lib.stride_tricks.as_strided(
        np.ravel(image),
        shape=(nrows*ncols, size, size, depth),
        writeable=False
    )
