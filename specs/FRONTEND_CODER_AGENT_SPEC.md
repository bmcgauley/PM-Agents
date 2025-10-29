# Frontend Coder Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Frontend Development (React/Next.js/TypeScript/Supabase)
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The Frontend Coder Agent generates production-ready React/Next.js code with TypeScript, integrated with Supabase for authentication, database, and storage. It follows modern best practices, accessibility standards, and design system patterns.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: Spec-Kit Agent (initialization), Qdrant Vector Agent (context), TypeScript Validator Agent (quality), Reporter Agent (documentation)
- **Primary responsibility**: Frontend code generation, component architecture, UI implementation

### 1.3 Key Responsibilities
1. **Component Development**: Create React components with TypeScript
2. **State Management**: Implement Zustand/Redux state stores
3. **API Integration**: Connect to Supabase and external APIs
4. **Authentication**: Implement Supabase Auth flows
5. **Data Fetching**: Set up React Query/SWR data fetching
6. **Styling**: Apply TailwindCSS and shadcn/ui components
7. **Routing**: Configure Next.js App Router
8. **Accessibility**: Ensure WCAG 2.1 AA compliance

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `FrontendCoderRequest`

```json
{
  "request_id": "string (UUID)",
  "task_type": "component|page|feature|refactor|bugfix",
  "specification": {
    "task_description": "string (natural language)",
    "component_type": "ui|layout|form|data-display|interactive",
    "requirements": {
      "functional": ["string (requirements)", ...],
      "non_functional": ["performance", "accessibility", "responsiveness"]
    },
    "target_path": "string (e.g., 'src/components/auth/LoginForm.tsx')",
    "dependencies": ["component names this depends on", ...]
  },
  "tech_stack": {
    "framework": "nextjs",
    "version": "14.2.0",
    "router_type": "app|pages",
    "language": "typescript",
    "state_management": "zustand|redux|context",
    "data_fetching": "react-query|swr|fetch",
    "styling": "tailwindcss",
    "ui_library": "shadcn/ui|radix-ui|mui|chakra",
    "authentication": "supabase|next-auth|clerk",
    "database": "supabase|prisma|drizzle"
  },
  "design_spec": {
    "figma_url": "string (optional)",
    "design_tokens": {
      "colors": {"primary": "#...", "secondary": "#...", ...},
      "spacing": {"sm": "8px", "md": "16px", ...},
      "typography": {"font_family": "Inter", "sizes": {...}}
    },
    "responsive_breakpoints": ["sm", "md", "lg", "xl", "2xl"]
  },
  "context": {
    "existing_codebase": "boolean",
    "codebase_path": "string (if existing)",
    "related_components": ["string (component paths)", ...],
    "api_schema": "object (if applicable)",
    "user_flow": "string (description of user journey)"
  },
  "quality_requirements": {
    "accessibility": "WCAG 2.1 AA",
    "browser_support": ["chrome", "firefox", "safari", "edge"],
    "mobile_support": "boolean",
    "performance_budget": {
      "lcp": "2.5s",
      "fid": "100ms",
      "cls": "0.1"
    }
  }
}
```

