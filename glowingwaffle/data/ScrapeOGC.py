import requests
from requests.exceptions import HTTPError
import re
import sys
import os


# TODO: Extend this also to the AER, maybe??

class ScrapeOGC:

    def __init__(self, folder=None, urls=None):
        self.urls = list()
        self.filenames = list()
        self.outputfolder = folder

        self.urls = urls

        if folder is not None and not os.path.exists(folder):
            # create a folder if the folder does not currently exist
            try:
                os.mkdir(folder)
            except OSError as err:
                sys.exit(f'Error Occured creating directory: {err}')

    def downloaddataurl(self):
        '''
        Download the CSV data from the URLS given in the list of URLS, while we are currently using this for
        the data from the Oil and Gas Council of BC, this can be extended to any file that has a URL, including
        none CSV data. If no folder supplied, the file will be downloaded to the Current Working Directory

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
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
                outputfilename = re.search(r"filename=\"([^']*)\";", response.headers['Content-Disposition']).group(1)

                if self.outputfolder is not None:
                    # gives the full path of the file for writing and saving
                    outputfilename = os.path.join(self.outputfolder, outputfilename)

                try:
                    f = open(outputfilename, 'wb')
                    # check if we were able to open the file
                except OSError:
                    sys.exit(f"Could not open the file: {outputfilename}")
                with f:
                    # write the content of the get request to the file that was opened
                    f.write(response.content)

                # save the filename to the list of the OGCData option
                self.filenames.append(outputfilename)

        print("Finished Downloading the files from OGC")
