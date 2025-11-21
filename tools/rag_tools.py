"""
Tools for interacting with the RAG system
"""
from typing import List

from tools.base import BaseTool, ToolResult, ToolParameter, ToolCategory
from rag.retriever import retrieve_relevant_chunks
from rag.collections import get_all_stats, list_collections


class SearchVectorDBTool(BaseTool):
    """Search the vector database for relevant documents"""

    def __init__(self):
        super().__init__()
        self.category = ToolCategory.SEARCH

    def get_description(self) -> str:
        return "Search the knowledge base for relevant information"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="The search query",
                required=True
            ),
            ToolParameter(
                name="collection",
                type="string",
                description="Which collection to search (or 'all' for all collections)",
                required=False,
                default="ai_academy_course"
            ),
            ToolParameter(
                name="top_k",
                type="number",
                description="Number of results to return",
                required=False,
                default=5
            )
        ]

    def execute(self, query: str, collection: str = "ai_academy_course", top_k: int = 5) -> ToolResult:
        """Execute vector search"""
        try:
            # Handle "all" collections case
            if collection == "all":
                all_collections = list_collections()
                all_results = []

                for coll_name in all_collections:
                    try:
                        docs = retrieve_relevant_chunks(
                            query=query,
                            collection_name=coll_name,
                            top_k=top_k
                        )
                        all_results.extend(docs)
                    except Exception as e:
                        # Skip collections that fail
                        continue

                # Sort by relevance if we have metadata
                results = all_results[:top_k]
            else:
                results = retrieve_relevant_chunks(
                    query=query,
                    collection_name=collection,
                    top_k=top_k
                )

            # Format results with full source metadata
            formatted_results = []
            for doc in results:
                # Increase content preview for better context (300 -> 800 chars)
                content_preview = doc.page_content[:800] + "..." if len(doc.page_content) > 800 else doc.page_content

                result_item = {
                    "content": content_preview,
                    "source": doc.metadata.get("source", "unknown"),
                    "collection": doc.metadata.get("collection", collection)
                }

                # Add page number for PDFs
                if "page" in doc.metadata:
                    result_item["page"] = doc.metadata.get("page")

                # Add source type for context
                if "source_type" in doc.metadata:
                    result_item["source_type"] = doc.metadata.get("source_type")

                formatted_results.append(result_item)

            return ToolResult(
                success=True,
                result=formatted_results
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )


class GetCollectionStatsTool(BaseTool):
    """Get statistics about available collections"""

    def __init__(self):
        super().__init__()
        self.category = ToolCategory.INFORMATION

    def get_description(self) -> str:
        return "Get statistics about the knowledge base collections"

    def get_parameters(self) -> List[ToolParameter]:
        return []

    def execute(self) -> ToolResult:
        """Get collection stats"""
        try:
            stats = get_all_stats()

            # Format for readability
            formatted_stats = {}
            for coll_name, coll_stats in stats.items():
                if "error" in coll_stats:
                    formatted_stats[coll_name] = {"status": "error", "error": coll_stats["error"]}
                else:
                    formatted_stats[coll_name] = {
                        "status": "ok",
                        "count": coll_stats.get("count", 0)
                    }

            return ToolResult(success=True, result=formatted_stats)
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))
