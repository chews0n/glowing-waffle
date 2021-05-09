import pandas as pd
import os
import sys


class ReadData:

    def __init__(self):

        self.files = list()
        self.pd_dict = {}
        self.df = None
        self.featureDf = None
        self.outputDf = None

    def read_csv_folder(self, folder=None):
        """
        Read in the csv data and concatenate it into a pandas object
        Parameters
        ----------
        folder: string , required (default=None)
                The absolute or relative path to the folder that you want to search in for csv files
        """

        # read in the files in the folder, this will be best in case you need to do something with the files later
        # instead of reading them directly into a pandas array, reads in all file types

        if not os.path.exists(folder):
            sys.exit("The folder supplied: " + folder + " does not exist")
        idx = 0
        files_with_headers = ['zone_prd.csv', 'zone_prd_1954_to_2006.csv', 'zone_prd_2007_to_2015.csv',
                              'zone_prd_2016_to_present.csv', 'f_operator.csv', 'plant_jur_code.csv', 'pst.csv',
                              'f_receipt.csv', 'aban_frm.csv', 'pst_dtl.csv', 'dst.csv', 'aban_dtl.csv', 'gas_anal.csv',
                              'drill_ev.csv', 'oil_dist.csv', 'form_top.csv', 'oil_anal.csv', 'aofp_tst.csv',
                              'oil_visc.csv', 'clients.csv', 'w_status.csv', 'projects.csv', 'c_status.csv',
                              'codes.csv', 'area.csv', 'wells.csv', 'logs_run.csv', 'compl_ev.csv', 'dst_rate.csv',
                              'facilities.csv', 'pools.csv', 'f_design.csv', 'wtr_anal.csv', 'f_processing.csv',
                              'aofp_dtl.csv', 'water_gas_disposal.csv', 'casings.csv', 'pay_zone.csv', 'compl_wo.csv',
                              'wtr_inj.csv', 'gas_inj.csv', 'core_cut.csv', 'f_flaring_app.csv', 'f_type.csv']

        for filename in os.listdir(folder):
            # only read in csv files
            if filename.lower().endswith('.csv'):

                if filename.lower() in files_with_headers:
                    print(f"reading in {filename}")
                    self.files.append(filename)
                    self.pd_dict[self.files[idx]] = pd.read_csv(os.path.join(folder, self.files[idx]), low_memory=False, skiprows=1, encoding ='latin1')
                    idx += 1
                else:
                    print(f"reading in {filename}")
                    self.files.append(filename)
                    self.pd_dict[self.files[idx]] = pd.read_csv(os.path.join(folder, self.files[idx]), low_memory=False, encoding ='latin1')
                    idx += 1

        if len(self.pd_dict) == 0:
            sys.exit("The folder supplied: " + folder + " does not contain any files, please revise")

        # Will concatenate later with other data frames
        # self.df = pd.concat(self.pd_array)

    def clean_data(self, columns_to_drop=None):
        """
        Clean the data in the data array and remove the NaN values

        Parameters
        ----------
        columns_to_drop: list, optional (default=None)
            A list of column strings to be removed from the pandas data object.
        Returns
        -------
        None
        """
        # Drop columns that are not part of the feature list
        self.df = self.df.drop(columns=columns_to_drop, axis=1)

        # Drop only completely empty rows
        # TODO: Create additional clean functions in case you need partial data from rows or want to set certain
        #  NaN values to a number
        self.df = self.df.dropna(how='all')

    def split_features_and_outputs(self, output_list=None):
        """
        Split the data frame into features and outputs in order to train and or test the model. This assumes that the
        df variable only contains features and outputs
        Parameters
        ----------
        output_list: list, required (default=None)
            List of outputs to use in the model
        Returns
        -------
        None
        """

        self.featureDf = self.df.drop(columns=output_list, axis=1)
        self.outputDf = self.df[output_list]
