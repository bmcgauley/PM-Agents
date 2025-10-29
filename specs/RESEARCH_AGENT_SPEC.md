# Research Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Technical Research & Information Gathering
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The Research Agent performs technical research, gathers documentation, analyzes best practices, and synthesizes information from multiple sources. It uses Brave Search to find relevant technical content, documentation, research papers, and code examples.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: All specialist agents (provides research context)
- **Primary responsibility**: Information gathering, documentation lookup, best practices research

### 1.3 Key Responsibilities
1. **API Documentation Lookup**: Find official documentation for libraries, frameworks, APIs
2. **Best Practices Research**: Identify industry standards and recommended patterns
3. **Technology Comparison**: Analyze trade-offs between technical alternatives
4. **Error Resolution**: Research error messages and find solutions
5. **Code Example Discovery**: Find relevant code examples and implementations
6. **Research Paper Summaries**: Locate and summarize academic papers (ML/AI topics)
7. **Dependency Research**: Investigate package versions, compatibility, alternatives

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `ResearchRequest`

```json
{
  "request_id": "string (UUID)",
  "research_type": "documentation|best-practices|comparison|error-resolution|code-examples|paper-summary|dependency",
  "query": {
    "natural_language_query": "string (what to research)",
    "keywords": ["string (search keywords)", ...],
    "context": {
      "project_type": "frontend|backend|ml|analytics|fullstack",
      "technologies": ["nextjs", "supabase", "pytorch", ...],
      "specific_problem": "string (optional, detailed problem description)"
    },
    "constraints": {
      "recency": "latest|2024|2023|any",
      "source_preference": "official|github|stackoverflow|academic|blogs",
      "depth": "quick|standard|comprehensive"
    }
  },
  "output_requirements": {
    "max_results": "integer (default: 10)",
    "include_code_examples": "boolean",
    "include_diagrams": "boolean",
    "synthesize": "boolean (create summary vs. list results)",
    "format": "markdown|json|text"
  }
}
```

