# Browser Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Web Automation & Testing (Puppeteer)
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The Browser Agent automates web interactions using Puppeteer. It performs web scraping, visual regression testing, end-to-end testing, accessibility testing, and captures screenshots/PDFs of web applications.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: Frontend Coder Agent (testing), Research Agent (web scraping), TypeScript Validator Agent (E2E testing)
- **Primary responsibility**: Browser automation, E2E testing, visual testing, web scraping

### 1.3 Key Responsibilities
1. **Web Scraping**: Extract data from websites
2. **Screenshot Capture**: Take screenshots of pages/components
3. **PDF Generation**: Generate PDFs from web pages
4. **E2E Testing**: Automate user flows and interactions
5. **Visual Regression Testing**: Compare screenshots for UI changes
6. **Accessibility Testing**: Run axe-core audits in browser
7. **Performance Testing**: Measure page load times, web vitals
8. **Form Automation**: Fill and submit forms programmatically

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `BrowserRequest`

```json
{
  "request_id": "string (UUID)",
  "task_type": "scrape|screenshot|pdf|e2e-test|visual-test|accessibility|performance|form-fill",
  "target": {
    "url": "string (URL to navigate to)",
    "selector": "string (CSS selector, optional)",
    "wait_for": "load|domcontentloaded|networkidle0|networkidle2|selector",
    "timeout_ms": "integer (default: 30000)"
  },
  "browser_config": {
    "headless": "boolean (default: true)",
    "viewport": {
      "width": "integer (default: 1920)",
      "height": "integer (default: 1080)"
    },
    "device_emulation": "desktop|mobile|tablet|custom",
    "user_agent": "string (optional)",
    "authentication": {
      "type": "basic|bearer|cookie",
      "credentials": "object (if needed)"
    }
  },
  "task_config": {
    "scraping": {
      "selectors": {
        "key_name": "string (CSS selector)"
      },
      "extract_type": "text|html|attribute|screenshot",
      "pagination": {
        "enabled": "boolean",
        "max_pages": "integer",
        "next_button_selector": "string"
      }
    },
    "screenshot": {
      "type": "fullpage|viewport|element",
      "format": "png|jpeg|webp",
      "quality": "integer (1-100, for jpeg/webp)",
      "output_path": "string"
    },
    "pdf": {
      "format": "A4|Letter|Legal",
      "print_background": "boolean",
      "margin": {
        "top": "string (e.g., '1cm')",
        "bottom": "string",
        "left": "string",
        "right": "string"
      },
      "output_path": "string"
    },
    "e2e_test": {
      "test_name": "string",
      "steps": [
        {
          "action": "navigate|click|type|select|wait|scroll|hover|screenshot",
          "selector": "string (CSS selector)",
          "value": "string (for type, select actions)",
          "options": "object (action-specific options)"
        }
      ],
      "assertions": [
        {
          "type": "element_exists|text_contains|url_contains|count_equals",
          "selector": "string (optional)",
          "expected": "string|integer"
        }
      ]
    },
    "visual_test": {
      "baseline_path": "string (path to baseline screenshot)",
      "threshold": "float (0.0-1.0, similarity threshold)",
      "ignore_regions": ["string (CSS selectors to ignore)", ...]
    },
    "accessibility": {
      "standard": "wcag2a|wcag2aa|wcag2aaa|section508",
      "rules": ["string (specific axe rules to run)", ...]
    },
    "performance": {
      "metrics": ["fcp", "lcp", "ttfb", "tti", "cls", "fid"],
      "iterations": "integer (default: 3)"
    },
    "form_fill": {
      "fields": [
        {
          "selector": "string (CSS selector)",
          "type": "text|email|password|select|checkbox|radio|file",
          "value": "string"
        }
      ],
      "submit_selector": "string",
      "wait_for_navigation": "boolean"
    }
  }
}
```