### 2.2 Output Schema: `FrontendCoderResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|partial|failed",
  "execution_time_seconds": "float",
  "deliverables": {
    "files_created": [
      {
        "path": "string (relative path)",
        "type": "component|hook|utility|type|style|test",
        "lines_of_code": "integer",
        "content": "string (file content)"
      }
    ],
    "files_modified": [
      {
        "path": "string",
        "changes": "string (diff or description)",
        "reason": "string"
      }
    ],
    "components_generated": [
      {
        "name": "string (component name)",
        "path": "string",
        "type": "ui|layout|form|data-display|interactive",
        "props": [
          {
            "name": "string",
            "type": "string (TypeScript type)",
            "required": "boolean",
            "description": "string"
          }
        ],
        "exports": ["string (export names)", ...],
        "dependencies": ["string (imported components)", ...]
      }
    ],
    "api_integrations": [
      {
        "endpoint": "string",
        "method": "GET|POST|PUT|DELETE",
        "authentication": "boolean",
        "implementation_path": "string"
      }
    ],
    "state_stores": [
      {
        "name": "string (store name)",
        "path": "string",
        "state_shape": "object (TypeScript interface)",
        "actions": ["string (action names)", ...]
      }
    ]
  },
  "validation": {
    "typescript_valid": "boolean",
    "linting_passed": "boolean",
    "accessibility_score": "float (0.0 - 1.0)",
    "build_succeeds": "boolean",
    "tests_exist": "boolean"
  },
  "metrics": {
    "component_count": "integer",
    "total_lines_of_code": "integer",
    "test_coverage": "float (percentage)",
    "bundle_size_kb": "float (estimated)",
    "generation_time_seconds": "float"
  },
  "documentation": {
    "component_docs": [
      {
        "component_name": "string",
        "usage_example": "string (JSX code example)",
        "props_documentation": "string (markdown)",
        "storybook_story": "string (optional)"
      }
    ],
    "readme_section": "string (markdown to add to README)"
  },
  "next_steps": [
    "string (recommendations)",
    "e.g., 'Add unit tests for LoginForm component'",
    "e.g., 'Configure Supabase environment variables'"
  ],
  "errors": [
    {
      "type": "syntax_error|type_error|import_error|build_error",
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
   - **Usage**: Read existing code, write new components, modify files
   - **Operations**:
     - `read_file`: Read existing components for context
     - `write_file`: Create new component files
     - `edit_file`: Modify existing files
     - `list_directory`: Discover project structure

2. **qdrant** (via Supervisor delegation)
   - **Usage**: Retrieve relevant code patterns and examples
   - **Operations**: Search for similar components, get context

3. **supabase** (Custom MCP Server: `@pm-agents/mcp-supabase`)
   - **Usage**: Query database schema, test authentication, manage storage
   - **Operations**:
     - `get_schema`: Fetch database table schemas
     - `test_auth`: Validate auth configuration
     - `upload_file`: Test storage operations

### 3.2 Optional Tools

1. **github** (MCP Server)
   - **Usage**: Search for code examples in GitHub repositories
   - **Operations**: Search code, get file contents

2. **brave-search** (MCP Server)
   - **Usage**: Look up Next.js/React/Supabase documentation
   - **Operations**: Search for API references, best practices

3. **puppeteer** (MCP Server)
   - **Usage**: Visual regression testing (future enhancement)
   - **Operations**: Screenshot components, test interactions

---

## 4. Algorithms & Workflows

### 4.1 Component Generation Algorithm

```python
def generate_component(request: FrontendCoderRequest) -> FrontendCoderResponse:
    """
    Generate a React component with TypeScript.

    Steps:
    1. Retrieve context from codebase
    2. Design component API (props, state, events)
    3. Generate component implementation
    4. Generate TypeScript types
    5. Generate styles (TailwindCSS)
    6. Generate tests
    7. Validate and build
    8. Return deliverables
    """

    # Step 1: Retrieve Context
    context = retrieve_context(
        task_description=request.specification.task_description,
        related_components=request.context.related_components,
        codebase_path=request.context.codebase_path
    )

    # Step 2: Design Component API
    component_api = design_component_api(
        task_description=request.specification.task_description,
        component_type=request.specification.component_type,
        requirements=request.specification.requirements,
        context=context
    )

    # Step 3: Generate Implementation
    component_code = generate_component_code(
        component_api=component_api,
        tech_stack=request.tech_stack,
        design_spec=request.design_spec,
        context=context
    )

    # Step 4: Generate TypeScript Types
    types_code = generate_types(
        component_api=component_api,
        api_schema=request.context.api_schema
    )

    # Step 5: Generate Styles
    styles_code = generate_styles(
        component_api=component_api,
        design_spec=request.design_spec,
        styling_approach=request.tech_stack.styling
    )

    # Step 6: Generate Tests
    tests_code = generate_tests(
        component_api=component_api,
        component_code=component_code,
        tech_stack=request.tech_stack
    )

    # Step 7: Validate and Build
    validation = validate_code(
        component_code=component_code,
        types_code=types_code,
        tests_code=tests_code,
        target_path=request.specification.target_path,
        quality_requirements=request.quality_requirements
    )

    # Step 8: Return Deliverables
    return create_response(
        status="success" if validation.passed else "partial",
        deliverables={
            "files_created": [
                {"path": component_api.component_path, "content": component_code},
                {"path": component_api.types_path, "content": types_code},
                {"path": component_api.test_path, "content": tests_code}
            ],
            "components_generated": [component_api.to_dict()],
            "validation": validation.to_dict()
        }
    )
```

### 4.2 Component API Design

```python
def design_component_api(
    task_description: str,
    component_type: str,
    requirements: Dict,
    context: Context
) -> ComponentAPI:
    """
    Design the component's API (props, state, events).

    Considerations:
    - Component type (UI, Form, Data Display, etc.)
    - Reusability and composability
    - TypeScript type safety
    - Accessibility requirements
    - Performance requirements
    """

    # Analyze Requirements
    analysis = analyze_requirements(task_description, requirements)

    # Determine Props
    props = []
    for req in analysis.functional_requirements:
        if req.requires_input:
            props.append(PropDefinition(
                name=req.prop_name,
                type=infer_type(req.description),
                required=req.is_required,
                description=req.description,
                default_value=req.default if not req.is_required else None
            ))

    # Determine State
    state_vars = []
    for req in analysis.stateful_requirements:
        state_vars.append(StateDefinition(
            name=req.state_name,
            type=infer_type(req.description),
            initial_value=req.initial_value
        ))

    # Determine Events
    events = []
    for req in analysis.interactive_requirements:
        events.append(EventDefinition(
            name=req.event_name,
            type=infer_event_type(req.description),
            payload_type=infer_payload_type(req.description)
        ))

    # Determine Composition
    children_support = should_support_children(component_type, requirements)
    render_props = identify_render_props(requirements)

    return ComponentAPI(
        name=generate_component_name(task_description),
        props=props,
        state=state_vars,
        events=events,
        children_support=children_support,
        render_props=render_props,
        accessibility=determine_accessibility_props(component_type)
    )
```

### 4.3 Code Generation with Best Practices

```python
def generate_component_code(
    component_api: ComponentAPI,
    tech_stack: TechStack,
    design_spec: DesignSpec,
    context: Context
) -> str:
    """
    Generate React component code following best practices.

    Best Practices Applied:
    - Functional components with hooks
    - TypeScript strict mode
    - Accessibility attributes (ARIA)
    - Error boundaries where appropriate
    - Memoization for performance
    - Proper key props for lists
    - Semantic HTML
    """

    template = get_component_template(tech_stack.framework, tech_stack.ui_library)

    code = template.render(
        component_name=component_api.name,
        props=component_api.props,
        state=component_api.state,
        events=component_api.events,

        # Imports
        imports=generate_imports(component_api, tech_stack),

        # TypeScript interface
        props_interface=generate_props_interface(component_api),

        # Component logic
        hooks=generate_hooks(component_api, tech_stack),
        event_handlers=generate_event_handlers(component_api),

        # JSX
        jsx=generate_jsx(component_api, design_spec, tech_stack),

        # Accessibility
        aria_attributes=generate_aria_attributes(component_api),

        # Exports
        exports=generate_exports(component_api)
    )

    # Apply code formatting
    code = format_code(code, language="typescript")

    return code


# Example Template Rendering
def generate_jsx(
    component_api: ComponentAPI,
    design_spec: DesignSpec,
    tech_stack: TechStack
) -> str:
    """
    Generate JSX with Tailwind classes and accessibility attributes.

    Example Output:
    ```tsx
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 p-6 bg-white rounded-lg shadow-md"
      aria-labelledby="form-title"
    >
      <h2 id="form-title" className="text-2xl font-bold text-gray-900">
        {title}
      </h2>

      <Input
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        aria-required="true"
        aria-invalid={errors.email ? "true" : "false"}
        aria-describedby={errors.email ? "email-error" : undefined}
      />
      {errors.email && (
        <p id="email-error" className="text-sm text-red-600" role="alert">
          {errors.email}
        </p>
      )}

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Submitting..." : "Submit"}
      </Button>
    </form>
    ```
    """

    # Logic to generate JSX based on component type
    if component_api.component_type == "form":
        return generate_form_jsx(component_api, design_spec, tech_stack)
    elif component_api.component_type == "data_display":
        return generate_data_display_jsx(component_api, design_spec, tech_stack)
    elif component_api.component_type == "interactive":
        return generate_interactive_jsx(component_api, design_spec, tech_stack)
    else:
        return generate_generic_jsx(component_api, design_spec, tech_stack)
```

### 4.4 Supabase Integration

```python
def integrate_supabase(
    component_api: ComponentAPI,
    integration_type: str,  # "auth" | "database" | "storage"
    tech_stack: TechStack
) -> SupabaseIntegration:
    """
    Generate Supabase integration code.

    Integration Types:
    - Auth: Sign up, sign in, sign out, password reset
    - Database: CRUD operations with TypeScript types
    - Storage: File upload, download, delete
    """

    if integration_type == "auth":
        return generate_auth_integration(component_api, tech_stack)
    elif integration_type == "database":
        return generate_database_integration(component_api, tech_stack)
    elif integration_type == "storage":
        return generate_storage_integration(component_api, tech_stack)


def generate_auth_integration(
    component_api: ComponentAPI,
    tech_stack: TechStack
) -> AuthIntegration:
    """
    Generate Supabase Auth integration.

    Example Output:
    ```tsx
    // hooks/useAuth.ts
    import { useEffect, useState } from 'react'
    import { User } from '@supabase/supabase-js'
    import { supabase } from '@/lib/supabase'

    export function useAuth() {
      const [user, setUser] = useState<User | null>(null)
      const [loading, setLoading] = useState(true)

      useEffect(() => {
        // Get initial session
        supabase.auth.getSession().then(({ data: { session } }) => {
          setUser(session?.user ?? null)
          setLoading(false)
        })

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
          (_event, session) => {
            setUser(session?.user ?? null)
          }
        )

        return () => subscription.unsubscribe()
      }, [])

      const signIn = async (email: string, password: string) => {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        if (error) throw error
      }

      const signOut = async () => {
        const { error } = await supabase.auth.signOut()
        if (error) throw error
      }

      return { user, loading, signIn, signOut }
    }
    ```
    """

    hook_code = generate_auth_hook(tech_stack.data_fetching)
    provider_code = generate_auth_provider()
    protected_route_code = generate_protected_route()

    return AuthIntegration(
        hook_path="hooks/useAuth.ts",
        hook_code=hook_code,
        provider_path="components/providers/AuthProvider.tsx",
        provider_code=provider_code,
        protected_route_path="components/auth/ProtectedRoute.tsx",
        protected_route_code=protected_route_code
    )


def generate_database_integration(
    component_api: ComponentAPI,
    tech_stack: TechStack
) -> DatabaseIntegration:
    """
    Generate Supabase Database integration with React Query.

    Example Output:
    ```tsx
    // hooks/useTodos.ts
    import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
    import { supabase } from '@/lib/supabase'
    import { Database } from '@/types/supabase'

    type Todo = Database['public']['Tables']['todos']['Row']
    type NewTodo = Database['public']['Tables']['todos']['Insert']

    export function useTodos(userId: string) {
      return useQuery({
        queryKey: ['todos', userId],
        queryFn: async () => {
          const { data, error } = await supabase
            .from('todos')
            .select('*')
            .eq('user_id', userId)
            .order('created_at', { ascending: false })

          if (error) throw error
          return data as Todo[]
        },
      })
    }

    export function useCreateTodo() {
      const queryClient = useQueryClient()

      return useMutation({
        mutationFn: async (newTodo: NewTodo) => {
          const { data, error } = await supabase
            .from('todos')
            .insert(newTodo)
            .select()
            .single()

          if (error) throw error
          return data as Todo
        },
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ['todos'] })
        },
      })
    }
    ```
    """

    # Generate TypeScript types from Supabase schema
    types_code = generate_supabase_types(tech_stack.database)

    # Generate CRUD hooks
    query_hooks = generate_query_hooks(component_api, tech_stack.data_fetching)
    mutation_hooks = generate_mutation_hooks(component_api, tech_stack.data_fetching)

    return DatabaseIntegration(
        types_path="types/supabase.ts",
        types_code=types_code,
        hooks_path=f"hooks/use{component_api.entity_name}.ts",
        hooks_code=query_hooks + mutation_hooks
    )
```

