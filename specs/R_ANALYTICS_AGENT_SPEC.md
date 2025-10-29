# R Analytics Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Data Analytics & Visualization (R/tidyverse)
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The R Analytics Agent generates R code for data analysis, statistical modeling, and interactive visualizations. It uses tidyverse for data manipulation, ggplot2 for visualizations, R Markdown for reports, and Shiny for interactive dashboards.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: Spec-Kit Agent (initialization), Qdrant Vector Agent (context), Reporter Agent (documentation)
- **Primary responsibility**: Data analytics, statistical analysis, dashboard creation

### 1.3 Key Responsibilities
1. **Data Wrangling**: Process and transform data using tidyverse (dplyr, tidyr)
2. **Statistical Analysis**: Perform statistical tests and modeling (lm, glm, tidymodels)
3. **Visualization**: Create publication-quality plots with ggplot2
4. **Reporting**: Generate R Markdown reports with reproducible analysis
5. **Interactive Dashboards**: Build Shiny apps for data exploration
6. **Predictive Modeling**: Implement machine learning pipelines with tidymodels/caret

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `RAnalyticsRequest`

```json
{
  "request_id": "string (UUID)",
  "task_type": "analysis|visualization|report|dashboard|model",
  "analytics_task": {
    "objective": "string (natural language description)",
    "analysis_type": "exploratory|inferential|predictive|descriptive",
    "dataset_info": {
      "data_path": "string (CSV, Excel, RDS, database connection)",
      "data_format": "csv|excel|rds|sql|parquet",
      "num_rows": "integer (optional)",
      "num_columns": "integer (optional)",
      "column_types": {
        "column_name": "numeric|character|factor|date|logical"
      }
    },
    "research_questions": [
      "string (questions to answer)",
      "e.g., 'Is there a correlation between X and Y?'",
      "e.g., 'What factors predict customer churn?'"
    ],
    "target_variable": "string (for predictive modeling)",
    "predictor_variables": ["string (variable names)", ...]
  },
  "visualization_spec": {
    "plot_types": ["scatter|line|bar|boxplot|histogram|heatmap|violin", ...],
    "color_palette": "viridis|brewer|custom",
    "theme": "minimal|classic|bw|light|dark",
    "faceting": "boolean",
    "interactive": "boolean (plotly conversion)"
  },
  "report_config": {
    "format": "html|pdf|word|github_document",
    "title": "string",
    "author": "string",
    "output_path": "string",
    "include_code": "boolean",
    "include_plots": "boolean",
    "include_tables": "boolean"
  },
  "dashboard_config": {
    "dashboard_type": "shiny|flexdashboard|shinydashboard",
    "layout": "sidebar|tabs|navbar|fillPage",
    "reactive_elements": ["filter", "plot", "table", "metric"],
    "deployment_target": "shinyapps.io|rstudio_connect|local"
  },
  "modeling_config": {
    "algorithm": "linear_regression|logistic_regression|random_forest|xgboost|glm|gam",
    "cross_validation": {
      "method": "k-fold|stratified|time-series",
      "folds": "integer"
    },
    "hyperparameter_tuning": "boolean",
    "feature_engineering": ["scaling", "encoding", "interaction_terms"],
    "metrics": ["rmse", "mae", "r-squared", "accuracy", "auc", "f1"]
  },
  "context": {
    "existing_codebase": "boolean",
    "codebase_path": "string (if existing)",
    "style_guide": "tidyverse|google|custom"
  }
}
```