### 2.2 Output Schema: `BrowserResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|failed",
  "execution_time_seconds": "float",
  "browser_info": {
    "user_agent": "string",
    "viewport": "object",
    "url": "string (final URL after navigation)"
  },
  "results": {
    "scraped_data": {
      "key_name": "string|array|object (extracted data)"
    },
    "screenshot": {
      "path": "string",
      "size_bytes": "integer",
      "dimensions": {
        "width": "integer",
        "height": "integer"
      }
    },
    "pdf": {
      "path": "string",
      "size_bytes": "integer",
      "num_pages": "integer"
    },
    "e2e_test": {
      "test_name": "string",
      "passed": "boolean",
      "duration_seconds": "float",
      "steps_executed": "integer",
      "steps_passed": "integer",
      "steps_failed": "integer",
      "failed_step_details": [
        {
          "step_index": "integer",
          "action": "string",
          "error_message": "string",
          "screenshot_path": "string"
        }
      ],
      "assertions_passed": "integer",
      "assertions_failed": "integer"
    },
    "visual_test": {
      "similarity_score": "float (0.0-1.0)",
      "passed": "boolean",
      "diff_path": "string (path to diff image)",
      "changed_pixels": "integer",
      "total_pixels": "integer"
    },
    "accessibility": {
      "passed": "boolean",
      "violations": [
        {
          "id": "string",
          "impact": "minor|moderate|serious|critical",
          "description": "string",
          "help_url": "string",
          "nodes": [
            {
              "html": "string",
              "target": "string (CSS selector)"
            }
          ]
        }
      ],
      "violation_count": "integer"
    },
    "performance": {
      "metrics": {
        "fcp": "float (milliseconds)",
        "lcp": "float (milliseconds)",
        "ttfb": "float (milliseconds)",
        "tti": "float (milliseconds)",
        "cls": "float",
        "fid": "float (milliseconds)"
      },
      "average_metrics": "object (if multiple iterations)",
      "lighthouse_score": "float (0-100, if available)"
    },
    "form_fill": {
      "submitted": "boolean",
      "fields_filled": "integer",
      "final_url": "string (after form submission)"
    }
  },
  "console_logs": [
    {
      "type": "log|warn|error",
      "message": "string",
      "timestamp": "string (ISO 8601)"
    }
  ],
  "network_requests": [
    {
      "url": "string",
      "method": "string",
      "status": "integer",
      "response_time_ms": "float"
    }
  ],
  "errors": [
    {
      "type": "navigation_error|timeout_error|selector_error|assertion_error",
      "message": "string",
      "step": "string (optional)"
    }
  ]
}
```

---

## 3. MCP Tools Required

### 3.1 Essential Tools

1. **puppeteer** (MCP Server)
   - **Usage**: All browser automation tasks
   - **Operations**:
     - `puppeteer_navigate`: Navigate to URL
     - `puppeteer_screenshot`: Capture screenshots
     - `puppeteer_click`: Click elements
     - `puppeteer_fill`: Fill form fields
     - `puppeteer_evaluate`: Execute JavaScript in browser

2. **filesystem** (MCP Server)
   - **Usage**: Save screenshots, PDFs, scraped data
   - **Operations**:
     - `write_file`: Save screenshots/PDFs/data
     - `read_file`: Read baseline images for visual testing

---

## 4. Algorithms & Workflows

### 4.1 Web Scraping Workflow

```python
def scrape_website(request: BrowserRequest) -> BrowserResponse:
    """
    Scrape data from website using Puppeteer.

    Steps:
    1. Launch browser
    2. Navigate to URL
    3. Wait for content to load
    4. Extract data using selectors
    5. Handle pagination (if enabled)
    6. Close browser
    7. Return scraped data
    """

    # Step 1: Launch Browser
    browser = launch_browser(
        headless=request.browser_config.headless,
        viewport=request.browser_config.viewport
    )

    page = browser.new_page()

    # Step 2: Navigate
    await page.goto(request.target.url, wait_until=request.target.wait_for)

    # Step 3: Wait for Content
    if request.target.selector:
        await page.wait_for_selector(request.target.selector, timeout=request.target.timeout_ms)

    # Step 4: Extract Data
    scraped_data = {}
    for key, selector in request.task_config.scraping.selectors.items():
        if request.task_config.scraping.extract_type == "text":
            data = await page.evaluate(f"document.querySelector('{selector}').textContent")
        elif request.task_config.scraping.extract_type == "html":
            data = await page.evaluate(f"document.querySelector('{selector}').innerHTML")
        elif request.task_config.scraping.extract_type == "attribute":
            data = await page.evaluate(f"document.querySelector('{selector}').getAttribute('href')")

        scraped_data[key] = data

    # Step 5: Handle Pagination (optional)
    if request.task_config.scraping.pagination.enabled:
        all_data = [scraped_data]
        for page_num in range(1, request.task_config.scraping.pagination.max_pages):
            next_button = request.task_config.scraping.pagination.next_button_selector
            if await page.query_selector(next_button):
                await page.click(next_button)
                await page.wait_for_selector(request.target.selector)

                # Extract data from new page
                page_data = {}
                for key, selector in request.task_config.scraping.selectors.items():
                    data = await page.evaluate(f"document.querySelector('{selector}').textContent")
                    page_data[key] = data

                all_data.append(page_data)
            else:
                break

        scraped_data = all_data

    # Step 6: Close Browser
    await browser.close()

    # Step 7: Return Results
    return create_response(
        status="success",
        results={"scraped_data": scraped_data}
    )
