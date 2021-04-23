from glowingwaffle.data import ScrapeOGC
import sys

OGC_URLS = ['https://reports.bcogc.ca/ogc/app001/r/ams_reports/bc_total_production?request=CSV_Y',
            'https://reports.bcogc.ca/ogc/app001/r/ams_reports/2?request=CSV_N',
            'https://iris.bcogc.ca/download/hydraulic_fracture_csv.zip',
            'https://iris.bcogc.ca/download/drill_csv.zip',
            'https://iris.bcogc.ca/download/prod_csv.zip']

OGC_PROD_HEADERS = ['Well Authorization Number', 'Completion Event Sequence', 'UWI', 'Zone Prod Period', 'Area Code',
                    'Formtn Code', 'Well Area Name', 'Oper Abbreviation', 'Production Days', 'Gas Production (e3m3)',
                    'Oil Production (m3)', 'Condensate Production (m3)', 'Water Production (m3)',
                    'Marketable Gas Volume (e3m3)', 'Ethane Sales Volume (m3)', 'Propane Sales Volume (m3)',
                    'Butane Sales Volume (m3)', 'Pentane Sales Volume (m3)']

OGC_FRAC_HEADERS = ['Fracture Date', 'WA Number', 'Well Area Name', 'Operator', 'Well Name', 'Latitude', 'Longitude',
                    'UWI', 'Trade Name', 'Supplier', 'Purpose', 'CAS Number', 'Ingredient Comments', 'Ingredient Name',
                    'Ingredient Concentration in HF Fluid % by Mass', 'Ingredient Percentage in Additive by % Mass',
                    'Total Water Volume (m^3)']

# In the perf_csv -- https://iris.bcogc.ca/download/hydraulic_fracture_csv.zip
OGC_PERF_HEADERS = ['WA NUM', 'DRILLNG EVENT', 'COMPLTN EVENT', 'UWI', 'WELL NAME', 'COMPLTN DATE',
                    'COMPLTN TOP DEPTH (m)', 'COMPLTN BASE DEPTH (m)', 'COMPLTN TYPE', 'COMPLETION WORKOVER KEY',
                    'FRAC SUMMARY KEY', 'PERF STAGE NUM', 'CHARGE TYPE', 'CHARGE SIZE (g)', 'SHOTS PER METER',
                    'DEGREE OF PHASING', 'PERF COMMENTS']

# In the hydraulic_fracture_csv -- https://iris.bcogc.ca/download/hydraulic_fracture_csv.zip
OGC_HYDRAULIC_FRACTURE_HEADERS = ['WA NUM', 'DRILLNG EVENT', 'COMPLTN EVENT', 'UWI', 'WELL NAME', 'COMPLTN DATE',
                                  'FRAC START TIME', 'COMPLTN TOP DEPTH (m)', 'COMPLTN BASE DEPTH (m)', 'COMPLTN TYPE',
                                  'COMPLETION WORKOVER KEY', 'FRAC SUMMARY KEY', 'FRAC STAGE NUM', 'BASE FLUID',
                                  'VISCOSITY GEL TYPE', 'ENERGIZER', 'ENERGIZER TYPE', 'PLUG BACK TOTAL DEPTH (m)',
                                  'ACID SPEARHEAD AMOUNT (m3)', 'ACID TYPE', 'BREAK DOWN PRESSURE (MPa)',
                                  'INST SHUT IN PRESSURE (MPa)', 'MAX TREATING PRESSURE (MPa)',
                                  'AVG TREATING PRESSURE (MPa)', 'AVG RATE (m3/min)', 'FRAC GRADIENT (KPa/m)',
                                  'TOTAL FLUID PUMPED (m3)', 'TOTAL CO2 PUMPED (m3)', 'TOTAL N2 PUMPED (scm)',
                                  'TOTAL CH4 PUMPED (e3m3)', 'RADIOACTIVE FLAG', 'RADIOACTIVE TRACER TYPE',
                                  'CHEMICAL TRACER FLAG', 'CHEMICAL TRACER TYPE', 'PROPPANT TYPE1',
                                  'PROPPANT TYPE1 PUMPED (t)', 'PROPPANT TYPE1 PLACED (t)', 'PROPPANT TYPE2',
                                  'PROPPANT TYPE2 PUMPED (t)', 'PROPPANT TYPE2 PLACED (t)', 'PROPPANT TYPE3',
                                  'PROPPANT TYPE3 PUMPED (t)', 'PROPPANT TYPE3 PLACED (t)', 'PROPPANT TYPE4',
                                  'PROPPANT TYPE4 PUMPED (t)', 'PROPPANT TYPE4 PLACED (t)']

