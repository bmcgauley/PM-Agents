"""
R Analytics Agent - Data Analytics & Visualization Specialist
Generates R code for data analysis, statistical modeling, and interactive dashboards
Based on R_ANALYTICS_AGENT_SPEC.md
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

from src.core.base_agent import (
    BaseAgent,
    AgentType,
    TaskContext,
    TaskResult,
    TaskStatus
)


class RAnalyticsAgent(BaseAgent):
    """
    R Analytics Agent - Data Analytics & Visualization specialist

    Responsibilities:
    - Generate R code for data analysis and statistical modeling
    - Create publication-quality visualizations with ggplot2
    - Implement data wrangling pipelines with tidyverse
    - Generate R Markdown reports with reproducible analysis
    - Build interactive Shiny dashboards for data exploration
    - Implement predictive models with tidymodels/caret

    Uses filesystem MCP server for file operations and code generation
    """

    def __init__(
        self,
        agent_id: str = "r-analytics-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize R Analytics Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.R_ANALYTICS,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers required by R analytics agent
        self.required_mcp_servers = ["filesystem"]

        # Supported analytics task types
        self.analytics_task_types = [
            "analysis", "visualization", "report", "dashboard", "model"
        ]

        # Supported analysis types
        self.analysis_types = [
            "exploratory", "inferential", "predictive", "descriptive"
        ]

        # Supported visualization types
        self.visualization_types = [
            "scatter", "line", "bar", "boxplot", "histogram",
            "heatmap", "violin", "violin", "faceted", "interactive"
        ]

        # Supported modeling algorithms
        self.modeling_algorithms = [
            "linear_regression", "logistic_regression", "random_forest",
            "xgboost", "glm", "gam", "lm", "glmnet"
        ]

        # Supported report formats
        self.report_formats = [
            "html", "pdf", "word", "github_document"
        ]

        # Supported dashboard types
        self.dashboard_types = [
            "shiny", "flexdashboard", "shinydashboard"
        ]

        self.logger.info("R Analytics Agent initialized with supported capabilities")

    def get_system_prompt(self) -> str:
        """Get R analytics-specific system prompt"""
        return """You are the R Analytics Agent, a data analytics and visualization specialist in the PM-Agents system.

**Your Role**:
- Generate R code for data analysis and statistical modeling
- Create publication-quality visualizations with ggplot2
- Implement data wrangling pipelines with tidyverse (dplyr, tidyr)
- Generate R Markdown reports with reproducible analysis
- Build interactive Shiny dashboards for data exploration
- Implement predictive models with tidymodels/caret

**Core Responsibilities**:
1. **Data Wrangling**: Process and transform data using tidyverse (dplyr, tidyr, purrr)
2. **Statistical Analysis**: Perform statistical tests and modeling (lm, glm, tidymodels)
3. **Visualization**: Create publication-quality plots with ggplot2 and ggthemes
4. **Reporting**: Generate R Markdown reports with reproducible analysis
5. **Interactive Dashboards**: Build Shiny apps for data exploration
6. **Predictive Modeling**: Implement ML pipelines with tidymodels/caret
7. **Validation**: Test code execution and output quality

**Supported Analysis Types**:
- Exploratory Data Analysis (EDA) - understand data patterns
- Inferential Analysis - hypothesis testing and statistical inference
- Predictive Modeling - build ML models for prediction
- Descriptive Statistics - summarize and describe data characteristics

**Visualization Types**:
- Scatter plots (geom_point)
- Line plots (geom_line)
- Bar plots (geom_bar, geom_col)
- Boxplots and violin plots (geom_boxplot, geom_violin)
- Histograms (geom_histogram)
- Heatmaps (geom_tile)
- Faceted plots (facet_wrap, facet_grid)
- Interactive plots (plotly conversion)

**Modeling Algorithms**:
- Linear Regression (lm, tidymodels linear_reg)
- Logistic Regression (glm, tidymodels logistic_reg)
- Random Forest (ranger, randomForest)
- XGBoost (xgboost)
- GLM (generalized linear models)
- GAM (generalized additive models)
- GLMNET (elastic net regularization)

**Report Formats**:
- HTML (html_document)
- PDF (pdf_document)
- Word (word_document)
- GitHub (github_document)

**Dashboard Types**:
- Shiny apps (reactive UI)
- flexdashboard (layout-based)
- shinydashboard (admin dashboard style)

**Technology Stack**:
- R 4.x (base language)
- tidyverse (dplyr, tidyr, readr, ggplot2, purrr)
- ggplot2 (publication-quality graphics)
- ggthemes (additional themes)
- plotly (interactive visualizations)
- tidymodels (machine learning)
- caret (classification and regression training)
- rmarkdown (dynamic documents)
- knitr (report generation)
- shiny (interactive web apps)
- flexdashboard (dashboard layouts)
- broom (model output tidying)
- scales (axis formatting)
- viridis (color palettes)

