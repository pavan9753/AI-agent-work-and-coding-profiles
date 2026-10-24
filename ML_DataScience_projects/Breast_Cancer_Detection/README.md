# Breast Cancer Detection

An educational binary-classification notebook using scikit-learn's Wisconsin diagnostic breast cancer dataset and a small Keras neural network.

**Source repository:** [pavan9753/Breast_Cancer_Detection](https://github.com/pavan9753/Breast_Cancer_Detection)

## Run locally

From this directory:

```bash
python -m venv .venv
```

Activate the environment, then install and launch Jupyter:

```bash
python -m pip install -r requirements.txt
python -m jupyter notebook Breast_Cancer_Detection.ipynb
```

Select **Run All** in Jupyter. The dataset is loaded from scikit-learn, so no separate data download is required.

## Notebook flow

1. Load the built-in dataset and inspect its features.
2. Standardize the measurements.
3. Train a three-layer Keras binary classifier.
4. Evaluate the model and print sample predictions.

This is an introductory notebook. It uses fixed row slices for train, validation, and test data; for a reliable estimate, use a shuffled, stratified split and fit preprocessing only on the training fold. Predictions are for learning and are not medical advice.