### 2.2 Output Schema: `RAnalyticsResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|partial|failed",
  "execution_time_seconds": "float",
  "deliverables": {
    "files_created": [
      {
        "path": "string (relative path)",
        "type": "script|notebook|report|dashboard|data",
        "lines_of_code": "integer",
        "content": "string (file content)"
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
          "n": "integer",
          "missing": "integer"
        }
      },
      "statistical_tests": [
        {
          "test_name": "string (e.g., 't-test', 'ANOVA', 'chi-squared')",
          "statistic": "float",
          "p_value": "float",
          "df": "integer",
          "interpretation": "string"
        }
      ],
      "correlations": {
        "var1_var2": "float (-1 to 1)"
      }
    },
    "visualizations": [
      {
        "plot_name": "string",
        "plot_type": "string",
        "file_path": "string (PNG, PDF, SVG)",
        "description": "string"
      }
    ],
    "models": [
      {
        "model_name": "string",
        "algorithm": "string",
        "performance": {
          "metric_name": "float"
        },
        "feature_importance": {
          "variable_name": "float (importance score)"
        },
        "model_path": "string (RDS file)"
      }
    ],
    "reports": [
      {
        "report_path": "string",
        "format": "html|pdf|word",
        "num_pages": "integer",
        "sections": ["string (section titles)", ...]
      }
    ],
    "dashboards": [
      {
        "dashboard_path": "string",
        "type": "shiny|flexdashboard",
        "run_command": "string (how to launch)",
        "url": "string (if deployed)"
      }
    ]
  },
  "validation": {
    "code_runs": "boolean",
    "plots_generated": "boolean",
    "report_compiles": "boolean",
    "dashboard_launches": "boolean",
    "models_converge": "boolean",
    "tests_pass": "boolean"
  },
  "insights": [
    "string (key findings)",
    "e.g., 'Strong positive correlation (r=0.85) between age and salary'",
    "e.g., 'Random Forest model achieves 92% accuracy'"
  ],
  "recommendations": [
    "string (actionable suggestions)",
    "e.g., 'Consider adding interaction terms between X and Z'",
    "e.g., 'Model shows signs of overfitting, reduce complexity'"
  ],
  "next_steps": [
    "string (follow-up actions)",
    "e.g., 'Run report: Rscript -e \"rmarkdown::render('analysis.Rmd')\"'",
    "e.g., 'Launch dashboard: shiny::runApp('dashboard/')'"
  ],
  "errors": [
    {
      "type": "data_error|syntax_error|modeling_error|rendering_error",
      "message": "string",
      "file": "string",
      "line": "integer",
      "severity": "critical|warning|info"
    }
  ]
}
```

---

## 3. MCP Tools Required

### 3.1 Essential Tools

1. **filesystem** (MCP Server)
   - **Usage**: Read data files, write R scripts, save plots
   - **Operations**:
     - `read_file`: Read CSV, Excel, data files
     - `write_file`: Create R scripts, save plots
     - `list_directory`: Discover data files

2. **qdrant** (via Supervisor delegation)
   - **Usage**: Retrieve R code patterns and examples
   - **Operations**: Search for similar analysis pipelines

### 3.2 Optional Tools

1. **github** (MCP Server)
   - **Usage**: Search for R package examples
   - **Operations**: Search code, get file contents

2. **brave-search** (MCP Server)
   - **Usage**: Look up R documentation, statistical methods
   - **Operations**: Search for API references, best practices

---

## 4. Algorithms & Workflows

### 4.1 Data Analysis Pipeline

```python
def generate_analysis(request: RAnalyticsRequest) -> RAnalyticsResponse:
    """
    Generate R code for data analysis.

    Steps:
    1. Retrieve context and examples
    2. Design analysis pipeline
    3. Generate data loading code
    4. Generate data wrangling code
    5. Generate statistical analysis code
    6. Generate visualizations
    7. Generate report (if requested)
    8. Validate and test
    9. Return deliverables
    """

    # Step 1: Retrieve Context
    context = retrieve_context(
        analytics_task=request.analytics_task,
        codebase_path=request.context.codebase_path
    )

    # Step 2: Design Pipeline
    pipeline = design_analysis_pipeline(
        analytics_task=request.analytics_task,
        context=context
    )

    # Step 3: Generate Data Loading
    data_loading_code = generate_data_loading(
        dataset_info=request.analytics_task.dataset_info
    )

    # Step 4: Generate Data Wrangling
    wrangling_code = generate_data_wrangling(
        dataset_info=request.analytics_task.dataset_info,
        analysis_type=request.analytics_task.analysis_type
    )

    # Step 5: Generate Statistical Analysis
    analysis_code = generate_statistical_analysis(
        analytics_task=request.analytics_task,
        modeling_config=request.modeling_config
    )

    # Step 6: Generate Visualizations
    visualization_code = generate_visualizations(
        analytics_task=request.analytics_task,
        visualization_spec=request.visualization_spec
    )

    # Step 7: Generate Report (optional)
    report_code = None
    if request.report_config:
        report_code = generate_rmarkdown_report(
            analytics_task=request.analytics_task,
            report_config=request.report_config,
            analysis_code=analysis_code,
            visualization_code=visualization_code
        )

    # Step 8: Validate
    validation = validate_r_code(
        data_loading_code=data_loading_code,
        wrangling_code=wrangling_code,
        analysis_code=analysis_code,
        visualization_code=visualization_code
    )

    # Step 9: Return Deliverables
    return create_response(
        status="success" if validation.passed else "partial",
        deliverables={
            "files_created": [
                {"path": "scripts/data_loading.R", "content": data_loading_code},
                {"path": "scripts/analysis.R", "content": analysis_code},
                {"path": "scripts/visualization.R", "content": visualization_code}
            ]
        }
    )
