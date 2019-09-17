import os
import zipfile

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
