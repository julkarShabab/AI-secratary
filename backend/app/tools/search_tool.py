from typing import Dict, Any, List
from ddgs import DDGS
from app.tools.base_tool import BaseTool


class SearchTool(BaseTool):

    @property
    def name(self) -> str:
        return "search_tool"

    @property
    def description(self) -> str:
        return "Use this to search the web for current information, news, research, or any topic"

    @property
    def parameters(self) -> Dict:
        return {
            "query": {
                "type": "string",
                "description": "The search query to look up",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Number of results to return. Default 5.",
                "required": False
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        query = params.get("query")
        max_results = params.get("max_results", 5)

        if not query:
            return {
                "success": False,
                "result": None,
                "error": "query is required"
            }

        try:
            results = self._search(query=query, max_results=max_results)
            return {
                "success": True,
                "result": results,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Search failed: {str(e)}"
            }

    def _search(self, query: str, max_results: int) -> List[Dict]:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
        return results