```

### 4.2 Code Generation Examples

```python
def generate_data_wrangling(
    dataset_info: DatasetInfo,
    analysis_type: str
) -> str:
    """
    Generate tidyverse data wrangling code.

    Example Output:
    ```r
    library(tidyverse)

    # Load data
    data <- read_csv("data/sales.csv")

    # Data cleaning and transformation
    data_clean <- data %>%
      # Remove missing values
      drop_na() %>%

      # Create new variables
      mutate(
        revenue = quantity * price,
        month = lubridate::month(date, label = TRUE),
        quarter = lubridate::quarter(date)
      ) %>%

      # Filter outliers
      filter(revenue < quantile(revenue, 0.99)) %>%

      # Group and summarize
      group_by(product_category, month) %>%
      summarize(
        total_revenue = sum(revenue),
        avg_price = mean(price),
        num_transactions = n(),
        .groups = "drop"
      ) %>%

      # Sort results
      arrange(desc(total_revenue))

    # View summary
    glimpse(data_clean)
    summary(data_clean)
    ```
    """

    template = get_tidyverse_template()

    code = template.render(
        data_path=dataset_info.data_path,
        data_format=dataset_info.data_format,
        analysis_type=analysis_type,
        column_types=dataset_info.column_types
    )

    return format_r_code(code)


def generate_visualizations(
    analytics_task: AnalyticsTask,
    visualization_spec: VisualizationSpec
) -> str:
    """
    Generate ggplot2 visualization code.

    Example Output:
    ```r
    library(ggplot2)
    library(ggthemes)

    # Set theme
    theme_set(theme_minimal())

    # 1. Scatter plot with trend line
    p1 <- ggplot(data_clean, aes(x = age, y = salary, color = department)) +
      geom_point(alpha = 0.6, size = 2) +
      geom_smooth(method = "lm", se = TRUE) +
      scale_color_viridis_d() +
      labs(
        title = "Relationship between Age and Salary",
        subtitle = "Colored by department",
        x = "Age (years)",
        y = "Salary ($)",
        color = "Department"
      ) +
      theme(
        plot.title = element_text(size = 14, face = "bold"),
        legend.position = "bottom"
      )

    # Save plot
    ggsave("plots/scatter_age_salary.png", p1, width = 10, height = 6, dpi = 300)

    # 2. Distribution with boxplot
    p2 <- ggplot(data_clean, aes(x = department, y = salary, fill = department)) +
      geom_boxplot(alpha = 0.7, outlier.color = "red") +
      geom_jitter(width = 0.2, alpha = 0.2) +
      scale_fill_brewer(palette = "Set2") +
      labs(
        title = "Salary Distribution by Department",
        x = "Department",
        y = "Salary ($)",
        fill = "Department"
      ) +
      coord_flip() +
      theme(legend.position = "none")

    ggsave("plots/boxplot_salary_dept.png", p2, width = 10, height = 6, dpi = 300)

    # 3. Time series plot
    p3 <- ggplot(data_clean, aes(x = month, y = total_revenue, group = product_category, color = product_category)) +
      geom_line(size = 1.2) +
      geom_point(size = 2) +
      scale_y_continuous(labels = scales::dollar) +
      scale_color_viridis_d() +
      labs(
        title = "Monthly Revenue by Product Category",
        x = "Month",
        y = "Total Revenue",
        color = "Product Category"
      ) +
      theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "bottom"
      )

    ggsave("plots/timeseries_revenue.png", p3, width = 12, height = 6, dpi = 300)
    ```
    """

    template = get_ggplot2_template()

    code = template.render(
        plot_types=visualization_spec.plot_types,
        color_palette=visualization_spec.color_palette,
        theme=visualization_spec.theme,
        faceting=visualization_spec.faceting,
        research_questions=analytics_task.research_questions
    )

    return format_r_code(code)