### 4.5 Test Generation

```python
def generate_tests(
    component_api: ComponentAPI,
    component_code: str,
    tech_stack: TechStack
) -> str:
    """
    Generate comprehensive tests for the component.

    Test Categories:
    - Rendering tests
    - Interaction tests
    - Accessibility tests
    - Integration tests (if API calls)
    """

    test_framework = get_test_framework(tech_stack.test_frameworks)

    tests = []

    # Rendering tests
    tests.extend(generate_rendering_tests(component_api))

    # Interaction tests
    tests.extend(generate_interaction_tests(component_api))

    # Accessibility tests
    tests.extend(generate_accessibility_tests(component_api))

    # Integration tests (for API calls)
    if has_api_calls(component_code):
        tests.extend(generate_integration_tests(component_api))

    return test_framework.render_tests(tests)


# Example Test Output (Jest + Testing Library)
"""
// LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { LoginForm } from './LoginForm'
import { supabase } from '@/lib/supabase'

jest.mock('@/lib/supabase')

describe('LoginForm', () => {
  it('renders email and password inputs', () => {
    render(<LoginForm />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('submits form with valid credentials', async () => {
    const mockSignIn = jest.fn().mockResolvedValue({ error: null })
    ;(supabase.auth as jest.Mocked<typeof supabase.auth>).signInWithPassword = mockSignIn

    render(<LoginForm />)

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })
  })

  it('meets accessibility standards', async () => {
    const { container } = render(<LoginForm />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
"""
```

