# -*-coding:utf-8-*-

"""

Retrain the YOLO model for your own dataset.

"""

import numpy as np
import keras.backend as K
from keras.layers import Input, Lambda
from keras.models import Model
from keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping
from yolo3.model import preprocess_true_boxes, yolo_body, tiny_yolo_body, yolo_loss
from yolo3.utils import get_random_data
import tensorflow as tf
import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   
os.environ["CUDA_VISIBLE_DEVICES"]="0"
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
def _main():
    annotation_path = 'D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\label_select_num_trainval.txt'
    log_dir = 'D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\logs\\004\\'
    classes_path = 'D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\model_data\\sign_classes.txt'
    anchors_path = 'D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\model_data\\yolo_anchors.txt'
    weights_path = 'D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\logs\\001\\ep308-loss6.655-val_loss6.712.h5'
    load_pretrained = True
    class_names = get_classes(classes_path)
    anchors = get_anchors(anchors_path)
    input_shape = (416,416) # multiple of 32, hw
    model = create_model(input_shape, anchors, len(class_names), weights_path,load_pretrained )
    train(model, annotation_path, input_shape, anchors, len(class_names), log_dir=log_dir)

 

def train(model, annotation_path, input_shape, anchors, num_classes, log_dir):
    model.compile(optimizer='adam', loss={'yolo_loss': lambda y_true, y_pred: y_pred})
    logging = TensorBoard(log_dir=log_dir)
    checkpoint = ModelCheckpoint(log_dir + "ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5",
        monitor='val_loss', save_weights_only=True, save_best_only=True, period=1)
    callbacks_list=[checkpoint]
    batch_size = 10
    val_split = 0.2
    with open(annotation_path) as f:
        lines = f.readlines()
    np.random.shuffle(lines)
    num_val = int(len(lines)*val_split)
    num_train = len(lines) - num_val


    print('Train on {} samples, val on {} samples, with batch size {}.'.format(num_train, num_val, batch_size))
 
    model.fit_generator(data_generator_wrap(lines[:num_train], batch_size, input_shape, anchors, num_classes),
            steps_per_epoch=max(1, num_train//batch_size),
            validation_data=data_generator_wrap(lines[num_train:], batch_size, input_shape, anchors, num_classes),
            validation_steps=max(1, num_val//batch_size),
            epochs=500,
            initial_epoch=0,callbacks=callbacks_list)
    model.save_weights(log_dir + 'trained_weights.h5')
 
def get_classes(classes_path):
    with open(classes_path) as f:
        class_names = f.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names

def get_anchors(anchors_path):
    with open(anchors_path) as f:
        anchors = f.readline()
    anchors = [float(x) for x in anchors.split(',')]
    return np.array(anchors).reshape(-1, 2)
 
def create_model(input_shape, anchors, num_classes, weights_path, load_pretrained, freeze_body=False):
    K.clear_session() # get a new session
    image_input = Input(shape=(None, None, 3))
    h, w = input_shape
    num_anchors = len(anchors)
    y_true = [Input(shape=(h//{0:32, 1:16, 2:8}[l], w//{0:32, 1:16, 2:8}[l], \
        num_anchors//3, num_classes+5)) for l in range(3)]

    model_body = yolo_body(image_input, num_anchors//3, num_classes)
    print('Create YOLOv3 model with {} anchors and {} classes.'.format(num_anchors, num_classes))

    if load_pretrained:
        model_body.load_weights(weights_path, by_name=True, skip_mismatch=True)
        print('Load weights {}.'.format(weights_path))
        if freeze_body:
            # Do not freeze 3 output layers.
            num = len(model_body.layers)-7
            for i in range(num): model_body.layers[i].trainable = False
            print('Freeze the first {} layers of total {} layers.'.format(num, len(model_body.layers)))
 
    model_loss = Lambda(yolo_loss, output_shape=(1,), name='yolo_loss',
        arguments={'anchors': anchors, 'num_classes': num_classes, 'ignore_thresh': 0.5})(
        [*model_body.output, *y_true])
    model = Model([model_body.input, *y_true], model_loss)
    return model

def data_generator(annotation_lines, batch_size, input_shape, anchors, num_classes):
    n = len(annotation_lines)
    np.random.shuffle(annotation_lines)
    i = 0
    while True:
        image_data = []
        box_data = []
        for b in range(batch_size):
            i %= n
            image, box = get_random_data(annotation_lines[i], input_shape, random=True)
            image_data.append(image)
            box_data.append(box)
            i += 1
        image_data = np.array(image_data)
        box_data = np.array(box_data)
        y_true = preprocess_true_boxes(box_data, input_shape, anchors, num_classes)
        yield [image_data, *y_true], np.zeros(batch_size)

def data_generator_wrap(annotation_lines, batch_size, input_shape, anchors, num_classes):
    n = len(annotation_lines)
    if n==0 or batch_size<=0: return None
    return data_generator(annotation_lines, batch_size, input_shape, anchors, num_classes)

if __name__ == '__main__':
    _main()
