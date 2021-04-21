import argparse
import os


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
    parser.add_argument("--train", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Run Retraining of the model.")

    parser.add_argument("--predict", type=str2bool, nargs='?',
                        const=True, default=True,
                        help="Run the prediction mode. This is done after training if this was set to true.")

    parser.add_argument("--model-folder", type=dir_path, nargs='?', default=os.getcwd(),
                        help="Folder to either output the model (if training is set to true) or read the model if "
                             "only running the predictor")

    parser.add_argument("--input-file", type=argparse.FileType('r'), nargs='?', default='input.csv',
                        help="Input file for the input to the model predictor.")

    # parse the arguments
    args = parser.parse_args()


def main():
    parse_arguments()


if __name__ == "__main__":
    main()
