# -*- coding: utf-8 -*-
"""
Created on Sun May 16 10:43:37 2021

@author: Pierce
"""
import pandas as pd
import numpy as np
import catboost as cb
import argparse

def pred_prod(model):
        """

        Parameters
        ----------
        model: CatBoostRegressor model
        Make a default CatBoostRegressor model
        
        features: csv file
        A csv file from user that contains features to predict production 
            

       
        Returns
        -------
        prediction:numpy array of predictions from model 
        
        TODO: Check for missing values or clean with functions from preparing 
        training data
        
        """
        # https://www.datacamp.com/community/tutorials/argument-parsing-in-python
        #Construct the argument parser
        ap = argparse.ArgumentParser()
        # Add argument for input file
        ap.add_argument("-input file path", dest = 'path', required=True, 
                        help ="path to csv file of features needed for model")
        args = vars(ap.parse_args())
        
        #List of features that the model needs
        featureList = []
        
        #read csv and place in dataframe
        dfFeatures = pd.read_csv(args.path)
        
        #Confirm csv has all features required for prediction
        columnList = dfFeatures.columns.values.tolist()
        #https://www.techbeamers.com/program-python-list-contains-elements/
        check = all(item in columnList for item in featureList)
        if check is False:
            #https://stackoverflow.com/questions/41125909/python-find-elements-in-one-list-that-are-not-in-the-other
            missing = np.setdiff1d(featureList, columnList)
            print("Feature file is missing {} features for prediction model".format(missing))
            return
                
        #Drop features that the model does not require
        dfFeatures = dfFeatures[featureList]
        
        
        #Create Numpy Array of features
        FinalFeatures = np.array(dfFeatures)
        
        prediction = model.predict(FinalFeatures)
        
        return prediction