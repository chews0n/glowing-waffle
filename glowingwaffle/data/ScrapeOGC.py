import requests
from requests.exceptions import HTTPError
import regex
import sys
import os
import zipfile36 as zipfile
from glowingwaffle.data import ReadData
import pandas as pd
from itertools import chain
import numpy as np


# TODO: Extend this also to the AER, maybe??

class ScrapeOGC:

    def __init__(self, folder=None, urls=None):
        self.urls = list()
        self.file_names = list()
        self.output_folder = folder
        self.wa_num = list()
        self.urls = urls
        self.dataframes_dict = {}
        self.feature_list = None
        self.removal_list = list()
        self.multiple_wells = list()
        self.multiple_names = list()
        self.multiple_list = ['compl_ev.csv', 'dst.csv', 'pst_dtl.csv', 'dst_rate.csv', 'perf_net_interval.csv']

        if folder is not None and not os.path.exists(folder):
            # create a folder if the folder does not currently exist
            try:
                os.mkdir(folder)
            except OSError as err:
                sys.exit(f'Error Occurred creating directory: {err}')

    def download_data_url(self, file_names=None, force_download=False):
        """
        Download the CSV data from the URLS given in the list of URLS, while we are currently using this for
        the data from the Oil and Gas Council of BC, this can be extended to any file that has a URL, including
        none CSV data. If no folder supplied, the file will be downloaded to the Current Working Directory

        Parameters
        ----------
        self

        Returns
        -------
        None
        """

        # Check if the necessary files have already been downloaded
        dont_download_flag = True

        # Have the ability to force the program to download in order to update the files that may already exist in
        # the folder
        if force_download:
            dont_download_flag = False

        for key in file_names:
            if not os.path.exists(os.path.join(self.output_folder, key)):
                dont_download_flag = False

        if dont_download_flag:
            print(f"All files already exist in the folder: {self.output_folder}, continuing to read in the data to "
                  f"data frames \n")
            return

        # loop over the requested urls to download the files to the computer
        for idx, dlurls in enumerate(self.urls):

            try:
                # Perform a GET request for the files listed in the URLS in the urls list
                print(f"Downloading file #{idx + 1} of {len(self.urls)} with url: {dlurls}")
                response = requests.get(dlurls, allow_redirects=True)

                # If the response was successful, no Exception will be raised
                response.raise_for_status()
            except HTTPError as http_err:
                sys.exit(f'HTTP error occurred while downloading file: {http_err}')
            except Exception as err:
                sys.exit(f'Other error occurred while downloading file: {err}')
            else:
                # open the file and save it to a location
                # this is specific to the OGC header data, so be careful when extending
                if 'content-disposition' in response.headers.keys():
                    output_filename = regex.search(r"filename=\"([^']*)\";",
                                                   response.headers['Content-Disposition']).group(1)
                else:
                    output_filename = dlurls.split('/')[-1]

                if self.output_folder is not None:
                    # gives the full path of the file for writing and saving
                    output_filename = os.path.join(self.output_folder, output_filename)

                try:
                    f = open(output_filename, 'wb')
                    # check if we were able to open the file
                except OSError:
                    sys.exit(f"Could not open the file: {output_filename}")
                with f:
                    # write the content of the get request to the file that was opened
                    f.write(response.content)

                # save the filename to the list of the OGCData option
                self.file_names.append(output_filename)

        print("Finished Downloading the files from OGC")

        print("Unzipping any Zipped downloads")
        self.unzip_folders()

    def unzip_folders(self):
        """
        Extract zip files if they were downloaded during the scraping from the OGC Website

        Parameters
        ----------
        self

        Returns
        -------
        None
        """
        # Loop through all of the downloaded files from OGC
        for idx, files in enumerate(self.file_names):
            # Check if the file is in fact a zip file
            if zipfile.is_zipfile(files):
                print(f"Unzipping {files}")

                zf = zipfile.ZipFile(files, 'r')

                # Extract the zip file into the specified folder
                zf.extractall(self.output_folder)
                zf.close()

                # Delete the zip files now that we have extracted them
                os.remove(files)

    def find_in_data_frames_dict(self, file_name=None, list_of_values=None, column=""):
        """

        Parameters
        ----------
        file_name string
        list_of_values list
        column string

        Returns
        -------
        df: pandas dataframe
        """

        # types of well authorization number header

        if column == "":
            WA_HEADER_NAMES = ['Wa Num', 'WA Num', 'Wa_num', 'WA_num', 'WA_NUM', 'WA_Num', 'Wa_Num', 'WA NUM',
                               'WA Number', 'Well Authorization Number']

            for header_names in self.dataframes_dict[file_name].columns:
                for wa_names in WA_HEADER_NAMES:
                    if header_names == wa_names:
                        column = header_names
                        break

                if not column == "":
                    break

            if column == "":
                sys.exit(
                    f'Error Occurred, could not find a well authorization header in: {file_name}, please check the file')

        df = self.dataframes_dict[file_name].loc[self.dataframes_dict[file_name][column].isin(list_of_values)]

        return df, column

    def find_well_names(self, area_code=None, formation_code=None):
        """
        Find all of the well names and UWI identifiers in the areas or formations that are defined
        :param area_code: list, required (default = None)
                        The list of OGC area codes that are areas of interest to grab wells from
        :param formation_code: list, required (default = None)
                        The list of formation codes that are of interest for the model to grab wells from
        :return:
        """

        # Since this is the first step, use it to read in the data to the OGC data object
        training_data = ReadData()

        training_data.read_csv_folder(self.output_folder)

        self.dataframes_dict = training_data.pd_dict

        # Check the 'Fracture Fluid Data.csv' data for

        file_list = ['zone_prd_2016_to_present.csv', 'zone_prd_2007_to_2015.csv']
        tmp_prod_df = list()

        print("finding well names....")
        for idx, file in enumerate(file_list):
            df1, _ = self.find_in_data_frames_dict(file_name=file, list_of_values=area_code, column='Area_code')

            df2, _ = self.find_in_data_frames_dict(file_name=file, list_of_values=formation_code, column='Formtn_code')

            tmp_prod_df.append(pd.concat([df1, df2]))

        self.wa_num.append(pd.concat(tmp_prod_df)['Wa_num'].to_list())

        total_prod_file = 'BC Total Production.csv'

        df1, _ = self.find_in_data_frames_dict(file_name=total_prod_file, list_of_values=area_code, column='Area Code')

        df2, _ = self.find_in_data_frames_dict(file_name=total_prod_file, list_of_values=formation_code,
                                               column='Formtn Code')

        df3 = pd.concat([df1, df2])

        self.wa_num.append(df3['Well Authorization Number'].to_list())

        print("found well names....")

        self.wa_num = list(chain.from_iterable(self.wa_num))
        # Remove duplicates from the list
        self.wa_num = list(set(self.wa_num))

        self.feature_list = pd.DataFrame(self.wa_num, columns=['Well Authorization Number'])

        
        
    def read_well_data(self, file_name=None):
        """

        Parameters
        ----------
        self

        file_name: dictionary that has the file and headers needed for the data object

        Returns
        -------

        """
        # grab the dictionary entry for the file and filter it for the well authorization number list

        for key in file_name:
            filtered_df, wa_col = self.find_in_data_frames_dict(file_name=key, list_of_values=self.wa_num)

            # remove the columns from the header list in the dictionary
            file_name[key].append(wa_col)

            filtered_df = filtered_df.loc[:, file_name[key]]

            # rename WA Num to Well Authorization Number to match the other data frame with all of the wells
            filtered_df = filtered_df.rename(columns={wa_col: "Well Authorization Number"})

            if key in self.multiple_list:
                self.multiple_wells.append(filtered_df)
                self.multiple_names.append(key)
            else:
                self.feature_list = pd.merge(self.feature_list, filtered_df, how="left",
                                             on=['Well Authorization Number'])
    
    def calc_well_design(self, multiple_loc=-1):

        """
        Function to calculate well design features from feature_list
        Features are then added to feature_list

        """
        #create dataframe on cluster level from fields of interest in feature list

        # dfCluster = self.feature_list['Well Authorization Number',
        #                        'PERF STAGE NUM',
        #                        'INTERVAL TOP DEPTH (m)',
        #                        'INTERVAL BASE DEPTH (m)',
        #                        'Formtn_code',
        #                        'Tvd_formtn_top_depth ',
        #                        'Compltn_top_depth',
        #                        'Compltn_base_depth',]

        #create dataframes on stage and well level
        dfStage = pd.DataFrame()
        dfWell = pd.DataFrame()
        dfCluster = pd.DataFrame()

        #Agg Cluster values to calculate number of clusters in a stage
        dfStage = self.multiple_wells[multiple_loc].groupby(['Well Authorization Number','PERF STAGE NUM']).agg({'INTERVAL TOP DEPTH (m)':'count'})
        dfStage.rename(columns = {'INTERVAL TOP DEPTH (m)':'Cluster Count'}, inplace =True)
        #Agg cluste values to determine max and min depths and total stages
        dfWell = self.multiple_wells[multiple_loc].groupby('Well Authorization Number').agg({'INTERVAL BASE DEPTH (m)':np.max,
                                  'INTERVAL TOP DEPTH (m)':np.min,
                                  'PERF STAGE NUM':'nunique'})
        dfWell.rename(columns = {'INTERVAL BASE DEPTH (m)':'Well Length',
                 'INTERVAL TOP DEPTH (m)': 'Heel Perf Depth',
                  'PERF STAGE NUM': 'Number of Stages'}, inplace = True)
        #Calculate completed length from the max and min clusters
        dfWell['Completed Length'] = dfWell['Well Length']-dfWell['Heel Perf Depth']


        dfCluster['Stage Length'] =  self.feature_list['Compltn_base_depth'] - self.feature_list['Compltn_top_depth']

        #Merge in stage calc to cluster dataframe
        dfCluster = pd.merge(dfCluster, dfStage,
                     on = ['Well Authorization Number','PERF STAGE NUM'],
                     how = 'left')
        #Calc cluster spacing based on stage length and number of clusters
        dfCluster['Cluster Spacing'] = dfCluster['Stage Length']/(dfCluster['Cluster Count']-1)

        #Agg clusters to well level and take in median to avoid outliers and merge to well value
        dfClusterPivot = dfCluster.pivot_table(index = ['Well Authorization Number'],
                           values = ['Stage Length','Cluster Spacing','Cluster Count'],
                           aggfunc = np.median)
        dfWell = pd.merge(dfWell, dfClusterPivot, on = 'Well Authorization Number')

        #Find wells as single point entry and adjust cluser spacing to be stage spacing
        dfWell.loc[(dfWell['Cluster Count'] < 2), 'Cluster Spacing'] = dfWell['Completed Length']/dfWell['Number of Stages']

        #Drop heel perf depth
        dfWell = dfWell.drop(['Heel Perf Depth'])
        #Merge well dataframe to feature list
        self.feature_list = pd.merge(self.feature_list, dfWell,
                             on = 'Well Authorization Number',
                             how = 'left')

    def determine_frac_type(self):
        """
        Use the feature list to determine the frac type and add them to the feature_list, then remove values needed
        for this determination from the feature_list

        Returns
        -------

        """

        print("Determining FRAC TYPE")

        self.feature_list.loc[
            self.feature_list['CHARGE TYPE'].isnull() & self.feature_list['CHARGE SIZE (g)'].isnull() &
            self.feature_list['SHOTS PER METER'].isnull() &
            self.feature_list['DEGREE OF PHASING'].isnull(), "FRAC TYPE"] = 'Frac Sleeve'

        self.feature_list.loc[self.feature_list['PERF COMMENTS'] == "AbrasiveJet", "FRAC TYPE"] = 'Frac Sleeve'
        self.feature_list.loc[self.feature_list['PERF COMMENTS'] == "Burst Disc", "FRAC TYPE"] = 'Frac Sleeve'
        self.feature_list.loc[self.feature_list['PERF COMMENTS'] == "Toe Port", "FRAC TYPE"] = 'Frac Sleeve'
        self.feature_list.loc[self.feature_list['PERF COMMENTS'] == "Cemented Sleeve", "FRAC TYPE"] = 'Frac Sleeve'

        self.feature_list.loc[self.feature_list['FRAC TYPE'].isnull(), "FRAC TYPE"] = 'Plug and Perf'

        self.removal_list.append('PERF COMMENTS')

    def calc_frac_props(self):
        """

        Returns
        -------

        """
        print("Determining Proppant Total")
        self.feature_list['Proppant Total'] = self.feature_list['PROPPANT TYPE1 PLACED (t)'] + \
                                self.feature_list['PROPPANT TYPE2 PLACED (t)'] + \
                                self.feature_list['PROPPANT TYPE3 PLACED (t)'] + \
                                self.feature_list['PROPPANT TYPE4 PLACED (t)']

        group = self.feature_list.groupby('Well Authorization Number')

        df2 = pd.DataFrame()

        print("Determining Proppant Total Sum")
        df2['Proppant Total Sum'] = group.apply(lambda x: sum(x['Proppant Total']))

        print("Determining Lateral Length")
        df2['Lateral Length'] = group.apply(
            lambda x: max(x['COMPLTN BASE DEPTH (m)']) - min(x['COMPLTN TOP DEPTH (m)']))

        print("Determining Average Treating Pressure")
        df2['Average Treating Pressure'] = group.apply(lambda x: x['AVG TREATING PRESSURE (MPa)'].mean())

        print("Determining Average Injection Rate")
        df2['Average Injection Rate'] = group.apply(lambda x: x['AVG RATE (m3/min)'].mean())

        print("Determining Frac Gradient (kPa/m)")
        df2['FRAC GRADIENT (KPa/m)'] = group.apply(lambda x: x['FRAC GRADIENT (KPa/m)'].mean())

        print("Determining Tonnage Per Metre")
        df2['Tonnage per m'] = df2['Proppant Total Sum'] / df2['Lateral Length']
        df2['Tonnage per m'] = df2['Tonnage per m'].round(2)

        print("Determining Energzier")

        # TODO: Check what the Energizer should be with multiple Energizer types for different stages, if there is a stage w/o None, use that and move on
        df2['Energizer'] = group.apply(lambda x: x['ENERGIZER'].value_counts().index.tolist()[0] if len(x['ENERGIZER'].value_counts().index.tolist()) > 0 else "None")
        df2['Energizer Type'] = group.apply(lambda x: x['ENERGIZER TYPE'].value_counts().index.tolist()[0] if len(x['ENERGIZER TYPE'].value_counts().index.tolist()) > 0 else "None")

        print("Determining Fluid Pumped (m3)")
        df2['Total Fluid Pumped (m3)'] = group.apply(lambda x: sum(x['TOTAL FLUID PUMPED (m3)']))

        print("Determining Fluid Per Metre")
        df2['Fluid per m'] = df2['Total Fluid Pumped (m3)'] / df2['Lateral Length']
        df2['Fluid per m'] = df2['Fluid per m'].round(2)

        print("Determining Tonnage Per fluid m3")
        df2['Tonnage per m3'] = df2['Proppant Total Sum']/df2['Total Fluid Pumped (m3)']
        df2['Tonnage per m3'] = df2['Fluid per m'].round(2)

        print("Determining CO2 Pumped (m3)")
        df2['Total CO2 Pumped (m3)'] = group.apply(lambda x: sum(x['TOTAL CO2 PUMPED (m3)']))

        print("Determining N2 Pumped (scm)")
        df2['Total N2 Pumped (scm)'] = group.apply(lambda x: sum(x['TOTAL N2 PUMPED (scm)']))

        print("Determining Total CH4 Pumped (e3m3)")
        df2['Total CH4 Pumped (e3m3)'] = group.apply(lambda x: sum(x['TOTAL CH4 PUMPED (e3m3)']))
        df2 = df2.reset_index()

        df2 = df2.drop(['Lateral Length'], axis=1)

        self.feature_list = pd.merge(self.feature_list, df2, how="left", on=['Well Authorization Number'])

        # TODO: create a list of things to remove from the feature_list
        #self.removal_list.append('PERF COMMENTS')

    def fill_feature_list_nan_with_val(self, columns=list(), val=0):
        """
        fill the columns in the list with the value given instead of nan

        Parameters
        ----------
        columns
        val

        Returns
        -------

        """

        for column in columns:
            self.feature_list[column] = self.feature_list[column].fillna(value=0, inplace=True)

    def remove_columns(self):
        """
        Remove extra columns that were added to the feature list for the final stage before training

        Parameters
        ----------
        columns
        val

        Returns
        -------

        """

        for column in self.removal_list:
            self.feature_list = self.feature_list.drop([column], axis=1)


        self.feature_list.to_csv("feature_list.csv")

    def aggregate_multiple_wells(self):

        for idx, df in enumerate(self.multiple_list):
            # aggregate the values in the well list, this has to be different for each of the files though for
            # the averaging technique

            if self.multiple_names[idx] == "perf_net_interval.csv":
                self.calc_well_design(idx)
            else:
                pass

