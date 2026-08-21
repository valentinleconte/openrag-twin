---
title: Vector search concepts
source_url: https://docs.opensearch.org/latest/vector-search/getting-started/concepts/
---

# Vector search concepts

Source: https://docs.opensearch.org/latest/vector-search/getting-started/concepts/

[Documentation](/latest/)

# Vector search concepts

This page defines key terms and techniques related to vector search in OpenSearch.

## Vector representations

* [***Vector embeddings***](https://docs.opensearch.org/latest/vector-search/getting-started/vector-search-basics/#vector-embeddings) are numerical representations of data—such as text, images, or audio—that encode meaning or features into a high-dimensional space. These embeddings enable similarity-based comparisons for search and machine learning (ML) tasks.
* ***Dense vectors*** are high-dimensional numerical representations where most elements have nonzero values. They are typically produced by deep learning models and are used in semantic search and ML applications.
* ***Sparse vectors*** contain mostly zero values and are often used in techniques like neural sparse search to efficiently represent and retrieve information.

## Vector search fundamentals

* [***Vector search***](https://docs.opensearch.org/latest/vector-search/getting-started/vector-search-basics/), also known as *similarity search* or *nearest neighbor search*, is a technique for finding items that are most similar to a given input vector. It is widely used in applications such as recommendation systems, image retrieval, and natural language processing.
* A [***space***](https://docs.opensearch.org/latest/vector-search/getting-started/vector-search-basics/#calculating-similarity) defines how similarity or distance between two vectors is measured. Different spaces use different distance metrics, such as Euclidean distance or cosine similarity, to determine how closely vectors resemble each other.
* A [***method***](https://docs.opensearch.org/latest/mappings/supported-field-types/knn-methods-engines/) refers to the algorithm used to organize vector data during indexing and retrieve relevant results during search in approximate k-NN search. Different methods balance trade-offs between accuracy, speed, and memory usage.
* An [***engine***](https://docs.opensearch.org/latest/mappings/supported-field-types/knn-methods-engines/) is the underlying library that implements vector search methods. It determines how vectors are indexed, stored, and retrieved during similarity search operations.

## k-NN search

* ***k-nearest neighbors (k-NN) search*** finds the k most similar vectors to a given query vector in an index. The similarity is determined based on a specified distance metric.
* [***Exact k-NN search***](https://docs.opensearch.org/latest/vector-search/vector-search-techniques/knn-score-script/) performs a brute-force comparison between a query vector and all vectors in an index, computing the exact nearest neighbors. This approach provides high accuracy but can be computationally expensive for large datasets.
* [***Approximate k-NN search***](https://docs.opensearch.org/latest/vector-search/vector-search-techniques/approximate-knn/) reduces computational complexity by using indexing techniques that speed up search operations while maintaining high accuracy. These methods restructure the index or reduce the dimensionality of vectors to improve performance.

## Query types

* An [***agentic query***](https://docs.opensearch.org/latest/query-dsl/specialized/agentic/) accepts a natural language question and uses a preconfigured agent to plan and execute the retrieval automatically.
* A [***k-NN query***](https://docs.opensearch.org/latest/query-dsl/specialized/k-nn/) searches vector fields using a query vector.
* A [***neural query***](https://docs.opensearch.org/latest/query-dsl/specialized/neural/) searches vector fields using text or image data.
* A [***neural sparse query***](https://docs.opensearch.org/latest/query-dsl/specialized/neural-sparse/) searches vector fields using raw text or sparse vector tokens.
* A [***template query***](https://docs.opensearch.org/latest/query-dsl/specialized/template/) contains placeholder variables that are resolved at runtime by search request processors, such as an ML inference processor that generates vector embeddings from text.

## Search techniques

* [***Semantic search***](https://docs.opensearch.org/latest/vector-search/ai-search/semantic-search/) interprets the intent and contextual meaning of a query rather than relying solely on exact keyword matches. This approach improves the relevance of search results, especially for natural language queries.
* [***Hybrid search***](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/) combines lexical (keyword-based) search with semantic (vector-based) search to improve search relevance. This approach ensures that results include both exact keyword matches and conceptually similar content.
* [***Multimodal search***](https://docs.opensearch.org/latest/vector-search/ai-search/multimodal-search/) enables you to search across multiple types of data, such as text and images. It allows queries in one format (for example, text) to retrieve results in another (for example, images).
* [***Radial search***](https://docs.opensearch.org/latest/vector-search/specialized-operations/radial-search-knn/) retrieves all vectors within a specified distance or similarity threshold from a query vector. It is useful for tasks that require finding all relevant matches within a given range rather than retrieving a fixed number of nearest neighbors.
* [***Neural sparse search***](https://docs.opensearch.org/latest/vector-search/ai-search/neural-sparse-search/) uses an inverted index, similar to BM25, to efficiently retrieve relevant documents based on sparse vector representations. This approach maintains the efficiency of traditional lexical search while incorporating semantic understanding.
* [***Conversational search***](https://docs.opensearch.org/latest/vector-search/ai-search/conversational-search/) allows you to interact with a search system using natural language queries and refine results through follow-up questions. This approach enhances the user experience by making search more intuitive and interactive.
* [***Retrieval-augmented generation (RAG)***](https://docs.opensearch.org/latest/vector-search/ai-search/conversational-search/#rag) enhances large language models (LLMs) by retrieving relevant information from an index and incorporating it into the model’s response. This approach improves the accuracy and relevance of generated text.
* [***Reranking***](https://docs.opensearch.org/latest/search-plugins/search-relevance/reranking-search-results/) is a second-pass scoring step that reorders initial search results using a more sophisticated model, such as a cross-encoder, to improve relevance.
* [***Agentic search***](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search/) lets you ask questions in natural language and have an OpenSearch agent plan and execute retrieval automatically. The agent reads the question, selects appropriate tools, and returns relevant results.

## Indexing and storage techniques

* [***Text chunking***](https://docs.opensearch.org/latest/vector-search/ingesting-data/text-chunking/) involves splitting long documents or text passages into smaller segments to improve search retrieval and relevance. Chunking helps vector search models process large amounts of text more effectively.
* [***Vector quantization***](https://docs.opensearch.org/latest/vector-search/optimizing-storage/knn-vector-quantization/) is a technique for reducing the storage size of vector embeddings by approximating them using a smaller set of representative vectors. This process enables efficient storage and retrieval in large-scale vector search applications.
* ***Scalar quantization (SQ)*** reduces vector precision by mapping floating-point values to a limited set of discrete values, decreasing memory requirements while preserving search accuracy.
* ***Product quantization (PQ)*** divides high-dimensional vectors into smaller subspaces and quantizes each subspace separately, enabling efficient approximate nearest neighbor search with reduced memory usage.
* ***Binary quantization*** compresses vector representations by converting numerical values to binary formats. This technique reduces storage requirements and accelerates similarity computations.
* [***Disk-based vector search***](https://docs.opensearch.org/latest/vector-search/optimizing-storage/disk-based-vector-search/) stores vector embeddings on disk rather than in memory, using binary quantization to reduce memory consumption while maintaining search efficiency.

* [Vector representations](#vector-representations)
* [Vector search fundamentals](#vector-search-fundamentals)
* [k-NN search](#k-nn-search)
* [Query types](#query-types)
* [Search techniques](#search-techniques)
* [Indexing and storage techniques](#indexing-and-storage-techniques)

WAS THIS PAGE HELPFUL?

✔ Yes  ✖ No

Tell us why

350 characters left

Thank you for your feedback!

Have a question? [Ask us on the OpenSearch forum](https://forum.opensearch.org/).

Want to contribute? [Edit this page](https://github.com/opensearch-project/documentation-website/edit/main/_vector-search/getting-started/concepts.md) or [create an issue](https://github.com/opensearch-project/documentation-website/issues/new?assignees=&labels=untriaged&template=issue_template.md&title=%5BDOC%5D).
