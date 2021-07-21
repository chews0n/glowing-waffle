# Glowing Waffle

## Introduction
This project is an undertaking for the 2021 SPE Calgary Data Science Mentorship Program. The following people were involved in this project:

- Chris Hewson - Resfrac
- Harrison Wood - Pason
- Pierce Anderson - ARC Resources
- Brendan Danyluik - CalFrac Well Services

The goal of this project was to create model that accurately predicts production values from Montney Basin wells, given a certain fracture design.

## Install
This project requires [Python 3](https://www.python.org/) and the following Python Libraries:

- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)
- [scikit-learn](https://scikit-learn.org/stable/)
- [CatBoost](https://catboost.ai/docs/installation/python-installation-method-pip-install.html#python-installation-method-pip-install)
- [datetime](https://pypi.org/project/DateTime/)
- [requests](https://pypi.org/project/requests/)
- [regex](https://pypi.org/project/regex/)
- [zipfile36](https://pypi.org/project/zipfile36/)

All of these can be installed from the requirements.txt file in the repository using the following command:

    pip install -r requirements.txt

To install the package, run the setup.py file, python 3.5 and above is required

    python setup.py install

## Usage
glowing-waffle can be used as a python package or as a standalone executable. The executable requires certain inputs in order to run that have default values.

Once installed, glowing-waffle can be used as a stand alone executable, the following command will display the usage of the standalone:
```shell script
glowing-waffle -h
```
Additionally, it should be noted that the input file required to predict IP90/IP180 for a particular well should follow the same format as the [template](templates/input_values_template.csv) within this repository. Please note that a lot of text based inputs require numbers to map to the enums, this template should be made more user friendly in the future.


## Model
Using a random forest model implemented in the CatBoost library, we will gather the necessary features and targets from public petroleum data sources for the Montney (using SQL/REST calls). 

Uncertainty can be applied by using separate sets to train the model(s). By acquiring different models using slightly different data sets, we will be able to more quantifiably capture uncertainty and the bounds of the outputs obtained from the model(s).

Once the model is trained, we will test the accuracy and predictability of the model using both a subset of the data that we have set aside and in comparison to a reservoir and fracture simulator. This will give us a good idea of the dependability of the model that has been created.

## Data
Publicly available production and well data was used for the Montney Basin in order to accurately train the model. This choice was made in order for the model to have wide applicability throughout the oil and gas industry.

### Features
This is a working list of features and will be modified as the project evolves:

#### Frac Design

1. Proppant per metre (or per stage)
2. Total Fluid
3. Fluid per metre (or per stage)
4. Total Proppant
5. Proppant concentration (max, or average?)
6. Average injection rate
7. Average treating pressure
8. Average frac gradient
9. Energizer (N2, CO2)
10. Frac type
11. Tonnage per meter
12. Frac fluid - type and composition (if available)

NB: Averages can skew the data significantly, make sure that you're using the right average

#### Well Design

1. Length of well
2. Stage spacing
    1. Cluster spacing and shots per cluster
3. Latitude, longitude and depth/TVD
4. Parent-Child effects - ie. distance from parent well

#### Geology

1. Initial flow back
2. Rate of Flow Back
3. Leak off rate
4. Rock properties (perm, poro, stresses)
5. Reservoir Pressure
6. Saturations 

### Targets

This is a working list of features and will be modified as the project evolves:

1. Initial Production in the first 90 days (IP90)
2. Initial Production in the first 180 days (IP180)

## License
Glowing Waffle is licensed under the Apache License, Version 2.0. See LICENSE for the full license text.