from glowingwaffle.data import ScrapeOGC
from glowingwaffle.training import RandomForestModel
import sys
import os
import pandas as pd
import scipy.stats
import numpy as np

OGC_URLS = ['https://reports.bcogc.ca/ogc/app001/r/ams_reports/bc_total_production?request=CSV_Y',
            'https://reports.bcogc.ca/ogc/app001/r/ams_reports/2?request=CSV_N',
            'https://iris.bcogc.ca/download/hydraulic_fracture_csv.zip',
            'https://iris.bcogc.ca/download/drill_csv.zip',
            'https://iris.bcogc.ca/download/prod_csv.zip']

AREA_CODE = [6200, 9022, 9021]

FORMATION_CODE = [4990, 4995, 4997, 5000, 4000]

FILE_DICT = {'wells.csv': ["Surf Nad83 Lat", "Surf Nad83 Long"],
             "perf.csv": ['PERF STAGE NUM', 'CHARGE TYPE', 'CHARGE SIZE (g)', 'SHOTS PER METER', 'DEGREE OF PHASING',
                          'PERF COMMENTS'],
             'hydraulic_fracture.csv': ['COMPLTN TOP DEPTH (m)', 'COMPLTN BASE DEPTH (m)', 'FRAC STAGE NUM',
                                        'VISCOSITY GEL TYPE', 'ENERGIZER', 'ENERGIZER TYPE', 'AVG RATE (m3/min)',
                                        'AVG TREATING PRESSURE (MPa)', 'FRAC GRADIENT (KPa/m)','TOTAL FLUID PUMPED (m3)'
                                        ,'TOTAL CO2 PUMPED (m3)', 'TOTAL N2 PUMPED (scm)','TOTAL CH4 PUMPED (e3m3)',
                                        'PROPPANT TYPE1','PROPPANT TYPE1 PLACED (t)','PROPPANT TYPE2',
                                        'PROPPANT TYPE2 PLACED (t)', 'PROPPANT TYPE3','PROPPANT TYPE3 PLACED (t)',
                                        'PROPPANT TYPE4','PROPPANT TYPE4 PLACED (t)'],
             'compl_ev.csv':["Compltn_top_depth", "Compltn_base_depth", "Formtn_code"], # multiple WA
             'form_top.csv':["Formtn_code", "Tvd_formtn_top_depth "], # multiple WA
             'perf_net_interval.csv':["PERF STAGE NUM", "INTERVAL TOP DEPTH (m)", "INTERVAL BASE DEPTH (m)"], #multiple WA
             'dst.csv': ["Dst_num", "Top_intrvl_depth (m)", "Base_intrvl_depth (m)", "Init_shutin_press",
                         "Final_shutin_press", "Misrun_flag", "Skin", "Permblty", "Run_temp (c)"], # multiple WA, filter out misruns
             'pst_dtl.csv': ["Run_depth_temp (C)", "Run_depth_press (kPa)", "Datum_press (kPa)", "Run_depth (m)"], # might be multiple
             'pay_zone.csv': ["Oil porsty", "Gas porsty", "Oil water satrtn", "Gas water satrtn",
                              "Tvd oil net pay size", "Tvd gas net pay size"],
             'dst_rate.csv': ["Dst_num", "Flowing_fluid_type", "Init_fluid_rate", "Avg_fluid_rate", "Final_fluid_rate"],#multiple WA
             'zone_prd_2007_to_2015.csv': ["Prod_period", "Oil_prod_vol (m3)", "Gas_prod_vol (e3m3)", "Cond_prod_vol (m3)"],#multiple WA
             'zone_prd_2016_to_present.csv': ["Prod_period", "Oil_prod_vol (m3)", "Gas_prod_vol (e3m3)", "Cond_prod_vol (m3)"],#multiple WA
             'BC Total Production.csv': ["Zone Prod Period", "Oil Production (m3)", "Gas Production (e3m3)", "Condensate Production (m3)"]}#multiple WA