# In the perf_net_interval.csv -- https://iris.bcogc.ca/download/hydraulic_fracture_csv.zip
OGC_PERF_NET_HEADERS = ['WA NUM', 'DRILLNG EVENT', 'COMPLTN EVENT', 'UWI', 'WELL NAME', 'COMPLTN DATE',
                        'COMPLTN TOP DEPTH (m)', 'COMPLTN BASE DEPTH (m)', 'COMPLTN TYPE', 'COMPLETION WORKOVER KEY',
                        'FRAC SUMMARY KEY', 'PERF STAGE NUM', 'INTERVAL TOP DEPTH (m)', 'INTERVAL BASE DEPTH (m)']

# In the wells file -- https://iris.bcogc.ca/download/drill_csv.zip
OGC_WELLS_HEADERS = ['Well Surf Loc', 'Well Name', 'WA Num', 'Surf Nad27 Lat', 'Surf Nad27 Long', 'Surf Nad83 Lat',
                     'Surf Nad83 Long', 'Surf UTM Zone Num', 'Surf UTM83 Northng', 'Surf UTM83 Eastng', 'Surf North',
                     'Surf East', 'Surf Owner', 'Ground Elevtn', 'Directional Flag', 'Surf Ref Corner', 'Surf Ref Unit',
                     'Surf Ref Block', 'Surf Ref Map', 'Surf Ref Lsd', 'Surf Ref Sect', 'Surf Ref Twp',
                     'Surf Ref Range', 'Surf DLS Exception', 'Surf Lsd', 'Surf Sect', 'Surf Twp', 'Surf Range',
                     'Surf Qtr Unit', 'Surf NTS Exception', 'Surf Unit', 'Surf Block', 'Surf Map', 'Oper Id',
                     'Oper Abbrev', 'Oper Abbrev2', 'Optnl Unit', 'Well Area Name', 'Well Name Date',
                     'Special Well Class Code', 'Test Hole']

# In the dst file -- https://iris.bcogc.ca/download/drill_csv.zip
OGC_DST_HEADERS = ['UWI', 'Area_code', 'Formtn_code', 'Pool_seq', 'Wa_num', 'Drillng_event_seq', 'Top_intrvl_depth (m)',
                   'Dst_num', 'Dst_Type', 'Base_intrvl_depth (m)', 'Init_hydro_press', 'Init_shutin_press',
                   'Init_shutin_time', 'Main_flow_init_press', 'Preflw_time', 'Preflw_start_press', 'Preflw_end_press',
                   'Preflw_gas_to_surf', 'Final_hydro_press', 'Final_shutin_press', 'Final_shutin_time',
                   'Main_flow_final_press', 'Main_valve_open_time', 'Main_flow_gas_to_surf', 'Dst_remarks',
                   'Init_extrpltd_press', 'Final_extrpltd_press', 'Misrun_flag', 'Skin', 'Permblty', 'Run_temp (c)',
                   'Detail_anlyss_flag', 'Flow_recvry_remarks', 'Dst_date', 'Project_code']
AREA_CODE = [6200, 9022, 9021]

FORMATION_CODE = [4990, 4995, 4997, 5000, 4000]


if __name__ == "__main__":
    # Download the files from the OGC website
    ogcData = ScrapeOGC(folder=sys.argv[1], urls=OGC_URLS)
    ogcData.download_data_url()
    ogcData.find_well_names(area_code=AREA_CODE, formation_code=FORMATION_CODE)

    ogcData.read_well_lat_long()

    print(f"we found {len(ogcData.wa_num)} well names")
