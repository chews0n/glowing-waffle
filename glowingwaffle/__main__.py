import argparse
import os
from glowingwaffle.data import ScrapeOGC

OGC_URLS = ['https://reports.bcogc.ca/ogc/app001/r/ams_reports/bc_total_production?request=CSV_Y',
            'https://reports.bcogc.ca/ogc/app001/r/ams_reports/2?request=CSV_N',
            'https://iris.bcogc.ca/download/hydraulic_fracture_csv.zip',
            'https://iris.bcogc.ca/download/drill_csv.zip',
            'https://iris.bcogc.ca/download/prod_csv.zip']

AREA_CODE = [6200, 9022, 9021]

FORMATION_CODE = [4990, 4995, 4997, 5000, 4000]

FILE_DICT = {'wells.csv': ["Surf Nad83 Lat", "Surf Nad83 Long"]}

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_arguments():
    # create parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='A Machine Learning Based Predictor for fracture design optimization '
                                                 'for use with the Montney Formation.')

    # add arguments to the parser
    parser.add_argument("--downloadOGC", type=str2bool, nargs='?', dest='download_ogc',
                        const=True, default=False,
                        help="Download the OGC Data")

    parser.add_argument("--train", type=str2bool, nargs='?', dest='train',
                        const=True, default=False,
                        help="Run Retraining of the model.")

    parser.add_argument("--predict", type=str2bool, nargs='?', dest='predict',
                        const=True, default=True,
                        help="Run the prediction mode. This is done after training if this was set to true.")

    parser.add_argument("--model-folder", type=dir_path, nargs='?', default=os.getcwd(), dest='model_folder',
                        help="Folder to either output the model (if training is set to true) or read the model if "
                             "only running the predictor")

    parser.add_argument("--input-file", type=argparse.FileType('r'), nargs='?', default='input.csv', dest='input_file',
                        help="Input file for the input to the model predictor.")

    # parse the arguments
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    ogc_data = ScrapeOGC(folder=args.model_folder, urls=OGC_URLS)

    # Download the OGC data from the OGC website

    ogc_data.download_data_url(file_names=FILE_DICT, force_download=args.download_ogc)

    if args.train:
        print("Starting to load in the data for training...")

        ogc_data.find_well_names(area_code=AREA_CODE, formation_code=FORMATION_CODE)

        ogc_data.read_well_data(file_name=FILE_DICT)

        print(f"we found {len(ogc_data.wa_num)} wells")

        # TODO: print out the CSV as backup in case you need to load in the data again for training


if __name__ == "__main__":
    main()
