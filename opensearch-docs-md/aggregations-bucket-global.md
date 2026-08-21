---
title: Global aggregation
source_url: https://docs.opensearch.org/latest/aggregations/bucket/global/
---

# Global aggregation

Source: https://docs.opensearch.org/latest/aggregations/bucket/global/

[Documentation](/latest/)

# Global aggregation

The `global` aggregation creates a single bucket containing all documents in the index, regardless of the search query. Subaggregations nested inside `global` operate on the full document set, allowing you to compare filtered metrics against overall metrics in the same request.

The `global` aggregation can only be placed as a top-level aggregation. Nesting it inside another bucket aggregation has no effect.

## Example

The following example computes two averages in a single request: one scoped to the query (orders under $50) and one across all documents using the `global` aggregation:

```
GET /opensearch_dashboards_sample_data_ecommerce/_search
{
  "size": 0,
  "query": {
    "range": {
      "taxful_total_price": {
        "lte": 50
      }
    }
  },
  "aggs": {
    "total_avg_amount": {
      "global": {},
      "aggs": {
        "avg_price": {
          "avg": {
            "field": "taxful_total_price"
          }
        }
      }
    },
    "filtered_avg": {
      "avg": {
        "field": "taxful_total_price"
      }
    }
  }
}
```

copy

## Example response

```
{
  "took": 19,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 1633,
      "relation": "eq"
    },
    "max_score": null,
    "hits": []
  },
  "aggregations": {
    "total_avg_amount": {
      "doc_count": 4675,
      "avg_price": {
        "value": 75.05542864304813
      }
    },
    "filtered_avg": {
      "value": 38.363175998928355
    }
  }
}
```

The `total_avg_amount` aggregation reports the average across all 4,675 documents ($75.06), while `filtered_avg` reports the average only for the 1,633 documents matching the query ($38.36).

## Response body fields

The following table lists the response body fields.

| Field | Data type | Description |
| --- | --- | --- |
| `doc_count` | Integer | The total number of documents in the index, independent of the search query. |

* [Example](#example)
* [Example response](#example-response)
* [Response body fields](#response-body-fields)

WAS THIS PAGE HELPFUL?

✔ Yes  ✖ No

Tell us why

350 characters left

Thank you for your feedback!

Have a question? [Ask us on the OpenSearch forum](https://forum.opensearch.org/).

Want to contribute? [Edit this page](https://github.com/opensearch-project/documentation-website/edit/main/_aggregations/bucket/global.md) or [create an issue](https://github.com/opensearch-project/documentation-website/issues/new?assignees=&labels=untriaged&template=issue_template.md&title=%5BDOC%5D).
