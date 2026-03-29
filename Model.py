import os
os.environ['KERAS_HOME'] = os.path.join(os.getcwd(), 'keras_cache')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


import seaborn as sns
from tensorflow.keras.applications import Xception
# Libraries for TensorFlow
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing import image
from tensorflow.keras import models, layers

# Library for Transfer Learning
from tensorflow.keras.applications import VGG16
from keras.applications.xception import preprocess_input

print("Importing libraries completed.")

path = 'Dataset/'

train_folder = path + "Train/"

# variables for image size
img_width = 200
img_height = 200

# variable for model
batch_size = 16
epochs = 5

print("Variable declaration completed.")

# listing the folders containing images

# Train Dataset
train_class_names = os.listdir(train_folder)
print("Train class names: %s" % (train_class_names))
# print("\n")

print("\nDataset class name listing completed.")

# declaration of functions


# Declaring variables
x = []  # to store array value of the images
y = []  # to store the labels of the images

for folder in os.listdir(train_folder):
    image_list = os.listdir(train_folder + "/" + folder)
    for img_name in image_list:
        # Loading images
        img = image.load_img(train_folder + "/" + folder + "/" + img_name, target_size=(img_width, img_height))

        # Converting to arrary
        img = image.img_to_array(img)

        # Transfer Learning: this is to apply preprocess of VGG16 model to our images before passing it to VGG16
        img = preprocess_input(img)  # Optional step

        # Appending the arrarys
        x.append(img)  # appending image array
        y.append(train_class_names.index(folder))  # appending class index to the array

print("Preparing Training Dataset Completed.")

# Preparing validation images data (image array and class name) for processing


# Training Dataset
print("Training Dataset")

x = np.array(x)  # Converting to np arrary to pass to the model
print(x.shape)

y = to_categorical(y)  # onehot encoding of the labels
# print(y)
print(y.shape)

# ===========
# Test Dataset
print("Test Dataset")

print("Summary of default Xception model.\n")

from tensorflow.keras.applications import Xception

# initializing model with weights='imagenet'i.e. we are carring its original weights
xcmodel = Xception(weights='imagenet')

# display the summary to see the properties of the model
xcmodel.summary()

input_layer = layers.Input(shape=(img_width, img_height, 3))

xcmodel = Xception(weights='imagenet', input_tensor=input_layer, include_top=False)

xcmodel.summary()

model = models.Sequential()
last_layer = xcmodel.output  # we are taking last layer of the model

# Add flatten layer: we are extending Neural Network by adding flattn layer
flatten = layers.Flatten()(last_layer)

# Add dense layer
dense1 = layers.Dense(100, activation='relu')(flatten)

# Add dense layer to the final output layer
output_layer = layers.Dense(4, activation='softmax')(flatten)

# Creating modle with input and output layer
model = models.Model(inputs=input_layer, outputs=output_layer)

# Summarize the model
model.summary()

# we will freez all the layers except the last layer

# we are making all the layers intrainable except the last layer
print("We are making all the layers intrainable except the last layer. \n")
for layer in model.layers[:-1]:
    layer.trainable = False
model.summary()

from sklearn.model_selection import train_test_split

xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2, random_state=0)

print("Splitting data for train and test completed.")

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

print("Model compilation completed.")

history2 = model.fit(xtrain, ytrain, epochs=epochs, batch_size=batch_size, verbose=True, validation_data=(xtest, ytest))
print(xtrain.shape)
print(ytrain.shape)
print("Fitting the model completed.")

model.save("Xception.h5")
acc = history2.history['accuracy']
val_acc = history2.history['val_accuracy']
epochs = range(len(acc))

plt.plot(epochs, acc, label='Training Accuracy')
plt.plot(epochs, val_acc, label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.show()

# Plot Model Loss
loss_train = history2.history['loss']
loss_val = history2.history['val_loss']
plt.plot(epochs, loss_train, label='Training Loss')
plt.plot(epochs, loss_val, label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.show()

y_pred = model.predict(xtest)
y_pred = np.argmax(y_pred, axis=1)
print(y_pred)
y_test = np.argmax(ytest, axis=1)
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
print(cm)

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix of Xception')
plt.show()
