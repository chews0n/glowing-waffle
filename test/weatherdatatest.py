from glowingwaffle.data import ReadData
import sys

if __name__ == "__main__":
    # instantiate the training data object from readData
    trainingData = ReadData()

    # Pass one argument into the program which is the rel or absolute path to the csv files
    trainingData.readcsvfolder(sys.argv[1])

    # clean the data and drop the columns we don't need
    trainingData.cleandata(columns_to_drop=['Longitude (x)', 'Latitude (y)', 'Climate ID',
                                            'Station Name', 'Data Quality', 'Max Temp Flag',
                                            'Min Temp Flag', 'Mean Temp Flag', 'Heat Deg Days Flag',
                                            'Cool Deg Days Flag', 'Total Rain Flag', 'Total Snow Flag',
                                            'Total Precip Flag', 'Snow on Grnd Flag', 'Dir of Max Gust Flag',
                                            'Spd of Max Gust Flag', 'Total Rain (mm)', 'Total Snow (cm)',
                                            'Heat Deg Days (°C)', 'Cool Deg Days (°C)'])

    # Split the features and the output data frames
    trainingData.splitfeaturesandoutputs(output_list=['Max Temp (°C)'])