```

### 4.2 E2E Test Execution

```python
def run_e2e_test(request: BrowserRequest) -> BrowserResponse:
    """
    Run end-to-end test with assertions.

    Steps:
    1. Launch browser
    2. Execute test steps sequentially
    3. Capture screenshots on failure
    4. Run assertions
    5. Close browser
    6. Return test results
    """

    browser = launch_browser(request.browser_config)
    page = browser.new_page()

    test_results = E2ETestResult(
        test_name=request.task_config.e2e_test.test_name,
        passed=True,
        steps_executed=0,
        steps_passed=0,
        steps_failed=0,
        failed_step_details=[]
    )

    try:
        # Execute steps
        for step_index, step in enumerate(request.task_config.e2e_test.steps):
            test_results.steps_executed += 1

            try:
                if step.action == "navigate":
                    await page.goto(step.value)
                elif step.action == "click":
                    await page.click(step.selector)
                elif step.action == "type":
                    await page.type(step.selector, step.value)
                elif step.action == "select":
                    await page.select(step.selector, step.value)
                elif step.action == "wait":
                    await page.wait_for_selector(step.selector)
                elif step.action == "scroll":
                    await page.evaluate(f"document.querySelector('{step.selector}').scrollIntoView()")
                elif step.action == "hover":
                    await page.hover(step.selector)
                elif step.action == "screenshot":
                    await page.screenshot(path=step.value)

                test_results.steps_passed += 1

            except Exception as e:
                test_results.steps_failed += 1
                test_results.passed = False

                # Capture failure screenshot
                failure_screenshot = f"failure_step_{step_index}.png"
                await page.screenshot(path=failure_screenshot)

                test_results.failed_step_details.append({
                    "step_index": step_index,
                    "action": step.action,
                    "error_message": str(e),
                    "screenshot_path": failure_screenshot
                })

                break  # Stop on first failure

        # Run assertions
        for assertion in request.task_config.e2e_test.assertions:
            try:
                if assertion.type == "element_exists":
                    element = await page.query_selector(assertion.selector)
                    assert element is not None

                elif assertion.type == "text_contains":
                    text = await page.evaluate(f"document.querySelector('{assertion.selector}').textContent")
                    assert assertion.expected in text

                elif assertion.type == "url_contains":
                    current_url = page.url
                    assert assertion.expected in current_url

                elif assertion.type == "count_equals":
                    count = await page.evaluate(f"document.querySelectorAll('{assertion.selector}').length")
                    assert count == assertion.expected

                test_results.assertions_passed += 1

            except AssertionError:
                test_results.assertions_failed += 1
                test_results.passed = False

    finally:
        await browser.close()

    return create_response(
        status="success",
        results={"e2e_test": test_results}
    )
