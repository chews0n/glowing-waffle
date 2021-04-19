from glowingwaffle.data import ScrapeOGC
import sys

OGC_URLS = ['https://reports.bcogc.ca/ogc/app001/r/ams_reports/bc_total_production?request=CSV_Y',
            'https://reports.bcogc.ca/ogc/app001/r/ams_reports/2?request=CSV_N']

OGC_PROD_HEADERS = ['Well Authorization Number', 'Completion Event Sequence', 'UWI', 'Zone Prod Period', 'Area Code',
                    'Formtn Code', 'Well Area Name', 'Oper Abbreviation', 'Production Days', 'Gas Production (e3m3)',
                    'Oil Production (m3)', 'Condensate Production (m3)', 'Water Production (m3)',
                    'Marketable Gas Volume (e3m3)', 'Ethane Sales Volume (m3)', 'Propane Sales Volume (m3)',
                    'Butane Sales Volume (m3)', 'Pentane Sales Volume (m3)']

OGC_FRAC_HEADERS = ['Fracture Date', 'WA Number', 'Well Area Name', 'Operator', 'Well Name', 'Latitude', 'Longitude',
                    'UWI', 'Trade Name', 'Supplier', 'Purpose', 'CAS Number', 'Ingredient Comments', 'Ingredient Name',
                    'Ingredient Concentration in HF Fluid % by Mass', 'Ingredient Percentage in Additive by % Mass',
                    'Total Water Volume (m^3)']

if __name__ == "__main__":
    # Download the files from the OGC website
    ogcData = ScrapeOGC(folder=sys.argv[1], urls=OGC_URLS)
    ogcData.downloaddataurl()
