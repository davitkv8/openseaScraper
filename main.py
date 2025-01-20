"""
This is main module, runs OpenSeaScraper processes.

You just need to specify any queries in namings.py module,
and add pass any queries you want to run during initialization OpenSeaScraper([ .....
it will do rest.
"""

from scraper import OpenSeaScraper


def main():
    OpenSeaScraper(["TOP_RANKINGS", "TRENDING_RANKINGS"]).get_data()


if __name__ == "__main__":
    main()
