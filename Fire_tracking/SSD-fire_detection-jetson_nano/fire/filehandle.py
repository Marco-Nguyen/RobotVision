import os
import glob

start_path = r'valid'
path_to_ann = r'val/ann'
path_to_img = r'val/img'

print(len(os.listdir(start_path)))
list_img_names = glob.glob(os.path.join(start_path, '*.jpg'))
list_ann_names = glob.glob(os.path.join(start_path, '*.xml'))

print(len(list_ann_names), len(list_img_names))
for img in list_img_names[:]:
    olddir, img_name = os.path.split(img)
    try:
    	os.renames(os.path.join(olddir, img_name), os.path.join(path_to_img, img_name))
    except Exception:
    	pass

for ann in list_ann_names[:]:
    olddir, ann_name = os.path.split(ann)
    try:
    	os.renames(os.path.join(olddir, ann_name), os.path.join(path_to_ann, ann_name))
    except Exception:
    	pass
print(len(list_ann_names), len(list_img_names))


start_path = r'train'
path_to_ann = r'train/ann'
path_to_img = r'train/img'

print(len(os.listdir(start_path)))
list_img_names = glob.glob(os.path.join(start_path, '*.jpg'))
list_ann_names = glob.glob(os.path.join(start_path, '*.xml'))

print(len(list_ann_names), len(list_img_names))
for img in list_img_names[:]:
    olddir, img_name = os.path.split(img)
    try:
    	os.renames(os.path.join(olddir, img_name), os.path.join(path_to_img, img_name))
    except Exception:
    	pass

for ann in list_ann_names[:]:
    olddir, ann_name = os.path.split(ann)
    try:
    	os.renames(os.path.join(olddir, ann_name), os.path.join(path_to_ann, ann_name))
    except Exception:
    	pass
print(len(list_ann_names), len(list_img_names))
