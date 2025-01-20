"""Module containing Graphql queries/mutations and describes all the essential details."""
from enum import Enum
from typing import TypedDict, Literal

# Available queries, add any queries here first before adding it in QUERY_DETAILS_MAP
AvailableQueries = list[Literal["TOP_RANKINGS", "TRENDING_RANKINGS"]]


class QueryDetails[TypedDict]:
    """Required details about the query that user should provide before adding it."""

    accessor_page_url: str  # Page url which communicates with specific graphql API
    body: dict  # Request body (Usually it's just dict containing Graphql query/mutation details)
    response_key: str  # Response key, a top level key returned by Graphql API as a response
    query_name: str  # Just Graphql query/mutation name


# Add available query details, so system will automatically handle it all.
QUERY_DETAILS_MAP = {
    # Graphql query for top items - maximum 100 result, all time
    "TOP_RANKINGS": {
        "accessor_page_url": "https://opensea.io/rankings",
        "body": {
            "id": "RankingsPageTopQuery",
            "query": "query RankingsPageTopQuery(\n  $chain: [ChainScalar!]\n  $count: Int!\n  $cursor: String\n  $topCollectionsSortBy: TrendingCollectionSort\n  $categories: [CategoryV2Slug!]!\n  $timeWindow: StatsTimeWindow\n  $floorPricePercentChange: Boolean!\n) {\n  ...RankingsPageTop_data\n}\n\nfragment RankingsPageTop_data on Query {\n  topCollectionsByCategory(after: $cursor, chains: $chain, first: $count, sortBy: $topCollectionsSortBy, categories: $categories) {\n    edges {\n      node {\n        createdDate\n        name\n        slug\n        logo\n        isVerified\n        relayId\n        ...StatsCollectionCell_collection\n        ...collection_url\n        statsV2 {\n          totalQuantity\n        }\n        windowCollectionStats(statsTimeWindow: $timeWindow) {\n          floorPrice {\n            unit\n            eth\n            symbol\n          }\n          numOwners\n          totalSupply\n          totalListed\n          numOfSales\n          volumeChange\n          volume {\n            eth\n            unit\n            symbol\n          }\n        }\n        floorPricePercentChange(statsTimeWindow: $timeWindow) @include(if: $floorPricePercentChange)\n        id\n        __typename\n      }\n      cursor\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n    }\n  }\n}\n\nfragment StatsCollectionCell_collection on CollectionType {\n  name\n  logo\n  isVerified\n  slug\n}\n\nfragment collection_url on CollectionType {\n  slug\n  isCategory\n}\n",
            "variables": {
              "chain": None,
              "count": 100,
              "cursor": None,
              "topCollectionsSortBy": "TOTAL_VOLUME",
              "categories": [],
              "timeWindow": "ALL_TIME",
              "floorPricePercentChange": False,
            },
        },
        "response_key": "topCollectionsByCategory",
        "query_name": "RankingsPageTopQuery",
    },

    # Graphql query for trending items - maximum 500 result, 7 days
    "TRENDING_RANKINGS": {
        "accessor_page_url": "https://opensea.io/rankings/trending",
        "body": {
            "id": "RankingsPageTrendingQuery",
            "query": "query RankingsPageTrendingQuery(\n  $chain: [ChainScalar!]\n  $count: Int!\n  $cursor: String\n  $categories: [CategoryV2Slug!]!\n  $eligibleCount: Int!\n  $trendingCollectionsSortBy: TrendingCollectionSort\n  $timeWindow: StatsTimeWindow\n  $floorPricePercentChange: Boolean!\n) {\n  ...RankingsPageTrending_data\n}\n\nfragment RankingsPageTrending_data on Query {\n  trendingCollectionsByCategory(after: $cursor, chains: $chain, first: $count, sortBy: $trendingCollectionsSortBy, categories: $categories, topCollectionLimit: $eligibleCount) {\n    edges {\n      node {\n        createdDate\n        name\n        slug\n        logo\n        isVerified\n        relayId\n        ...StatsCollectionCell_collection\n        ...collection_url\n        statsV2 {\n          totalQuantity\n        }\n        windowCollectionStats(statsTimeWindow: $timeWindow) {\n          floorPrice {\n            unit\n            eth\n            symbol\n          }\n          numOwners\n          totalSupply\n          totalListed\n          numOfSales\n          volumeChange\n          volume {\n            unit\n            eth\n            symbol\n          }\n        }\n        floorPricePercentChange(statsTimeWindow: $timeWindow) @include(if: $floorPricePercentChange)\n        id\n        __typename\n      }\n      cursor\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n    }\n  }\n}\n\nfragment StatsCollectionCell_collection on CollectionType {\n  name\n  logo\n  isVerified\n  slug\n}\n\nfragment collection_url on CollectionType {\n  slug\n  isCategory\n}\n",
            "variables": {
              "chain": None,
              "count": 500,
              "cursor": None,
              "categories": [],
              "eligibleCount": 500,
              "trendingCollectionsSortBy": "TOTAL_VOLUME",
              "timeWindow": "SEVEN_DAY",
              "floorPricePercentChange": True,
            },
        },
        "response_key": "trendingCollectionsByCategory",
        "query_name": "RankingsPageTrendingQuery",
    },
}
