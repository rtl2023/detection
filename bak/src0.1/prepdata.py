import os
import sys
import numpy as np
import pickle
import h5py
from PIL import Image
from scipy import misc
from scipy import io as sio
import matplotlib.pyplot as plt


def get_image_num(path, ext):
    sizes = []
    for dir in os.listdir(path):
        lable_num, lable_name = dir.split('~')
        sizes += [0]
        for root, dirs, files in os.walk(os.path.join(path, dir)):
            for file in files:
                f = os.path.join(root, file)
                if os.path.splitext(f)[1] == ext:
                    sizes[-1] += 1
    return sizes


def get_train_data(path, ext, size, *, is_resize=1):
    """ Create the image db for training
    
    Input: image path, extension name, picture size=(w,h,c)
    
    The folder structure should be [lable_number]~[lable name] to distinguish class,
        eg. 0~abnormal, 1~normal
    Each image (in [path]/*.[ext]) will be load into imdb as well as its table.
    The mode of the image must be all the same.
        
    Output: x_train, y_train, info=('size','lable_name','avg_image')
    
    """
    s = get_image_num(path, ext)
    n = sum(s)
    output = len(s)
    x_train = np.empty((n,) + size, dtype='float32')
    y_train = np.zeros((n,output), dtype='float32')
    info = dict()
    info['count'] = 0
    info['size'] = size
    info['avg_image'] = np.zeros(size, dtype='float32')
    info['image_path'] = []
    info['lable_name'] = []
    if is_resize == 0:
        size = None
    for dir in os.listdir(path):
        lable_num, lable_name = dir.split('~')
        info['lable_name'].append (lable_name)
        for root, dirs, files in os.walk(os.path.join(path, dir)):
            for file in files:
                f = os.path.join(root, file)
                if ext == os.path.splitext(f)[1]:
                    arr = load_image(f, resize=size)
                    y_train[info['count']][lable_num] = 1
                    x_train[info['count']] = arr
                    print(f + '  has been loaded')
                    info['image_path'].append(str(f))
                    info['avg_image'] += arr
                    info['count'] += 1
    info['avg_image'] /= info['count']
    print('Getting training data successfully !')
    return x_train, y_train, info


def subavg_data(img, avg_img):
    for i in range(0, img.shape[0]):
        img[i]-=avg_img


def save_mat_data(path, varname, arr):
    sio.savemat(path, {varname: arr})


def load_mat_data(path, varname):
    arr = sio.loadmat(path)
    return arr[varname]


def save_train_data(path, x_train, y_train, info):
    sio.savemat(os.path.join(path, 'x_train.mat'),{'x_train':x_train})
    print("%s(%.3f mb) has been saved in %s" % ('x_train', sys.getsizeof(x_train) / 1000000, path))
    sio.savemat(os.path.join(path, 'y_train.mat'), {'y_train': y_train})
    print("%s(%.3f mb) has been saved in %s" % ('y_train', sys.getsizeof(y_train) / 1000000, path))
    pickle.dump(info, open(os.path.join(path, 'info.pkl'),'wb'))
    # io.savemat(os.path.join(path, 'info.mat'),{'info':info})
    # print("%s(%.3f mb) has been saved in %s" % ('info', sys.getsizeof(info) / 1000000, path))


def load_train_data(path):
    d = sio.loadmat(os.path.join(path, 'x_train.mat'))
    x_train = d['x_train']
    print("%s(%.3f mb) has been loaded in %s" % ('x_train', sys.getsizeof(x_train) / 1000000, path))
    d = sio.loadmat(os.path.join(path, 'y_train.mat'))
    y_train = d['y_train']
    print("%s(%.3f mb) has been loaded in %s" % ('y_train', sys.getsizeof(y_train) / 1000000, path))
    info = pickle.load(open(os.path.join(path, 'info.pkl'), 'rb'))
    # d = h5py.File(os.path.join(path, 'info.mat'), 'r') #??????mat????????????
    # d = io.loadmat(os.path.join(path, 'info.mat'),struct_as_record=0)
    # info = d['info']
    #???print("%s(%.3f mb) has been loaded in %s" % ('info', sys.getsizeof(info) / 1000000, path))
    return x_train, y_train, info


def load_train_data2(path):
    d = sio.loadmat(os.path.join(path, 'xavg_train.mat'))
    x_train = d['xavg_train']
    print("%s(%.3f mb) has been loaded in %s" % ('xavg_train', sys.getsizeof(x_train) / 1000000, path))
    d = sio.loadmat(os.path.join(path, 'y_train.mat'))
    y_train = d['y_train']
    print("%s(%.3f mb) has been loaded in %s" % ('y_train', sys.getsizeof(y_train) / 1000000, path))
    info = pickle.load(open(os.path.join(path, 'info.pkl'), 'rb'))
    return x_train, y_train, info

def load_image(path, resize=None):
    im = Image.open(path)
    if resize:
        im = misc.imresize(im, resize)
    arr = np.asarray(im, dtype='float32')
    if resize:
        arr = arr.reshape(resize)
    return arr


def save_image(path, arr, resize=None):
    if resize:
        arr = arr.reshape(resize)
    im = Image.fromarray(arr)
    misc.imsave(path, im)


if __name__ == '__main__':
    x_train, y_train, info=get_train_data("D:\\ProcMake\\current\\ABD\\row\\cnn_uscd_biclassification",'.tif',(260, 260, 1),is_resize=1)
    save_train_data("D:\\ProcMake\\current\\ABD\\intermediate\\train_data",x_train,y_train,info)
    #x_train, y_train, info = load_train_data("D:\\ProcMake\\current\\ABD\\intermediate\\train_data")
    subavg_data(x_train, info['avg_image'])
    save_mat_data(os.path.join("D:\\ProcMake\\current\\ABD\\intermediate\\train_data", 'xavg_train.mat'),'xavg_train', x_train)
    arr = x_train[3345]
    #arr=info['avg_image']
    #avg = info['avg_image']
    save_image("D:\\ProcMake\\current\\ABD\\image\\2.png", arr, (260, 260))
