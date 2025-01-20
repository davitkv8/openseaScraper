from scraper import OpenSeaScraper


def main():
    OpenSeaScraper(["TOP_RANKINGS"]).get_data()


if __name__ == "__main__":
    main()