def generate_statistical_analysis(
    analytics_task: AnalyticsTask,
    modeling_config: ModelingConfig
) -> str:
    """
    Generate statistical analysis code.

    Example Output:
    ```r
    library(tidyverse)
    library(broom)

    # 1. Descriptive Statistics
    summary_stats <- data_clean %>%
      select(age, salary, years_experience) %>%
      summarize(
        across(
          everything(),
          list(
            mean = ~mean(.x, na.rm = TRUE),
            median = ~median(.x, na.rm = TRUE),
            sd = ~sd(.x, na.rm = TRUE),
            min = ~min(.x, na.rm = TRUE),
            max = ~max(.x, na.rm = TRUE)
          ),
          .names = "{.col}_{.fn}"
        )
      )

    print(summary_stats)

    # 2. Correlation Analysis
    cor_matrix <- data_clean %>%
      select(age, salary, years_experience) %>%
      cor(use = "complete.obs")

    print(cor_matrix)

    # Correlation test
    cor_test_result <- cor.test(data_clean$age, data_clean$salary)
    print(cor_test_result)

    # 3. Linear Regression
    model_lm <- lm(salary ~ age + years_experience + department, data = data_clean)
    summary(model_lm)

    # Model diagnostics
    par(mfrow = c(2, 2))
    plot(model_lm)

    # Tidy model output
    model_tidy <- tidy(model_lm, conf.int = TRUE)
    model_glance <- glance(model_lm)

    print(model_tidy)
    print(model_glance)

    # 4. ANOVA
    anova_result <- aov(salary ~ department, data = data_clean)
    summary(anova_result)

    # Post-hoc test
    TukeyHSD(anova_result)

    # 5. Save results
    write_csv(summary_stats, "results/summary_statistics.csv")
    write_csv(model_tidy, "results/regression_results.csv")
    saveRDS(model_lm, "models/linear_model.rds")
    ```
    """

    template = get_statistical_analysis_template()

    code = template.render(
        analysis_type=analytics_task.analysis_type,
        research_questions=analytics_task.research_questions,
        target_variable=analytics_task.target_variable,
        predictor_variables=analytics_task.predictor_variables,
        algorithm=modeling_config.algorithm if modeling_config else None
    )

    return format_r_code(code)


def generate_rmarkdown_report(
    analytics_task: AnalyticsTask,
    report_config: ReportConfig,
    analysis_code: str,
    visualization_code: str
) -> str:
    """
    Generate R Markdown report.

    Example Output:
    ```rmarkdown
    ---
    title: "Sales Analysis Report"
    author: "Data Science Team"
    date: "`r Sys.Date()`"
    output:
      html_document:
        toc: true
        toc_float: true
        code_folding: hide
        theme: flatly
    ---

    ```{r setup, include=FALSE}
    knitr::opts_chunk$set(
      echo = TRUE,
      message = FALSE,
      warning = FALSE,
      fig.width = 10,
      fig.height = 6,
      dpi = 300
    )
    ```

    ## Executive Summary

    This report presents an analysis of sales data to answer the following research questions:

    - Is there a relationship between product category and revenue?
    - What are the seasonal trends in sales?
    - Which factors predict customer purchase behavior?

    ## Data

    ```{r load-data}
    library(tidyverse)
    library(ggplot2)

    data <- read_csv("data/sales.csv")
    glimpse(data)
    ```

    ### Data Quality

    ```{r data-quality}
    # Check missing values
    missing_summary <- data %>%
      summarize(across(everything(), ~sum(is.na(.)))) %>%
      pivot_longer(everything(), names_to = "variable", values_to = "missing_count")

    knitr::kable(missing_summary, caption = "Missing Values by Variable")
    ```

    ## Analysis

    ### Descriptive Statistics

    ```{r descriptive-stats}
    summary_stats <- data %>%
      select(age, salary, purchase_amount) %>%
      summarize(across(
        everything(),
        list(mean = mean, median = median, sd = sd, min = min, max = max),
        .names = "{.col}_{.fn}"
      ))

    knitr::kable(summary_stats, caption = "Summary Statistics")
    ```

    ### Visualizations

    ```{r plot-revenue}
    ggplot(data, aes(x = product_category, y = revenue, fill = product_category)) +
      geom_boxplot() +
      scale_fill_viridis_d() +
      labs(title = "Revenue Distribution by Product Category",
           x = "Product Category", y = "Revenue ($)") +
      theme_minimal() +
      theme(legend.position = "none")
    ```

    ### Statistical Tests

    ```{r statistical-tests}
    # ANOVA
    anova_result <- aov(revenue ~ product_category, data = data)
    summary(anova_result)

    # Post-hoc test
    TukeyHSD(anova_result)
    ```

    ## Predictive Modeling

    ```{r modeling}
    library(tidymodels)

    # Split data
    set.seed(123)
    data_split <- initial_split(data, prop = 0.8, strata = purchased)
    train_data <- training(data_split)
    test_data <- testing(data_split)

    # Create recipe
    recipe <- recipe(purchased ~ age + salary + product_category, data = train_data) %>%
      step_normalize(all_numeric_predictors()) %>%
      step_dummy(all_nominal_predictors())

    # Define model
    model_spec <- logistic_reg() %>%
      set_engine("glm")

    # Create workflow
    workflow <- workflow() %>%
      add_recipe(recipe) %>%
      add_model(model_spec)

    # Fit model
    model_fit <- workflow %>%
      fit(data = train_data)

    # Evaluate
    predictions <- model_fit %>%
      predict(test_data) %>%
      bind_cols(test_data)

    # Metrics
    metrics <- predictions %>%
      metrics(truth = purchased, estimate = .pred_class)

    knitr::kable(metrics, caption = "Model Performance Metrics")
    ```

    ## Conclusions

    1. Strong relationship between product category and revenue (F = XX, p < 0.001)
    2. Seasonal trends show peak sales in Q4
    3. Logistic regression model achieves 85% accuracy in predicting purchases

    ## Recommendations

    1. Focus marketing efforts on high-revenue categories
    2. Prepare inventory for Q4 demand spike
    3. Deploy predictive model to identify high-value customers
    ```
    """

    template = get_rmarkdown_template()

    code = template.render(
        title=report_config.title,
        author=report_config.author,
        output_format=report_config.format,
        include_code=report_config.include_code,
        research_questions=analytics_task.research_questions,
        analysis_code=analysis_code,
        visualization_code=visualization_code
    )

    return code


