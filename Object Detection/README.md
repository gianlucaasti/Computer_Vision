# INTRODUCTION
An AI for object detection. The goal of this project is to create an AI for detection and selection of White Blood Cells, Red Blood Cells, Platelets.


# PREPROCESSING: Plot of the images with Anchor Boxes
I did this step to be sure that the Anchor Boxes were right and they refered to the correct elements.
This code is largely based on the notebook found at this link:

https://www.kaggle.com/code/raivokoot/plot-images-bounding-boxes-visualization

They are both applied to medical data, but the original one was applied to chest x-rays.

#PreProcessing Labels and Stratified Split
The dataset has unbalanced classes. I stratified the dataset, but I think I will need to oversample the 2 classes with only the 8% of the data.
The FBC column has been copied both to the train folder and the test folder. I did this because is our only sample.
In the train folder I will remove the original picture and keep only the augmented ones after the data augmentation step.
In this code I check the classes and the relative frequencies of the target labels in the dataset.
I have also slightly modified this code to create a stratified sample of the dataset
https://www.kaggle.com/code/backtracking/smart-data-split-train-eval-for-object-detection/notebook