INPUT_HEADERS = ['Well Authorization Number',
                'Surf Nad83 Lat',
                'Surf Nad83 Long',
                'CHARGE TYPE',
                'VISCOSITY GEL TYPE',
                'ENERGIZER',
                'ENERGIZER TYPE',
                'PROPPANT TYPE1',
                'PROPPANT TYPE2',
                'PROPPANT TYPE3',
                'PROPPANT TYPE4',
                'FRAC TYPE',
                'Energizer',
                'Energizer Type',
                'COMPLTN TOP DEPTH (m)',
                'COMPLTN BASE DEPTH (m)',
                'FRAC STAGE NUM',
                'IP90',
                'IP180',
                'Total Fluid Pumped (m3)',
                'CHARGE SIZE (g)',
                'SHOTS PER METER',
                'DEGREE OF PHASING',
                'AVG RATE (m3/min)',
                'AVG TREATING PRESSURE (MPa)',
                'FRAC GRADIENT (KPa/m)_x',
                'Oil porsty',
                'Gas porsty',
                'Oil water satrtn',
                'Gas water satrtn',
                'Tvd oil net pay size',
                'Tvd gas net pay size',
                'Average Treating Pressure',
                'Average Injection Rate',
                'FRAC GRADIENT (KPa/m)_y',
                'Fluid per m',
                'Tonnage per m3']

STRING_INPUTS = ['CHARGE TYPE',
                'VISCOSITY GEL TYPE',
                'ENERGIZER',
                'ENERGIZER TYPE',
                'PROPPANT TYPE1',
                'PROPPANT TYPE2',
                'PROPPANT TYPE3',
                'PROPPANT TYPE4',
                'FRAC TYPE',
                'Energizer',
                'Energizer Type']

def mean_confidence_interval(data, confidence=0.95):
    # https://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h

if __name__ == "__main__":
    # Download the files from the OGC website
    output_folder = None
    try:
        output_folder = sys.argv[1]
    except:
        output_folder = os.getcwd()

    try:
        featurelistcsv = sys.argv[2]
    except:
        featurelistcsv = None

    ogcData = ScrapeOGC(folder=output_folder, urls=OGC_URLS)

    if (featurelistcsv is not None and os.path.isfile(featurelistcsv)):
        ogcData.feature_list = pd.read_csv(featurelistcsv)
        ogcData.feature_list = ogcData.feature_list.iloc[:, 1:]

    else:

        ogcData.download_data_url(file_names=FILE_DICT)

        ogcData.find_well_names(area_code=AREA_CODE, formation_code=FORMATION_CODE)

        ogcData.read_well_data(file_name=FILE_DICT)

        ogcData.calc_ip90_ip180()

        #ogcData.calc_well_design()

        ogcData.determine_frac_type()

        ogcData.fill_feature_list_nan_with_val(columns=['PROPPANT TYPE1 PLACED (t)', 'PROPPANT TYPE2 PLACED (t)',
                                                        'PROPPANT TYPE3 PLACED (t)', 'PROPPANT TYPE4 PLACED (t)'],
                                               val=0)
        ogcData.calc_frac_props()

        ogcData.fill_feature_list_nan_with_val(columns=['Total CO2 Pumped (m3)', 'Total N2 Pumped (scm)',
                                                        'Total CH4 Pumped (e3m3)'], val=0)

        ogcData.remove_wells()

        ogcData.create_cleaned_feature_list()

        #ogcData.remove_columns()

        ogcData.print_feature_list_to_csv()

    ogcData.convert_string_inputs_to_none(STRING_INPUTS)

    ogcData.fill_feature_list_nan_with_val(columns=INPUT_HEADERS, val=0)

    ensemble_pred = list()

    for ens_iter in range(0, 10):

        ogcModel = RandomForestModel(df=ogcData.feature_list)

        ogcModel.split_data()

        ogcModel.train_model()

        ogcModel.y_predip90, ogcModel.y_predip180 = ogcModel.predict_initial_production(ogcModel.x_testip90, ogcModel.x_testip180)

        ogcModel.feature_importance(ens_iter)

        # use the input value(s) to predict the outputs
        if len(sys.argv) > 3:
            if (os.path.isfile(sys.argv[3])):
                inputcsv = pd.read_csv(sys.argv[3])
                inputcsv = inputcsv.drop(['Well Authorization Number'], axis=1)
                wellnames = inputcsv.filter(['Well Authorization Number'], axis=1)
                predicted_vals = [0.0, 0.0]
                predicted_vals[0], predicted_vals[1] = ogcModel.predict_initial_production(inputcsv, inputcsv)

                print("predicted IP90 iter#{}: {} \n".format(ens_iter, predicted_vals[0]))

                print("predicted IP180 iter#{}: {} \n".format(ens_iter, predicted_vals[1]))

                ensemble_pred.append(predicted_vals)


