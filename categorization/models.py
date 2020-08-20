from tensorflow.keras import layers, models, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import AUC, FalseNegatives, FalsePositives, TruePositives, TrueNegatives


def make_model(image_size, feature):
    model = models.Sequential()

    model.add(layers.Conv2D(image_size, (3, 3), padding="same", activation='relu',
                            input_shape=(image_size, image_size, 3),
                            name="input_" + str(feature)))

    model.add(layers.BatchNormalization(name="batch1_" + str(feature)))
    model.add(layers.Conv2D(int(image_size / 2), (3, 3),
                            activation='relu', name="conv1_" + str(feature)))
    model.add(layers.BatchNormalization(name="batch2_" + str(feature)))
    model.add(layers.MaxPooling2D((2, 2), name="max1_" + str(feature)))

    model.add(layers.Conv2D(int(image_size/4), (3, 3),
                            activation='relu', name="conv2_" + str(feature)))
    model.add(layers.BatchNormalization(name="batch3_" + str(feature)))
    model.add(layers.MaxPooling2D((2, 2), name="max2_" + str(feature)))

    model.add(layers.Conv2D(int(image_size/8), (3, 3),
                            activation='relu', name="conv5_" + str(feature)))
    model.add(layers.BatchNormalization(name="batch6_" + str(feature)))
    model.add(layers.MaxPooling2D((2, 2), name="max3_" + str(feature)))

    model.add(layers.Conv2D(int(image_size/16), (3, 3),
                            activation='relu', name="conv6_" + str(feature)))
    model.add(layers.BatchNormalization(name="batch7_" + str(feature)))
    model.add(layers.AveragePooling2D((2, 2), name="avg1_" + str(feature)))

    model.add(layers.Flatten(name="flatten_" + str(feature)))
    model.add(layers.Dense(48, activation='relu',
                           name="dense1_" + str(feature)))
    model.add(layers.Dropout(0.3, name="dropout1_" + str(feature)))

    model.add(layers.Dense(16, activation='relu',
                           name="dense2_" + str(feature)))
    model.add(layers.Dropout(0.5, name="dropout2_" + str(feature)))

    model.add(layers.Dense(1, activation='sigmoid',
                           name="dense3_" + str(feature)))

    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss="binary_crossentropy",
                  metrics=['accuracy', AUC(), FalseNegatives(),
                           FalsePositives(), TruePositives(), TrueNegatives()])

    return model


def define_stacked_model(neural_nets, features, trainable=True):
    if trainable == False:
        for model in neural_nets:
            for layer in model.layers:
                layer.trainable = False

    ensemble_visible = [model.input for model in neural_nets]
    ensemble_outputs = [model.layers[18].output for model in neural_nets]

    merge = layers.concatenate(ensemble_outputs)
    hidden = layers.Dense(32, activation='relu')(merge)
    hidden_drop = layers.Dropout(0.3)(hidden)
    hidden2 = layers.Dense(16, activation='relu')(hidden_drop)
    hidden3 = layers.Dense(4, activation='relu')(hidden2)
    output = layers.Dense(1, activation='sigmoid')(hidden3)
    model = Model(inputs=ensemble_visible, outputs=output)

    model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001),
                  metrics=['accuracy', AUC()])

    return model


def load_all_models(save_path, features):
    all_models = list()
    for feature in features:
        # filename = save_path + str(feature) + '/save.h5'
        filename = save_path + str(feature) + '/model.h5'
        model = models.load_model(filename)
        all_models.append(model)
        print('loaded model of ' + str(feature))
    return all_models
