from os.path import join, isdir
from os import listdir
import argparse
import json
import glob
import xml.etree.ElementTree as ET

# Parse command line arguments
parser = argparse.ArgumentParser(description='Parse the VID Annotations for training DCFNet')
parser.add_argument('data', metavar='DIR', help='path to VID')
args = parser.parse_args()

# Set base paths
print('VID2015 Data:')
VID_base_path = args.data
ann_base_path = join(VID_base_path, 'Annotations/VID/train/')
img_base_path = join(VID_base_path, 'Data/VID/train/')
sub_sets = ["ILSVRC2015_VID_train_0000", "ILSVRC2015_VID_train_0001"] # sorted({'a', 'b', 'c', 'd', 'e'})

# Collect all video frames and their annotations
# into a JSON file
vid = []
for sub_set in sub_sets:
    sub_set_base_path = join(ann_base_path, sub_set)
    videos = sorted(listdir(sub_set_base_path))
    s = []
    for vi, video in enumerate(videos):
        # For the moment only use 20 videos per subset
        if vi == 20:
            break

        print('subset: {} video id: {:04d} / {:04d}'.format(sub_set, vi, len(videos)))
        v = dict()
        v['base_path'] = join(img_base_path, sub_set, video)
        v['frame'] = []
        video_base_path = join(sub_set_base_path, video)
        xmls = sorted(glob.glob(join(video_base_path, '*.xml')))
        for xml in xmls:
            f = dict()
            xmltree = ET.parse(xml)
            size = xmltree.findall('size')[0]
            frame_sz = [int(it.text) for it in size]
            objects = xmltree.findall('object')
            objs = []
            for object_iter in objects:
                trackid = int(object_iter.find('trackid').text)
                name = (object_iter.find('name')).text
                bndbox = object_iter.find('bndbox')
                occluded = int(object_iter.find('occluded').text)
                o = dict()
                o['c'] = name
                o['bbox'] = [int(bndbox.find('xmin').text), int(bndbox.find('ymin').text),
                             int(bndbox.find('xmax').text), int(bndbox.find('ymax').text)]
                o['trackid'] = trackid
                o['occ'] = occluded
                objs.append(o)
            f['frame_sz'] = frame_sz
            f['img_path'] = xml.split('/')[-1].replace('xml', 'JPEG')
            f['objs'] = objs
            v['frame'].append(f)
        s.append(v)
    vid.append(s)


print('save json (raw vid info), please wait 1 min~')
json.dump(vid, open('vid.json', 'w'), indent=2)
print('done!')