```

### 4.3 Visual Regression Testing

```python
def run_visual_test(request: BrowserRequest) -> BrowserResponse:
    """
    Compare current screenshot with baseline for visual regressions.

    Steps:
    1. Capture current screenshot
    2. Load baseline screenshot
    3. Compare images pixel-by-pixel
    4. Generate diff image
    5. Calculate similarity score
    6. Return results
    """

    # Step 1: Capture Current Screenshot
    browser = launch_browser(request.browser_config)
    page = browser.new_page()
    await page.goto(request.target.url)

    current_screenshot_path = "current_screenshot.png"
    await page.screenshot(path=current_screenshot_path)

    await browser.close()

    # Step 2: Load Baseline
    baseline_path = request.task_config.visual_test.baseline_path
    baseline_image = Image.open(baseline_path)
    current_image = Image.open(current_screenshot_path)

    # Step 3: Compare Images
    diff_image, changed_pixels = compare_images(
        baseline_image,
        current_image,
        ignore_regions=request.task_config.visual_test.ignore_regions
    )

    # Step 4: Generate Diff Image
    diff_path = "visual_diff.png"
    diff_image.save(diff_path)

    # Step 5: Calculate Similarity
    total_pixels = baseline_image.width * baseline_image.height
    similarity_score = 1.0 - (changed_pixels / total_pixels)

    # Step 6: Return Results
    passed = similarity_score >= request.task_config.visual_test.threshold

    return create_response(
        status="success",
        results={
            "visual_test": {
                "similarity_score": similarity_score,
                "passed": passed,
                "diff_path": diff_path,
                "changed_pixels": changed_pixels,
                "total_pixels": total_pixels
            }
        }
    )
```

---

## 5. Success Criteria

### 5.1 Functional Requirements
- ✅ Navigate to URLs without errors
- ✅ Extract data accurately from selectors
- ✅ Capture high-quality screenshots (300 DPI)
- ✅ E2E tests execute all steps
- ✅ Visual tests detect UI changes
- ✅ Accessibility audits complete

### 5.2 Performance Requirements
- ✅ Navigation completes within timeout
- ✅ Screenshot capture <5 seconds
- ✅ E2E tests run <2 minutes (typical)
- ✅ Visual comparison <10 seconds

### 5.3 Reliability Requirements
- ✅ Graceful handling of timeouts
- ✅ Retry on transient network errors
- ✅ Capture failure screenshots for debugging

---

## 6. Implementation Notes

### 6.1 Technology Stack
- **Browser Automation**: Puppeteer
- **Image Comparison**: Pixelmatch, sharp
- **Accessibility**: axe-core (via Puppeteer)

### 6.2 Dependencies
```json
{
  "puppeteer": "^21.0.0",
  "puppeteer-extra": "^3.3.0",
  "puppeteer-extra-plugin-stealth": "^2.11.0",
  "pixelmatch": "^5.3.0",
  "sharp": "^0.33.0",
  "@axe-core/puppeteer": "^4.8.0"
}
```

### 6.3 Best Practices
- Use `waitForSelector` instead of fixed delays
- Run in headless mode for CI/CD
- Set appropriate timeouts based on network conditions
- Clean up browser instances to avoid memory leaks

---

## 7. Example Use Cases

### 7.1 Screenshot Capture
```json
{
  "task_type": "screenshot",
  "target": {
    "url": "https://example.com",
    "wait_for": "networkidle0"
  },
  "task_config": {
    "screenshot": {
      "type": "fullpage",
      "format": "png",
      "output_path": "screenshots/homepage.png"
    }
  }
}
```

### 7.2 E2E Test (Login Flow)
```json
{
  "task_type": "e2e-test",
  "target": {
    "url": "https://example.com/login"
  },
  "task_config": {
    "e2e_test": {
      "test_name": "User Login Flow",
      "steps": [
        {"action": "type", "selector": "#email", "value": "test@example.com"},
        {"action": "type", "selector": "#password", "value": "password123"},
        {"action": "click", "selector": "button[type='submit']"},
        {"action": "wait", "selector": ".dashboard"}
      ],
      "assertions": [
        {"type": "url_contains", "expected": "/dashboard"},
        {"type": "element_exists", "selector": ".user-profile"}
      ]
    }
  }
}
```

---

## 8. Future Enhancements

1. **Parallel Execution**: Run multiple browser instances concurrently
2. **Video Recording**: Record test execution videos
3. **Network Throttling**: Simulate slow connections
4. **Geolocation Spoofing**: Test location-based features
5. **PDF Text Extraction**: Extract and search PDF content

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
