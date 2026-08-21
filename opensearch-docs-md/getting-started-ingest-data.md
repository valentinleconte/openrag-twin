---
title: Ingest your data into OpenSearch
source_url: https://docs.opensearch.org/latest/getting-started/ingest-data/
---

# Ingest your data into OpenSearch

Source: https://docs.opensearch.org/latest/getting-started/ingest-data/

[Documentation](/latest/)

# Ingest your data into OpenSearch

There are several ways to ingest data into OpenSearch:

* Ingest individual documents. For more information, see [Indexing documents](https://docs.opensearch.org/latest/getting-started/communicate/#indexing-documents).
* Index multiple documents in bulk. For more information, see [Bulk indexing](#bulk-indexing).
* Use Data Prepper—an OpenSearch server-side data collector that can enrich data for downstream analysis and visualization. For more information, see [Data Prepper](https://docs.opensearch.org/latest/data-prepper/).
* Use other ingestion tools. For more information, see [OpenSearch tools](https://docs.opensearch.org/latest/tools/).

## Bulk indexing

To index documents in bulk, you can use the [Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/). For example, if you want to index several documents into the `students` index, send the following request:

```
POST _bulk
{ "create": { "_index": "students", "_id": "2" } }
{ "name": "Jonathan Powers", "gpa": 3.85, "grad_year": 2025 }
{ "create": { "_index": "students", "_id": "3" } }
{ "name": "Jane Doe", "gpa": 3.52, "grad_year": 2024 }
```

copy

## Experiment with sample data

OpenSearch provides a fictitious e-commerce dataset that you can use to experiment with REST API requests and OpenSearch Dashboards visualizations. You can create an index and define field mappings by downloading the corresponding dataset and mapping files.

### Create a sample index

Use the following steps to create a sample index and define field mappings for the document fields:

1. Download the [`ecommerce-field_mappings.json`](https://github.com/opensearch-project/documentation-website/blob/3.8/assets/examples/ecommerce-field_mappings.json) file. This file defines a [mapping](https://docs.opensearch.org/latest/opensearch/mappings/) for the sample data you will use.

   To use cURL, send the following request:

   ```
    curl -O https://raw.githubusercontent.com/opensearch-project/documentation-website/3.8/assets/examples/ecommerce-field_mappings.json
   ```

   copy

   To use wget, send the following request:

   ```
    wget https://raw.githubusercontent.com/opensearch-project/documentation-website/3.8/assets/examples/ecommerce-field_mappings.json
   ```

   copy
2. Download [`ecommerce.ndjson`](https://github.com/opensearch-project/documentation-website/blob/3.8/assets/examples/ecommerce.ndjson). This file contains the index data formatted so that it can be ingested by the Bulk API:

   To use cURL, send the following request:

   ```
    curl -O https://raw.githubusercontent.com/opensearch-project/documentation-website/3.8/assets/examples/ecommerce.ndjson
   ```

   copy

   To use wget, send the following request:

   ```
    wget https://raw.githubusercontent.com/opensearch-project/documentation-website/3.8/assets/examples/ecommerce.ndjson
   ```

   copy
3. Define the field mappings provided in the mapping file:

   ```
    curl -H "Content-Type: application/json" -X PUT "https://localhost:9200/ecommerce" -ku admin:<custom-admin-password> --data-binary "@ecommerce-field_mappings.json"
   ```

   copy
4. Upload the documents using the Bulk API:

   ```
    curl -H "Content-Type: application/x-ndjson" -X PUT "https://localhost:9200/ecommerce/_bulk" -ku admin:<custom-admin-password> --data-binary "@ecommerce.ndjson"
   ```

   copy

### Query the data

Query the data using the Search API. The following query searches for documents in which `customer_first_name` is `Sonya`:

```
GET ecommerce/_search
{
  "query": {
    "match": {
      "customer_first_name": "Sonya"
    }
  }
}
```

copy

### Visualize the data

To learn how to use OpenSearch Dashboards to visualize the data, see the [OpenSearch Dashboards getting started guide](https://docs.opensearch.org/latest/dashboards/getting-started/).

## Further reading

* For information about Data Prepper, see [Data Prepper](https://docs.opensearch.org/latest/data-prepper/).
* For information about ingestion tools, see [OpenSearch tools](https://docs.opensearch.org/latest/tools/).
* For information about OpenSearch Dashboards, see [OpenSearch Dashboards getting started guide](https://docs.opensearch.org/latest/dashboards/getting-started/).
* For information about bulk indexing, see [Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/).

## Next steps

* See [Search your data](https://docs.opensearch.org/latest/getting-started/search-data/) to learn about search options.

* [Bulk indexing](#bulk-indexing)
* [Experiment with sample data](#experiment-with-sample-data)
  + [Create a sample index](#create-a-sample-index)
  + [Query the data](#query-the-data)
  + [Visualize the data](#visualize-the-data)
* [Further reading](#further-reading)
* [Next steps](#next-steps)

WAS THIS PAGE HELPFUL?

✔ Yes  ✖ No

Tell us why

350 characters left

Thank you for your feedback!

Have a question? [Ask us on the OpenSearch forum](https://forum.opensearch.org/).

Want to contribute? [Edit this page](https://github.com/opensearch-project/documentation-website/edit/main/_getting-started/ingest-data.md) or [create an issue](https://github.com/opensearch-project/documentation-website/issues/new?assignees=&labels=untriaged&template=issue_template.md&title=%5BDOC%5D).