---

## 5. Success Criteria

### 5.1 Functional Requirements
- ✅ Components render without errors
- ✅ All props work as documented
- ✅ Event handlers trigger correctly
- ✅ Supabase integration works (auth, database, storage)
- ✅ State management functions correctly
- ✅ API calls succeed and handle errors

### 5.2 Quality Requirements
- ✅ Zero TypeScript errors
- ✅ ESLint passes with no warnings
- ✅ Prettier formatting applied
- ✅ WCAG 2.1 AA accessibility compliance
- ✅ 80%+ test coverage
- ✅ No console errors or warnings

### 5.3 Performance Requirements
- ✅ LCP (Largest Contentful Paint): <2.5s
- ✅ FID (First Input Delay): <100ms
- ✅ CLS (Cumulative Layout Shift): <0.1
- ✅ Component bundle size: <50KB (uncompressed)
- ✅ Re-renders minimized (React DevTools Profiler)

### 5.4 Integration Requirements
- ✅ Compatible with TypeScript Validator Agent validation
- ✅ Components documented for Reporter Agent
- ✅ Works with existing design system (if applicable)
- ✅ Supabase schema matches database (if applicable)

---

## 6. Error Handling

### 6.1 Error Categories

1. **TypeScript Errors**
   - Type mismatches
   - Missing types
   - Invalid imports
   - **Recovery**: Auto-fix common issues, escalate complex ones

