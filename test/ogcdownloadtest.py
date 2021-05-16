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
             'dst.csv':["Dst_num", "Top_intrvl_depth (m)", "Base_intrvl_depth (m)", "Init_shutin_press", "Final_shutin_press", "Misrun_flag", "Skin", "Permblty", "Run_temp (c)"],
             'pst_dtl.csv': ["Run_depth_temp (C)", "Run_depth_press (kPa)", "Datum_press (kPa)", "Run_depth (m)"],
             'pay_zone.csv': ["Oil porsty", "Gas porsty", "Oil water satrtn", "Gas water satrtn", "Tvd oil net pay size", "Tvd gas net pay size"],
             'dst_rate.csv': ["Dst_num", "Flowing_fluid_type", "Init_fluid_rate", "Avg_fluid_rate", "Final_fluid_rate"],
             }

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
    
    df = ogcData.feature_list
    
    df.to_csv("feature_list.csv")

    print(f"we found {len(ogcData.wa_num)} well names")