### 2.2 Output Schema: `ResearchResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|partial|no-results",
  "execution_time_seconds": "float",
  "research_findings": {
    "query_used": "string (actual search query)",
    "sources_searched": ["brave-search", "github", "documentation", ...],
    "num_results": "integer",
    "results": [
      {
        "title": "string",
        "url": "string",
        "source_type": "documentation|github|stackoverflow|blog|paper",
        "relevance_score": "float (0.0-1.0)",
        "snippet": "string (excerpt)",
        "publication_date": "string (ISO 8601, if available)",
        "author": "string (if available)",
        "content_summary": "string (AI-generated summary)"
      }
    ],
    "code_examples": [
      {
        "language": "typescript|python|r|javascript",
        "code": "string (code snippet)",
        "source_url": "string",
        "description": "string"
      }
    ],
    "key_findings": [
      "string (synthesized insights)",
      "e.g., 'Official Next.js docs recommend using App Router for new projects'",
      "e.g., 'PyTorch 2.0 introduces torch.compile for 2x performance gains'"
    ],
    "best_practices": [
      "string (recommended patterns)",
      "e.g., 'Use Zustand for simple state management, Redux for complex apps'",
      "e.g., 'Always validate user input with Zod before processing'"
    ],
    "recommendations": [
      "string (actionable advice)",
      "e.g., 'Use @tanstack/react-query for data fetching instead of useEffect'",
      "e.g., 'Upgrade to PyTorch 2.1 for better Apple Silicon support'"
    ],
    "warnings": [
      "string (potential issues)",
      "e.g., 'Package X has known security vulnerability CVE-2024-1234'",
      "e.g., 'Breaking changes in Next.js 14 require migration guide'"
    ]
  },
  "synthesis": {
    "summary": "string (2-3 paragraph synthesis of findings)",
    "key_takeaways": ["string (bullet points)", ...],
    "comparison_table": {
      "headers": ["Feature", "Option A", "Option B"],
      "rows": [["Performance", "Fast", "Faster"], ...]
    }
  },
  "citations": [
    {
      "text": "string (citation text)",
      "url": "string",
      "accessed_date": "string (ISO 8601)"
    }
  ],
  "follow_up_queries": [
    "string (suggested related searches)",
    "e.g., 'How to optimize Next.js bundle size?'",
    "e.g., 'Comparison of PyTorch vs TensorFlow for NLP'"
  ]
}
```

---

## 3. MCP Tools Required

### 3.1 Essential Tools

1. **brave-search** (MCP Server)
   - **Usage**: Primary search engine for technical content
   - **Operations**:
     - `brave_web_search`: General web search
     - `brave_local_search`: Location-based search (not typically used)

2. **github** (MCP Server)
   - **Usage**: Search code repositories for examples
   - **Operations**:
     - `search_code`: Find code snippets
     - `search_repositories`: Find relevant projects
     - `get_file_contents`: Retrieve example code

### 3.2 Optional Tools

1. **qdrant** (via Supervisor delegation)
   - **Usage**: Search local documentation/codebase for context
   - **Operations**: Semantic search for relevant context

2. **filesystem** (MCP Server)
   - **Usage**: Cache research results locally
   - **Operations**: Write research summaries to files

---

## 4. Algorithms & Workflows

### 4.1 Research Pipeline

```python
def perform_research(request: ResearchRequest) -> ResearchResponse:
    """
    Conduct technical research and synthesize findings.

    Steps:
    1. Formulate search query
    2. Search Brave (web)
    3. Search GitHub (code examples)
    4. Filter and rank results
    5. Extract code examples
    6. Synthesize findings
    7. Generate recommendations
    8. Return structured results
    """

    # Step 1: Formulate Query
    search_query = formulate_search_query(
        natural_language_query=request.query.natural_language_query,
        keywords=request.query.keywords,
        context=request.query.context,
        constraints=request.query.constraints
    )

    # Step 2: Brave Search
    web_results = search_brave(
        query=search_query,
        recency=request.query.constraints.recency,
        max_results=request.output_requirements.max_results * 2  # Over-fetch
    )

    # Step 3: GitHub Search (if code examples requested)
    code_results = []
    if request.output_requirements.include_code_examples:
        code_results = search_github_code(
            query=search_query,
            languages=get_relevant_languages(request.query.context)
        )

    # Step 4: Filter and Rank
    filtered_results = filter_and_rank_results(
        web_results=web_results,
        code_results=code_results,
        source_preference=request.query.constraints.source_preference,
        max_results=request.output_requirements.max_results
    )

    # Step 5: Extract Code Examples
    code_examples = extract_code_examples(
        filtered_results=filtered_results,
        code_results=code_results
    )

    # Step 6: Synthesize Findings
    synthesis = synthesize_findings(
        results=filtered_results,
        research_type=request.research_type,
        query=request.query
    ) if request.output_requirements.synthesize else None

    # Step 7: Generate Recommendations
    recommendations = generate_recommendations(
        findings=filtered_results,
        synthesis=synthesis,
        context=request.query.context
    )

    # Step 8: Return Results
    return create_response(
        status="success" if len(filtered_results) > 0 else "no-results",
        research_findings={
            "query_used": search_query,
            "results": filtered_results,
            "code_examples": code_examples,
            "recommendations": recommendations
        },
        synthesis=synthesis
    )