2. **Build Errors**
   - Syntax errors
   - Missing dependencies
   - Configuration issues
   - **Recovery**: Fix syntax, suggest dependency installation

3. **Runtime Errors**
   - API call failures
   - Invalid props
   - State management errors
   - **Recovery**: Add error boundaries, proper error handling

4. **Accessibility Errors**
   - Missing ARIA labels
   - Keyboard navigation issues
   - Color contrast failures
   - **Recovery**: Add accessibility attributes, adjust styles

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: TailwindCSS 3+
- **UI Library**: shadcn/ui (Radix UI primitives)
- **State Management**: Zustand or Redux Toolkit
- **Data Fetching**: React Query or SWR
- **Backend**: Supabase
- **Testing**: Jest + React Testing Library + axe

### 7.2 Design Patterns
- **Composition Pattern**: Build complex UIs from simple components
- **Container/Presentational Pattern**: Separate logic from UI
- **Render Props Pattern**: Flexible component customization
- **Custom Hooks Pattern**: Reusable stateful logic

### 7.3 Dependencies
```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@supabase/supabase-js": "^2.43.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.5.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "latest",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.400.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "eslint": "^8.57.0",
    "prettier": "^3.2.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.3.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@axe-core/react": "^4.9.0"
  }
}
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
- ✅ Component rendering
- ✅ Props validation
- ✅ Event handlers
- ✅ Custom hooks

### 8.2 Integration Tests
- ✅ Supabase auth flows
- ✅ Database CRUD operations
- ✅ File upload/download
- ✅ API integrations

### 8.3 Accessibility Tests
- ✅ axe-core automated tests
- ✅ Keyboard navigation
- ✅ Screen reader compatibility

---

## 9. Future Enhancements

1. **Visual Regression Testing**: Integrate Chromatic or Percy
2. **AI-Powered Styling**: Generate Tailwind classes from design descriptions
3. **Component Playground**: Auto-generate Storybook stories
4. **Performance Optimization**: Automatic code splitting and lazy loading
5. **Internationalization**: Auto-generate i18n translations

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
