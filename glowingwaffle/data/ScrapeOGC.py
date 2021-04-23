import requests
from requests.exceptions import HTTPError
import regex
import sys
import os
import zipfile36 as zipfile
from glowingwaffle.data import ReadData
import pandas as pd
from itertools import chain


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

        if folder is not None and not os.path.exists(folder):
            # create a folder if the folder does not currently exist
            try:
                os.mkdir(folder)
            except OSError as err:
                sys.exit(f'Error Occurred creating directory: {err}')

    def download_data_url(self):
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

    def find_in_data_frames_dict(self, file_name=None, list_of_values=None, column=None):
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
        df = self.dataframes_dict[file_name].loc[self.dataframes_dict[file_name][column].isin(list_of_values)]

        return df

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
            df1 = self.find_in_data_frames_dict(file_name=file, list_of_values=area_code, column='Area_code')

            df2 = self.find_in_data_frames_dict(file_name=file, list_of_values=formation_code, column='Formtn_code')

            tmp_prod_df.append(pd.concat([df1, df2]))

        self.wa_num.append(pd.concat(tmp_prod_df)['Wa_num'].to_list())

        total_prod_file = 'BC Total Production.csv'

        df1 = self.find_in_data_frames_dict(file_name=total_prod_file, list_of_values=area_code, column='Area Code')

        df2 = self.find_in_data_frames_dict(file_name=total_prod_file, list_of_values=formation_code,
                                            column='Formtn Code')

        df3 = pd.concat([df1, df2])

        self.wa_num.append(df3['Well Authorization Number'].to_list())

        print("found well names....")

        self.wa_num = list(chain.from_iterable(self.wa_num))
        # Remove duplicates from the list
        self.wa_num = list(set(self.wa_num))

        self.feature_list = pd.DataFrame(self.wa_num, columns=['Well Authorization Number'])

    def read_well_lat_long(self):
        """

        Parameters
        ----------
        self

        Returns
        -------

        """
        # grab the dictionary entry for the 'wells.csv' file and filter it for the well authorization number list
        filtered_df = self.find_in_data_frames_dict(file_name='wells.csv', list_of_values=self.wa_num, column='WA Num')

        # remove the columns "Surf Nad83 Lat","Surf Nad83 Long" from the wells.csv data and put it into the feature
        # list
        filtered_df = filtered_df.loc[:, ["Surf Nad83 Lat", "Surf Nad83 Long", "WA Num"]]

        # rename WA Num to Well Authorization Number to match the other data frame with all of the wells
        filtered_df = filtered_df.rename(columns={"Surf Nad83 Lat": "SURFACE_LAT", "Surf Nad83 Long": "SURFACE_LONG",
                                                  "WA Num": "Well Authorization Number"})

        self.feature_list = pd.merge(self.feature_list, filtered_df, how="left", on=['Well Authorization Number'])
