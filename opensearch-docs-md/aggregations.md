---
title: Aggregations
source_url: https://docs.opensearch.org/latest/aggregations/
---

# Aggregations

Source: https://docs.opensearch.org/latest/aggregations/

[Documentation](/latest/)

# Aggregations

OpenSearch is for more than search. Aggregations let you tap into OpenSearch’s powerful analytics engine to analyze your data and extract statistics from it.

The use cases of aggregations vary from analyzing data in real time to take some action to using OpenSearch Dashboards to create a visualization dashboard.

OpenSearch can perform aggregations on massive datasets in milliseconds. Compared to queries, aggregations consume more CPU cycles and memory.

## General aggregation structure

The structure of an aggregation query is as follows:

```
GET _search
{
  "size": 0,
  "aggs": {
    "<aggregation_name>": {
      "<aggregation_type>": {}
    }
  }
}
```

copy

If you’re only interested in the aggregation result and not in the results of the query, set `size` to `0`.

In the `aggs` property (you can use `aggregations` if you want), you can define any number of aggregations. Each aggregation is defined by its name and one of the types of aggregations that OpenSearch supports.

The name of the aggregation helps you to distinguish between different aggregations in the response. The `<aggregation_type>` placeholder specifies the aggregation type, such as `sum` or `min`.

## Example aggregation

The following example uses the OpenSearch Dashboards sample e-commerce data. To add the sample data, log in to OpenSearch Dashboards, choose **Home**, and then choose **Try our sample data**. For **Sample eCommerce orders**, choose **Add data**.

This example uses the `avg` aggregation to find the average value of the `taxful_total_price` field:

```
GET opensearch_dashboards_sample_data_ecommerce/_search
{
  "size": 0,
  "aggs": {
    "avg_taxful_total_price": {
      "avg": {
        "field": "taxful_total_price"
      }
    }
  }
}
```

copy

The response includes an `aggregations` block containing the calculated average value:

```
{
  "took" : 1,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 4675,
      "relation" : "eq"
    },
    "max_score" : null,
    "hits" : [ ]
  },
  "aggregations" : {
    "avg_taxful_total_price" : {
      "value" : 75.05542864304813
    }
  }
}
```

## Aggregation types

There are three main aggregation types:

