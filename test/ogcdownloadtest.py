from glowingwaffle.data import ScrapeOGC
import sys
import os

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
                                        'VISCOSITY GEL TYPE', 'ENERGIZER', 'ENERGIZER TYPE',
                                        'AVG TREATING PRESSURE (MPa)', 'FRAC GRADIENT (KPa/m)','TOTAL FLUID PUMPED (m3)'
                                        ,'TOTAL CO2 PUMPED (m3)', 'TOTAL N2 PUMPED (scm)','TOTAL CH4 PUMPED (e3m3)',
                                        'PROPPANT TYPE1','PROPPANT TYPE1 PLACED (t)','PROPPANT TYPE2',
                                        'PROPPANT TYPE2 PLACED (t)', 'PROPPANT TYPE3','PROPPANT TYPE3 PLACED (t)',
                                        'PROPPANT TYPE4','PROPPANT TYPE4 PLACED (t)']}

if __name__ == "__main__":
    # Download the files from the OGC website
    output_folder = None
    try:
        output_folder = sys.argv[1]
    except:
        output_folder = os.getcwd()

    ogcData = ScrapeOGC(folder=output_folder, urls=OGC_URLS)

    ogcData.download_data_url(file_names=FILE_DICT)

    ogcData.find_well_names(area_code=AREA_CODE, formation_code=FORMATION_CODE)

    ogcData.read_well_data(file_name=FILE_DICT)

    ogcData.determine_frac_type()

    ogcData.fill_feature_list_nan_with_val(columns=['PROPPANT TYPE1 PLACED (t)', 'PROPPANT TYPE2 PLACED (t)',
                                                    'PROPPANT TYPE3 PLACED (t)', 'PROPPANT TYPE4 PLACED (t)'], val=0)

    ogcData.calc_frac_props()

    ogcData.fill_feature_list_nan_with_val(columns=['Total CO2 Pumped (m3)', 'Total N2 Pumped (scm)',
                                                    'Total CH4 Pumped (e3m3)'], val=0)

    ogcData.remove_columns()

    print(f"we found {len(ogcData.wa_num)} well names")
