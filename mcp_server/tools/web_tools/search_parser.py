from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from agent.utils.logger import get_logger
from urllib.parse import urlparse
import re

logger = get_logger(__name__)


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    position: int
    domain: str
    favicon_url: Optional[str] = None
    source_type: str = "web"
    published_date: Optional[str] = None


@dataclass
class SearchResultSet:
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    refinements: List[str] = None
    search_engine: str = "google"

    def __post_init__(self):
        if self.refinements is None:
            self.refinements = []


class GoogleSearchParser:
    @staticmethod
    def parse(html: str, query: str = "") -> SearchResultSet:
        results = []
        position = 1

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            result_containers = soup.find_all("div", {"class": "g"})

            for container in result_containers[:10]:
                try:
                    link_elem = container.find("a", {"href": True})
                    title_elem = container.find("h3")
                    snippet_elem = container.find("span", {"class": "st"})

                    if not link_elem or not title_elem:
                        continue

                    url = link_elem["href"]
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    domain = urlparse(url).netloc
                    favicon_url = f"https://www.google.com/s2/favicons?domain={domain}"

                    result = SearchResult(
                        url=url,
                        title=title,
                        snippet=snippet,
                        position=position,
                        domain=domain,
                        favicon_url=favicon_url,
                        source_type="web",
                    )

                    results.append(result)
                    position += 1
                except Exception as e:
                    logger.debug(f"Failed to parse result container: {e}")
                    continue

            total_results = len(results)

            return SearchResultSet(
                query=query,
                results=results,
                total_results=total_results,
                search_time_ms=0,
                search_engine="google",
            )
        except Exception as e:
            logger.error(f"Failed to parse Google search results: {e}")
            return SearchResultSet(
                query=query,
                results=[],
                total_results=0,
                search_time_ms=0,
                search_engine="google",
            )


class DuckDuckGoParser:
    @staticmethod
    def parse(json_data: Dict[str, Any], query: str = "") -> SearchResultSet:
        results = []
        position = 1

        try:
            results_data = json_data.get("results", [])

            for result in results_data[:10]:
                try:
                    url = result.get("url")
                    title = result.get("title")
                    snippet = result.get("snippet", "")

                    if not url or not title:
                        continue

                    domain = urlparse(url).netloc

                    search_result = SearchResult(
                        url=url,
                        title=title,
                        snippet=snippet,
                        position=position,
                        domain=domain,
                        favicon_url=f"https://www.google.com/s2/favicons?domain={domain}",
                        source_type="web",
                    )

                    results.append(search_result)
                    position += 1
                except Exception as e:
                    logger.debug(f"Failed to parse DuckDuckGo result: {e}")
                    continue

            total_results = json_data.get("meta", {}).get("total_results", len(results))

            return SearchResultSet(
                query=query,
                results=results,
                total_results=total_results,
                search_time_ms=0,
                search_engine="duckduckgo",
            )
        except Exception as e:
            logger.error(f"Failed to parse DuckDuckGo results: {e}")
            return SearchResultSet(
                query=query,
                results=[],
                total_results=0,
                search_time_ms=0,
                search_engine="duckduckgo",
            )


class SearchResultFilter:
    @staticmethod
    def deduplicate(results: List[SearchResult], similarity_threshold: float = 0.8) -> List[SearchResult]:
        unique_results = []
        seen_urls = set()

        for result in results:
            domain_path = urlparse(result.url).netloc + urlparse(result.url).path
            if domain_path not in seen_urls:
                unique_results.append(result)
                seen_urls.add(domain_path)

        return unique_results

    @staticmethod
    def filter_by_domain(results: List[SearchResult], domains: List[str]) -> List[SearchResult]:
        domain_set = {d.lower() for d in domains}
        return [r for r in results if any(r.domain.lower().endswith(d) for d in domain_set)]

    @staticmethod
    def filter_by_source_type(results: List[SearchResult], types: List[str]) -> List[SearchResult]:
        return [r for r in results if r.source_type in types]

    @staticmethod
    def rank_by_relevance(results: List[SearchResult], query: str) -> List[SearchResult]:
        query_terms = set(query.lower().split())

        def calculate_score(result: SearchResult) -> float:
            score = 0.0

            title_terms = set(result.title.lower().split())
            score += len(query_terms & title_terms) * 2

            snippet_terms = set(result.snippet.lower().split())
            score += len(query_terms & snippet_terms)

            if result.domain in ["wikipedia.org", "github.com", "stackoverflow.com"]:
                score += 1

            return score

        ranked = sorted(results, key=calculate_score, reverse=True)
        return ranked

    @staticmethod
    def filter_out_ads_and_duplicates(results: List[SearchResult]) -> List[SearchResult]:
        filtered = []
        seen_titles = set()

        for result in results:
            normalized_title = result.title.lower().strip()

            if normalized_title not in seen_titles and "advertisement" not in result.snippet.lower():
                filtered.append(result)
                seen_titles.add(normalized_title)

        return filtered