def generate_shiny_dashboard(
    analytics_task: AnalyticsTask,
    dashboard_config: DashboardConfig
) -> str:
    """
    Generate Shiny dashboard code.

    Example Output: See implementation for full Shiny app structure
    """

    template = get_shiny_template(dashboard_config.dashboard_type)

    code = template.render(
        layout=dashboard_config.layout,
        reactive_elements=dashboard_config.reactive_elements,
        research_questions=analytics_task.research_questions
    )

    return code
```

---

## 5. Success Criteria

### 5.1 Functional Requirements
- ✅ Data loads without errors
- ✅ Analysis produces expected outputs
- ✅ Plots render correctly
- ✅ Reports compile to target format
- ✅ Dashboards launch and are interactive
- ✅ Models converge and produce predictions

### 5.2 Quality Requirements
- ✅ Code follows tidyverse style guide
- ✅ All functions documented
- ✅ Plots publication-quality (300 DPI)
- ✅ Statistical tests appropriately chosen
- ✅ Reports well-formatted with clear narrative

### 5.3 Performance Requirements
- ✅ Analysis completes in reasonable time (<5 min for typical datasets)
- ✅ Dashboards responsive (<1s interaction delay)
- ✅ Plots render quickly (<2s)

---

## 6. Implementation Notes

### 6.1 Technology Stack
- **Core**: R 4.x
- **Data Manipulation**: tidyverse (dplyr, tidyr, readr, purrr)
- **Visualization**: ggplot2, plotly
- **Modeling**: tidymodels, caret
- **Reporting**: R Markdown, knitr
- **Dashboards**: Shiny, flexdashboard

### 6.2 Dependencies
```r
dependencies <- c(
  "tidyverse",
  "ggplot2",
  "plotly",
  "tidymodels",
  "caret",
  "rmarkdown",
  "knitr",
  "shiny",
  "flexdashboard",
  "broom",
  "scales",
  "viridis",
  "ggthemes"
)
```

---

## 7. Testing Strategy

### 7.1 Unit Tests (testthat)
- ✅ Data loading functions
- ✅ Data transformation functions
- ✅ Statistical test helpers

### 7.2 Integration Tests
- ✅ Full analysis pipeline
- ✅ Report compilation
- ✅ Dashboard launch

---

## 8. Future Enhancements

1. **Interactive Plots**: More plotly integration
2. **Advanced Modeling**: Deep learning with keras/tensorflow
3. **Big Data**: sparklyr integration
4. **Real-time Dashboards**: Streaming data support
5. **Automated Reporting**: Scheduled report generation

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
