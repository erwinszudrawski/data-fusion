from modules import Generator
import os

dataset = 'base_poland'
data = '/Volumes/ssd/data/products/'+dataset
output_path = '/Volumes/ssd/data/datasets/'+dataset
bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12', 'SCL']
clc_path = '/Volumes/ssd/data/corine/33tun.tif'
resolution = 'R20m'

tile_container = Generator.TileContainer(
    [Generator.Tile(data+'/'+x, bands, resolution) for x in os.listdir(data) if x[0] != '.']
)
tile_container.create_dataset(output_path, '/Volumes/ssd/data/class_dict.csv', '/Volumes/ssd/data/corine/rendered_poland.tif')

cropper = Generator.Cropper(output_path)
cropper.crop(256)
cropper.split(0.8)