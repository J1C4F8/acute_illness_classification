import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import cv2
import os
import sys
import numpy as np
# from keras.layers.normalization import BatchNormalization
import random

sys.path.append(os.getcwd())
from augment.face_org import *

def load_data(folder_sick, folder_healthy, image_size, type):
    files_healthy = os.listdir(folder_healthy)
    files_sick = os.listdir(folder_sick)
    data = []
    labels = []

    for filename in files_healthy:
        sick = 0
        full_path = folder_healthy + "/" + str(filename)
        if type in filename and "n2-" not in filename and os.path.isfile(full_path):
            image =  cv2.imread(full_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, dsize=(image_size, image_size), interpolation=cv2.INTER_CUBIC)
            data.append(np.asarray(image, dtype = np.int32))
            labels.append(np.asarray(sick, dtype = np.int32))
    for filename in files_sick:
        sick = 1
        full_path = folder_sick + "/" + str(filename)
        if type in filename and os.path.isfile(full_path):
            image =  cv2.imread(full_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, dsize=(image_size, image_size), interpolation=cv2.INTER_CUBIC)
            data.append(np.asarray(image, dtype = np.int32))
            labels.append(np.asarray(sick, dtype = np.int32))

    events = list(zip(data, labels))
    random.shuffle(events)
    data, labels = zip(*events)
    # print(data)
    return np.asarray(data, dtype=np.int32), np.asarray(labels, dtype=np.int32)

def make_model(image_size):
    model = models.Sequential()

    model.add(layers.Conv2D(image_size, (3, 3), activation='relu', input_shape=(image_size, image_size, 3)))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(image_size, (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D((2, 2)))

    model.add(layers.Conv2D(int(image_size/2), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(int(image_size/2), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D((2, 2)))

    model.add(layers.Conv2D(int(image_size/4), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(int(image_size/4), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D((2, 2)))

    model.add(layers.Conv2D(int(image_size/8), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(int(image_size/8), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D((2, 2)))

    model.add(layers.Conv2D(int(image_size/16), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(int(image_size/16), (3, 3), activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.AveragePooling2D((2, 2)))

    model.add(layers.Flatten())
    model.add(layers.Dense(52, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(1, activation='softmax'))

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss="binary_crossentropy",
                metrics=['accuracy'])

    return model




def load_data_eyes(image_folder_sick, image_folder_healthy, image_size):
    images_left, labels_left = load_data(image_folder_sick, image_folder_healthy, image_size, "left")
    images_right, labels_right = load_data(image_folder_sick, image_folder_healthy, image_size, "right")

    images = np.concatenate((images_left, images_right), axis = 0)
    labels = np.concatenate((labels_left, labels_right), axis =0)

    permutation = np.random.permutation(len(images))

    return images(permutation), labels(permutation)


def make_plots(history):
    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0.5, 1])
    plt.legend(loc='lower right')
    fig_path = "data/plots/accuracy_" + str(feature) + ".png"
    plt.savefig(fig_path)

    plt.title('Learning Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Cross Entropy')
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='val')
    plt.legend()
    fig_path = "data/plots/learning_curve_" + str(feature) + ".png"
    plt.savefig(fig_path)



if __name__ == "__main__":
    
    image_folder_sick = 'data/parsed/sick'
    image_folder_healthy = 'data/parsed/healthy'
    image_folder_altered = 'data/parsed/altered'
    image_folder_cfd = 'data/parsed/cfd'
    checkpoint_path = 'categorization/model_saves/'
    image_size = 217
    face_features = ["mouth", "face", "skin", "eyes"]
    neural_nets = []

    for feature in face_features:
        
        if feature == "eyes":
            test_images, test_labels = load_data_eyes(image_folder_sick, image_folder_healthy, image_size)
            train_images, train_labels = load_data_eyes(image_folder_altered, image_folder_cfd, image_size)

        else:
            test_images, test_labels = load_data(image_folder_sick, image_folder_healthy, image_size, feature)
            train_images, train_labels = load_data(image_folder_altered, image_folder_cfd, image_size, feature)

        model = make_model(image_size)

        cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path + str(feature) + "/cp.ckpt",
                                                save_weights_only=True,
                                                verbose=1)

        history = model.fit(train_images, train_labels, epochs=10, 
                        validation_data=(test_images, test_labels), callbacks=[cp_callback])

        neural_nets.append(history)
        make_plots(history)