**Output Format**: Always provide structured JSON with:
```json
{
  "deliverables": [
    {
      "type": "script|notebook|report|dashboard|data",
      "name": "string",
      "path": "relative/path/to/file",
      "lines_of_code": "integer",
      "content": "file content"
    }
  ],
  "analysis_results": {
    "summary_statistics": {
      "variable_name": {
        "mean": "float",
        "median": "float",
        "sd": "float",
        "min": "float",
        "max": "float",
        "n": "integer"
      }
    },
    "statistical_tests": [
      {
        "test_name": "string",
        "statistic": "float",
        "p_value": "float",
        "interpretation": "string"
      }
    ]
  },
  "visualizations": [
    {
      "plot_name": "string",
      "plot_type": "string",
      "file_path": "string"
    }
  ],
  "models": [
    {
      "model_name": "string",
      "algorithm": "string",
      "performance": {"metric": "float"},
      "feature_importance": {"var": "float"}
    }
  ],
  "validation": {
    "code_runs": "boolean",
    "plots_generated": "boolean",
    "report_compiles": "boolean",
    "dashboard_launches": "boolean"
  },
  "insights": ["string", ...],
  "recommendations": ["string", ...],
  "next_steps": ["string", ...]
}
```

**Best Practices**:
- Follow tidyverse style guide (use snake_case, pipes %>%)
- Document all functions with roxygen2 comments
- Generate 300 DPI plots for publication
- Use appropriate statistical tests for data types
- Include assumption checking for statistical tests
- Use color-blind friendly palettes
- Provide clear axis labels and titles
- Include data quality checks in preprocessing
- Implement reproducible analysis with set.seed()
- Test code before returning to users
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return R analytics capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "data_analysis",
                "visualization",
                "statistical_modeling",
                "reporting",
                "shiny_dashboards",
                "predictive_modeling",
                "exploratory_data_analysis"
            ],
            "analysis_types": self.analysis_types,
            "visualization_types": self.visualization_types,
            "modeling_algorithms": self.modeling_algorithms,
            "report_formats": self.report_formats,
            "dashboard_types": self.dashboard_types,
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute R analytics task (data analysis, visualization, modeling, etc.)"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"R Analytics Agent executing: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_analytics_prompt(task, context)
                }
            ]

            # Call Claude API
            response = await self._call_claude_api(messages)

            # Parse response
            result_data = self._parse_response(response)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Create result
            result = TaskResult(
                task_id=self.current_task or "r-analytics-task",
                status=TaskStatus.COMPLETED,
                deliverables=result_data.get("deliverables", []),
                risks_identified=result_data.get("risks_identified", []),
                issues=result_data.get("issues", []),
                next_steps=result_data.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata={
                    "analysis_type": result_data.get("analysis_type"),
                    "num_visualizations": len(result_data.get("visualizations", [])),
                    "num_models": len(result_data.get("models", []))
                }
            )

            self.logger.info(f"R Analytics Agent completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"R Analytics Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "r-analytics-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Analytics task failed: {str(e)}",
                    "resolution": "Check task requirements and data availability"
                }],
                next_steps=["Review error details", "Adjust task parameters", "Retry"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_analytics_prompt(self, task: str, context: TaskContext) -> str:
        """Build analytics prompt for Claude"""
        prompt = f"""## R Analytics & Data Analysis Task

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Previous Outputs**: {json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else "None"}

**Available Analysis Types**: {', '.join(self.analysis_types)}
**Available Visualization Types**: {', '.join(self.visualization_types)}
**Available Modeling Algorithms**: {', '.join(self.modeling_algorithms)}
**Available Report Formats**: {', '.join(self.report_formats)}
**Available Dashboard Types**: {', '.join(self.dashboard_types)}

**Available MCP Tools**: {', '.join(context.mcp_tools_available)}

---

Please complete the R analytics task by:
1. Analyzing task requirements and data characteristics
2. Designing appropriate analysis pipeline
3. Generating R code for data loading and preprocessing
4. Implementing statistical analysis and modeling
5. Creating publication-quality visualizations
6. Generating R Markdown report if requested
7. Building Shiny dashboard if requested
8. Providing validation and performance metrics
9. Suggesting insights and recommendations

Provide your response as valid JSON following the schema in your system prompt.
"""
        return prompt

    async def _call_claude_api(self, messages: List[Dict[str, str]]) -> str:
        """Call Claude API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    system=self.get_system_prompt(),
                    messages=messages
                )
                return response.content[0].text

            except Exception as e:
                self.logger.warning(f"Claude API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay_seconds * (attempt + 1))
                else:
                    raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response"""
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                json_str = response

            return json.loads(json_str)

        except json.JSONDecodeError:
            return {
                "deliverables": [],
                "risks_identified": [],
                "issues": [{
                    "severity": "high",
                    "description": "Failed to parse R Analytics agent response",
                    "resolution": "Retry task with simplified requirements"
                }],
                "next_steps": []
            }
