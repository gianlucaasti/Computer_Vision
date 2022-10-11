# INTRODUCTION
**WORK IN PROGRESS: THE PROJECT IS NOT COMPLETED YET**

An AI for object detection. The goal of this project is to create an AI for detection and selection of White Blood Cells, Red Blood Cells, Platelets.

![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)


# PREPROCESSING: Plot of the images with Anchor Boxes
I did this step to be sure that the Anchor Boxes were right and they refered to the correct elements.
This code is largely based on the notebook found at this link:

https://www.kaggle.com/code/raivokoot/plot-images-bounding-boxes-visualization

They are both applied to medical data, but the original one was applied to chest x-rays.

# PREPROCESSING: Labels and Stratified Split
The dataset has unbalanced classes. I stratified the dataset, but I think I will need to oversample the 2 classes with only the 8% of the data.
The FBC column has been copied both to the train folder and the test folder. I did this because is our only sample.
In the train folder I will remove the original picture and keep only the augmented ones after the data augmentation step.
In this code I check the classes and the relative frequencies of the target labels in the dataset.
I have also slightly modified this code to create a stratified sample of the dataset
https://www.kaggle.com/code/backtracking/smart-data-split-train-eval-for-object-detection/notebook

# PREPROCESSING: Gaussian and S&P noise
I have decided to do data augmentation on the train dataset.
The pictures of "Platelets" and "WBC" were augmented creating copies with both Gaussian and S&P noise.
The relevant columns of the csv file for the original images, were copied and associated to the new ones.

**NEXT STEPS**:
<ul>
<li>Augment more data (FNB)</li>
<li>Automate the csv copy-paste step</li>
</ul>


# MODEL_TRAINING: Retinanet
After reading online a few papers and use cases on blood cells detection (eg: https://pubmed.ncbi.nlm.nih.gov/34828220/)
I have decided to implent a CPU version of Retinanet.
I decided to use this model because:
<ul>
<li>I could easily train it with CPU</li>
<li>It was used in different medical studies</li>
<li>Different papers show that it works pretty well with small images</li>
<li>It is a bit slow, but real-time detection wasn't requested</li>
</ul>

You can find:
<ul>
<li><strong>LOGS</strong>: in the TRAINING_LOGS folder. They can be opened in tensorboard</li>
<li><strong>WEIGHTS</strong>: in the TRAINING_WEIGHTS folder. They can be used to further train your network</li>
</ul>

The code is largely based on this notebook: https://www.kaggle.com/code/mahipalsingh/detection-using-keras-retinanet-train

The model was taken from this github repository: https://github.com/fizyr/keras-retinanet

**NEXT STEPS**:
<ul>
<li>Retrain the whole network using mAP</li>
<li>Create a full pipeline to evaluate the model on the validation set. Statistics to check: Recall, Precision, F1</li>
<li>As I mentioned (and I cannot stress this enough) I need to check that the model performs well on the unbalanced classes</li>
</ul>




# Demo Evaluation
The Demo Evaluation folder contains a chunk of the training script to load the model, check the metrics and use it to forecast bounding boxes and classes over a sample of validation data

**NEXT STEPS**:
<ul>
<li>The mAP values are ok but I would like to do oversampling on certain classes</li>
<li>I am considering doing undersampling of RBC</li>
<li>Get and plot a proper confusion matrix for more informations</li>
</ul>