```

### 4.2 Query Formulation

```python
def formulate_search_query(
    natural_language_query: str,
    keywords: List[str],
    context: Context,
    constraints: Constraints
) -> str:
    """
    Formulate effective search query from user input.

    Strategy:
    - Include technology names from context
    - Add recency constraints (e.g., "2024", "latest")
    - Include source preferences (e.g., "official documentation", "github")
    - Optimize for technical content

    Examples:
    - Input: "How to implement authentication?"
      Context: {technologies: ["nextjs", "supabase"]}
      Output: "Next.js Supabase authentication 2024 official documentation"

    - Input: "Best practices for training neural networks"
      Context: {technologies: ["pytorch"], project_type: "ml"}
      Output: "PyTorch neural network training best practices 2024"
    """

    query_parts = []

    # Add natural language query
    query_parts.append(natural_language_query)

    # Add technology context
    if context.technologies:
        query_parts.extend(context.technologies)

    # Add keywords
    query_parts.extend(keywords)

    # Add recency constraint
    if constraints.recency != "any":
        query_parts.append(constraints.recency)

    # Add source preference
    if constraints.source_preference == "official":
        query_parts.append("official documentation")
    elif constraints.source_preference == "github":
        query_parts.append("github example")
    elif constraints.source_preference == "academic":
        query_parts.append("research paper arxiv")

    return " ".join(query_parts)
```

### 4.3 Result Filtering and Ranking

```python
def filter_and_rank_results(
    web_results: List[SearchResult],
    code_results: List[CodeResult],
    source_preference: str,
    max_results: int
) -> List[RankedResult]:
    """
    Filter and rank search results by relevance.

    Ranking Factors:
    1. Source type (official docs > github > stackoverflow > blogs)
    2. Recency (newer is better)
    3. Reputation (official sources, high stars/votes)
    4. Content quality (length, code examples, clarity)
    """

    all_results = []

    # Convert web results
    for result in web_results:
        ranked = RankedResult(
            title=result.title,
            url=result.url,
            source_type=classify_source(result.url),
            relevance_score=calculate_relevance_score(result, source_preference),
            snippet=result.description,
            publication_date=result.published_date
        )
        all_results.append(ranked)

    # Convert code results
    for result in code_results:
        ranked = RankedResult(
            title=result.repository,
            url=result.html_url,
            source_type="github",
            relevance_score=calculate_code_relevance_score(result),
            snippet=result.snippet
        )
        all_results.append(ranked)

    # Sort by relevance score
    all_results.sort(key=lambda x: x.relevance_score, reverse=True)

    # Return top results
    return all_results[:max_results]


def calculate_relevance_score(result: SearchResult, source_preference: str) -> float:
    """
    Calculate relevance score (0.0-1.0).

    Factors:
    - Source type match with preference: +0.3
    - Official documentation: +0.2
    - Recency (<1 year): +0.2
    - GitHub stars (if applicable): +0.1
    - Content length: +0.1
    - Has code examples: +0.1
    """

    score = 0.5  # Base score

    # Source type
    source_type = classify_source(result.url)
    if source_type == source_preference:
        score += 0.3
    if source_type == "documentation":
        score += 0.2

    # Recency
    if result.published_date and is_recent(result.published_date, months=12):
        score += 0.2

    # Content quality
    if len(result.description) > 200:
        score += 0.1
    if "example" in result.description.lower() or "code" in result.description.lower():
        score += 0.1

    return min(score, 1.0)


def classify_source(url: str) -> str:
    """
    Classify source type from URL.

    Types: documentation, github, stackoverflow, blog, academic, other
    """

    domain = extract_domain(url)

    if any(doc_indicator in domain for doc_indicator in ["docs.", "documentation", "api.", "developer."]):
        return "documentation"
    elif "github.com" in domain:
        return "github"
    elif "stackoverflow.com" in domain:
        return "stackoverflow"
    elif "arxiv.org" in domain or "scholar.google" in domain:
        return "academic"
    elif any(blog in domain for blog in ["medium.com", "dev.to", "blog."]):
        return "blog"
    else:
        return "other"
