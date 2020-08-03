import tensorflow as tf
import sys
import os
import numpy as np

sys.path.append(os.getcwd())
from categorization.cnn import load_data

print("Loading data...")

image_size = 128
test_images_mouth, test_labels = load_data(
    'data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "mouth")
test_images_face, test_labels = load_data(
    'data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "face")
test_images_skin, test_labels = load_data(
    'data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "skin")
test_images_right_eye, test_labels = load_data(
    'data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "right")

perm = np.random.permutation(len(test_images_mouth))
test_images = [test_images_mouth[perm], test_images_face[perm],
               test_images_skin[perm], test_images_right_eye[perm]]
test_labels = test_labels[perm]

print("Loading model and making predictions...")

stacked = tf.keras.models.load_model(
    "categorization/model_saves/stacked/model.h5")

pred = stacked.predict(test_images)

plt.figure(figsize=(10, 10))
for i in range(25):
    plt.subplot(5, 5, i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(train_images[1][i], cmap=plt.cm.binary)
    # The CIFAR labels happen to be arrays,
    # which is why you need the extra index
    plt.xlabel(pred[i])
plt.show()
