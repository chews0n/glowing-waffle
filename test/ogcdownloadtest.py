from glowingwaffle.data import scrapeOGC
import sys

OGC_URLS = ['https://reports.bcogc.ca/ogc/app001/r/ams_reports/bc_total_production?request=CSV_Y',
            'https://reports.bcogc.ca/ogc/app001/r/ams_reports/2?request=CSV_N']

if __name__ == "__main__":
    # Download the files from the OGC website
    ogcData = scrapeOGC(folder=sys.argv[1], urls=OGC_URLS)
    ogcData.downloadDataUrl()