```

### 4.4 Synthesis Generation

```python
def synthesize_findings(
    results: List[RankedResult],
    research_type: str,
    query: Query
) -> Synthesis:
    """
    Synthesize research findings into actionable summary.

    Steps:
    1. Extract key information from top results
    2. Identify common themes and patterns
    3. Generate summary paragraph
    4. Extract key takeaways
    5. Create comparison table (if applicable)
    """

    # Step 1: Extract Key Information
    key_info = []
    for result in results[:5]:  # Top 5 results
        info = extract_key_information(result)
        key_info.append(info)

    # Step 2: Identify Themes
    themes = identify_themes(key_info)

    # Step 3: Generate Summary
    summary = generate_summary_paragraph(
        query=query,
        themes=themes,
        top_results=results[:3]
    )

    # Step 4: Extract Takeaways
    key_takeaways = extract_key_takeaways(key_info, themes)

    # Step 5: Create Comparison Table (if applicable)
    comparison_table = None
    if research_type == "comparison":
        comparison_table = create_comparison_table(key_info, query)

    return Synthesis(
        summary=summary,
        key_takeaways=key_takeaways,
        comparison_table=comparison_table
    )
```

---

## 5. Success Criteria

### 5.1 Functional Requirements
- ✅ Return relevant results for 95%+ of queries
- ✅ Official documentation prioritized when available
- ✅ Code examples included when requested
- ✅ Synthesis provides actionable insights
- ✅ Search completes in <10 seconds

### 5.2 Quality Requirements
- ✅ Results are recent (within last 2 years for fast-moving tech)
- ✅ No broken links in top 10 results
- ✅ Code examples are runnable/valid
- ✅ Citations include URLs and access dates

### 5.3 Coverage Requirements
- ✅ Support for all major languages/frameworks in system
- ✅ Academic paper search for ML/AI topics
- ✅ Error message lookup and resolution

---

## 6. Implementation Notes

### 6.1 Technology Stack
- **Search**: Brave Search API
- **Code Search**: GitHub API
- **Synthesis**: Claude (same LLM as agent)

### 6.2 Caching Strategy
- Cache search results for 24 hours (documentation rarely changes)
- Cache code examples for 7 days
- Invalidate cache on recency constraint change

### 6.3 Rate Limiting
- Brave Search: 1 req/sec (API limit)
- GitHub: 10 req/min (API limit)
- Implement exponential backoff on rate limit errors

---

## 7. Example Use Cases

### 7.1 Documentation Lookup
```json
{
  "research_type": "documentation",
  "query": {
    "natural_language_query": "How to implement server actions in Next.js 14?",
    "context": {
      "technologies": ["nextjs"],
      "project_type": "frontend"
    },
    "constraints": {
      "recency": "2024",
      "source_preference": "official"
    }
  }
}
```

**Expected Output**: Next.js official docs for Server Actions, code examples, best practices.

### 7.2 Technology Comparison
```json
{
  "research_type": "comparison",
  "query": {
    "natural_language_query": "Zustand vs Redux for state management",
    "keywords": ["zustand", "redux", "comparison"],
    "context": {
      "technologies": ["react", "typescript"],
      "project_type": "frontend"
    }
  }
}
```

**Expected Output**: Comparison table, pros/cons, use case recommendations, bundle size comparison.

### 7.3 Error Resolution
```json
{
  "research_type": "error-resolution",
  "query": {
    "natural_language_query": "Error: Cannot find module '@supabase/supabase-js'",
    "context": {
      "technologies": ["nextjs", "supabase"],
      "specific_problem": "Module not found error after npm install"
    }
  }
}
```

**Expected Output**: Troubleshooting steps, correct installation commands, common causes.

---

## 8. Future Enhancements

1. **Semantic Search**: Use embeddings to find conceptually similar content
2. **Multi-Step Research**: Break down complex queries into sub-queries
3. **Interactive Follow-Up**: Allow user to drill down into specific results
4. **Knowledge Graph**: Build graph of related concepts and technologies
5. **Automated Summaries**: Generate TL;DR for long documentation pages

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