* [Metric aggregations](#metric-aggregations) – Calculate metrics such as `sum`, `min`, `max`, and `avg` on numeric fields.
* [Bucket aggregations](#bucket-aggregations) – Sort query results into groups based on some criteria.
* [Pipeline aggregations](#pipeline-aggregations) – Pipe the output of one aggregation as an input to another.

### Metric aggregations

Metric aggregations calculate statistics on numeric field values:

* [`avg`](https://docs.opensearch.org/latest/aggregations/metric/average/) – Calculate average values.
* [`cardinality`](https://docs.opensearch.org/latest/aggregations/metric/cardinality/) – Count unique values.
* [`extended_stats`](https://docs.opensearch.org/latest/aggregations/metric/extended-stats/) – Get comprehensive statistics including standard deviation.
* [`max`](https://docs.opensearch.org/latest/aggregations/metric/maximum/) – Find maximum values.
* [`min`](https://docs.opensearch.org/latest/aggregations/metric/minimum/) – Find minimum values.
* [`percentile`](https://docs.opensearch.org/latest/aggregations/metric/percentile/) – Calculate percentiles (for example, median, 95th percentile).
* [`stats`](https://docs.opensearch.org/latest/aggregations/metric/stats/) – Get basic statistics (`count`, `sum`, `min`, `max`, and `avg`).
* [`sum`](https://docs.opensearch.org/latest/aggregations/metric/sum/) – Calculate sum of values.
* [`value_count`](https://docs.opensearch.org/latest/aggregations/metric/value-count/) – Count non-null values.

For a complete list of metric aggregations, see [Metric aggregations](https://docs.opensearch.org/latest/aggregations/metric/).

### Bucket aggregations

Bucket aggregations group documents into buckets based on field values, ranges, or other criteria:

* [`terms`](https://docs.opensearch.org/latest/aggregations/bucket/terms/) – Group by unique field values.
* [`date_histogram`](https://docs.opensearch.org/latest/aggregations/bucket/date-histogram/) – Group by time intervals.
* [`histogram`](https://docs.opensearch.org/latest/aggregations/bucket/histogram/) – Group by numeric intervals.
* [`range`](https://docs.opensearch.org/latest/aggregations/bucket/range/) – Group by numeric ranges.
* [`filter`](https://docs.opensearch.org/latest/aggregations/bucket/filter/) – Create a single bucket matching a filter.
* [`filters`](https://docs.opensearch.org/latest/aggregations/bucket/filters/) – Create multiple buckets, one for each filter.
* [`missing`](https://docs.opensearch.org/latest/aggregations/bucket/missing/) – Group documents that are missing a field value.
* [`significant_terms`](https://docs.opensearch.org/latest/aggregations/bucket/significant-terms/) – Find unusual or interesting terms in a dataset.

For a complete list of bucket aggregations, see [Bucket aggregations](https://docs.opensearch.org/latest/aggregations/bucket/).

### Pipeline aggregations

Pipeline aggregations process the output of other aggregations:

* [`avg_bucket`](https://docs.opensearch.org/latest/aggregations/pipeline/avg-bucket/) – Calculate the average across buckets.
* [`cumulative_sum`](https://docs.opensearch.org/latest/aggregations/pipeline/cumulative-sum/) – Calculate a running total across buckets.
* [`bucket_sort`](https://docs.opensearch.org/latest/aggregations/pipeline/bucket-sort/) – Sort and limit the number of buckets returned.

For a complete list of pipeline aggregations, see [Pipeline aggregations](https://docs.opensearch.org/latest/aggregations/pipeline/).

## Nested aggregations

Aggregations within aggregations are called *nested aggregations* or *subaggregations*.

Metric aggregations produce simple results and can’t contain nested aggregations.

Bucket aggregations produce buckets of documents that you can nest in other aggregations. You can perform complex analysis on your data by nesting metric and bucket aggregations within bucket aggregations.

### General nested aggregation syntax

```
{
  "aggs": {
    "name": {
      "type": {
        "data"
      },
      "aggs": {
        "nested": {
          "type": {
            "data"
          }
        }
      }
    }
  }
}
```

The inner `aggs` keyword begins a new nested aggregation. The syntax of the parent aggregation and the nested aggregation is the same. Nested aggregations run in the context of the preceding parent aggregations.

### Nested aggregation example

The following example uses the OpenSearch Dashboards sample e-commerce data to group orders by category and calculate the average price within each category. This query returns the top 5 categories sorted in descending alphabetical order:

```
GET opensearch_dashboards_sample_data_ecommerce/_search
{
  "size": 0,
  "aggs": {
    "categories": {
      "terms": {
        "field": "category.keyword",
        "size": 5,
        "order": {
          "_key": "desc"
        }
      },
      "aggs": {
        "avg_price": {
          "avg": {
            "field": "taxful_total_price"
          }
        }
      }
    }
  }
}
```

copy

The response includes buckets for each category, sorted in descending alphabetical order, with the average price calculated within each bucket:

```
{
  "took" : 22,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 4675,
      "relation" : "eq"
    },
    "max_score" : null,
    "hits" : [ ]
  },
  "aggregations" : {
    "categories" : {
      "doc_count_error_upper_bound" : 0,
      "sum_other_doc_count" : 572,
      "buckets" : [
        {
          "key" : "Women's Shoes",
          "doc_count" : 1136,
          "avg_price" : {
            "value" : 92.8513836927817
          }
        },
        {
          "key" : "Women's Clothing",
          "doc_count" : 1903,
          "avg_price" : {
            "value" : 70.99312352207042
          }
        },
        {
          "key" : "Women's Accessories",
          "doc_count" : 830,
          "avg_price" : {
            "value" : 73.28953313253012
          }
        },
        {
          "key" : "Men's Shoes",
          "doc_count" : 944,
          "avg_price" : {
            "value" : 97.24356130826271
          }
        },
        {
          "key" : "Men's Clothing",
          "doc_count" : 2024,
          "avg_price" : {
            "value" : 73.81122043292984
          }
        }
      ]
    }
  }
}
```

For more examples of nested aggregations, see [Pipeline aggregations](https://docs.opensearch.org/latest/aggregations/pipeline/#buckets-path).

You can also pair your aggregations with search queries to narrow down the data you’re analyzing before aggregating. If you don’t add a query, OpenSearch implicitly uses the `match_all` query.

## Using aggregations

You can use aggregations through the OpenSearch API or through OpenSearch Dashboards.

### Using the aggregations API

You can run aggregation requests from the command line using a tool such as cURL or from the OpenSearch Dashboards Dev Tools console. For more information about using the Dev Tools console, see [Running queries in the Dev Tools console](https://docs.opensearch.org/latest/dashboards/visualize/run-queries/).

See the [Example aggregation](#example-aggregation) and [Nested aggregation example](#nested-aggregation-example) sections for sample API requests and responses. For detailed syntax and parameters for each aggregation type, see the type-specific documentation pages listed in the [Aggregation types](#aggregation-types) section.

### Using aggregations in OpenSearch Dashboards

Aggregations power many visualization types in OpenSearch Dashboards. When you create a visualization, OpenSearch Dashboards automatically generates aggregation queries based on your selections. If you’re new to OpenSearch Dashboards, see [Getting started with OpenSearch Dashboards](https://docs.opensearch.org/latest/dashboards/getting-started/).

The metric and bucket options you see in the **Visualize** application correspond to the aggregation types described on this page. `Count` is the default Y-axis metric—it displays the number of documents in each bucket (`doc_count`) and requires no field selection.

The following metrics are available in the **Visualize** application: `Count`, `Average`, `Max`, `Median`, `Min`, `Percentile Ranks`, `Percentiles`, `Standard Deviation`, `Sum`, `Top Hit`, `Unique Count`, `Cumulative Sum`, `Derivative`, `Moving Avg`, `Serial Diff`, `Average Bucket`, `Max Bucket`, `Min Bucket`, and `Sum Bucket`.

The following bucket aggregations are available in the **Visualize** application: `Date Histogram`, `Date Range`, `Filters`, `Histogram`, `IPv4 Range`, `Range`, `Significant Terms`, and `Terms`.

For descriptions of each option and how they map to the Aggregations API, see [Configuring visualizations](https://docs.opensearch.org/latest/dashboards/visualize/visualize-app/configuring-viz/#data-tab). For a hands-on tutorial, see [Creating aggregation-based visualizations](https://docs.opensearch.org/latest/dashboards/visualize/visualize-app/aggregation-based-viz/).

## Aggregations on text fields

By default, OpenSearch doesn’t support aggregations on a [`text`](https://docs.opensearch.org/latest/mappings/supported-field-types/text/) field. Because `text` fields are tokenized, an aggregation on a `text` field has to reverse the tokenization process back to its original string and then formulate an aggregation based on that. This kind of an operation consumes significant memory and degrades cluster performance.

While you can enable aggregations on `text` fields by setting the [`fielddata`](https://docs.opensearch.org/latest/mappings/supported-field-types/text/#parameters) parameter to `true` in the mapping, the aggregations are still based on the tokenized words and not on the raw text.

We recommend keeping a raw version of the `text` field as a [`keyword`](https://docs.opensearch.org/latest/mappings/supported-field-types/keyword/) field that you can aggregate on.

The following example creates a `product_name` field with a `keyword` subfield named `raw`. You can perform aggregations on `product_name.raw` instead of on `product_name`:

```
PUT products
{
  "mappings": {
    "properties": {
      "product_name": {
        "type": "text",
        "fielddata": true,
        "fields": {
          "raw": {
            "type": "keyword"
          }
        }
      }
    }
  }
}
```

copy

For more information about mappings, see [Mappings](https://docs.opensearch.org/latest/mappings/).

## Limitations

Because aggregators are processed using the `double` data type for all values, `long` values of 253 and greater are approximate.

## Next steps

* Explore [metric aggregations](https://docs.opensearch.org/latest/aggregations/metric/) to calculate statistics on your data.
* Learn about [bucket aggregations](https://docs.opensearch.org/latest/aggregations/bucket/) to group and analyze data by categories, ranges, or time intervals.
* Discover [pipeline aggregations](https://docs.opensearch.org/latest/aggregations/pipeline/) for advanced analysis using the output of other aggregations.
* Create [visualizations in OpenSearch Dashboards](https://docs.opensearch.org/latest/dashboards/visualize/viz-index/) using aggregations.

* [General aggregation structure](#general-aggregation-structure)
* [Example aggregation](#example-aggregation)
* [Aggregation types](#aggregation-types)
  + [Metric aggregations](#metric-aggregations)
  + [Bucket aggregations](#bucket-aggregations)
  + [Pipeline aggregations](#pipeline-aggregations)
* [Nested aggregations](#nested-aggregations)
  + [General nested aggregation syntax](#general-nested-aggregation-syntax)
  + [Nested aggregation example](#nested-aggregation-example)
* [Using aggregations](#using-aggregations)
  + [Using the aggregations API](#using-the-aggregations-api)
  + [Using aggregations in OpenSearch Dashboards](#using-aggregations-in-opensearch-dashboards)
* [Aggregations on text fields](#aggregations-on-text-fields)
* [Limitations](#limitations)
* [Next steps](#next-steps)

WAS THIS PAGE HELPFUL?

✔ Yes  ✖ No

Tell us why

350 characters left

Thank you for your feedback!

Have a question? [Ask us on the OpenSearch forum](https://forum.opensearch.org/).

Want to contribute? [Edit this page](https://github.com/opensearch-project/documentation-website/edit/main/_aggregations/index.md) or [create an issue](https://github.com/opensearch-project/documentation-website/issues/new?assignees=&labels=untriaged&template=issue_template.md&title=%5BDOC%5D).
