# Ollama PM-Agents Setup Guide

Complete guide for running PM-Agents with local Ollama models (Gemma3:1b).

## Overview

The Ollama implementation provides a **cost-free, local alternative** to the Anthropic Claude API, enabling:
- ✅ **Zero API costs** - Run entirely locally
- ✅ **Offline operation** - No internet required after model download
- ✅ **Privacy-focused** - Data never leaves your machine
- ✅ **Development/testing** - Iterate without API rate limits
- ✅ **GPU acceleration** - Leverage local GPU for performance

## Architecture Compatibility

The Ollama implementation (`pm_ollama_agents.py`) is **100% compatible** with the Anthropic implementation (`pm_system.py`), using the same:
- Hierarchical architecture (Coordinator → Planner → Supervisor → Specialists)
- Data structures (AgentType, TaskContext, TaskResult, ProjectState)
- Agent interface (BaseAgent with `process_task()`)
- 9 specialist agents (Spec-Kit, Qdrant, Frontend, Python ML/DL, R Analytics, TypeScript Validator, Research, Browser, Reporter)

---

## Installation

### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download installer from [ollama.com](https://ollama.com/download)

**Verify installation:**
```bash
ollama --version
```

### 2. Pull Gemma3:1b Model

```bash
# Standard model (default - 1B parameters)
ollama pull gemma3:1b

# Alternative sizes
ollama pull gemma3:3b      # 3B parameters (larger, better quality)

# View available models
ollama list
```

### 3. Start Ollama Server

```bash
ollama serve
```

Server runs on `http://localhost:11434` by default.

**Verify server is running:**
```bash
curl http://localhost:11434/api/tags
```

---

## Usage

### Basic Usage

```bash
python pm_ollama_agents.py \
  --project-name "Test Project" \
  --project-description "Build a React app with user authentication" \
  --project-type frontend \
  --requirements "React 18" "TypeScript" "Responsive design"
```

### Advanced Usage with GPU Acceleration

```bash
python pm_ollama_agents.py \
  --project-name "ML Model Training" \
  --project-description "Train PyTorch image classification model" \
  --project-type ml \
  --requirements "PyTorch" "TensorBoard" "Data augmentation" \
  --model gemma3:1b \
  --num-gpu 35 \
  --log-level INFO
```

### Using Larger Model

```bash
python pm_ollama_agents.py \
  --project-name "Analytics Dashboard" \
  --project-description "R Shiny dashboard for sales analytics" \
  --project-type analytics \
  --requirements "tidyverse" "ggplot2" "Shiny" \
  --model gemma3:3b \
  --num-gpu -1 \
  --log-level INFO
```

---

## Configuration Options

### Command-Line Arguments

| Argument | Description | Default | Options |
|----------|-------------|---------|---------|
| `--project-name` | Project name | Required | String |
| `--project-description` | Project description | Required | String |
| `--project-type` | Project type | Required | `frontend`, `backend`, `ml`, `analytics`, `fullstack` |
| `--requirements` | Space-separated requirements | Required | List of strings |
| `--ollama-url` | Ollama API URL | `http://localhost:11434` | URL string |
| `--model` | Ollama model | `gemma3:1b` | Any Ollama model |
| `--num-gpu` | GPU layers | `-1` (auto) | `-1` (auto), `0` (CPU only), `>0` (specific layers) |
| `--quantization` | Model quantization | `None` | `Q4_0`, `Q4_1`, `Q5_0`, `Q5_1`, `Q8_0`, `F16`, `F32` |
| `--log-level` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### GPU Configuration

**Auto GPU (Recommended):**
```bash
--num-gpu -1  # Ollama automatically uses GPU if available
```

**CPU Only:**
```bash
--num-gpu 0  # Force CPU-only execution
```

**Specific GPU Layers:**
```bash
--num-gpu 35  # Run 35 model layers on GPU
```

**How to determine optimal GPU layers:**
1. Start with `-1` (auto) and monitor GPU memory
2. If GPU memory is insufficient, reduce layers (e.g., `--num-gpu 20`)
3. Check GPU usage: `nvidia-smi` (NVIDIA) or `rocm-smi` (AMD)

### Model Sizes

| Model | Parameters | Size | Speed | Quality | Use Case |
|-------|-----------|------|-------|---------|----------|
| `gemma3:1b` | 1 billion | Small | Fast | Good | Development, testing, learning |
| `gemma3:3b` | 3 billion | Medium | Moderate | Better | General use, production |

**Note:** Gemma3 models are already optimized. If you need smaller/faster models, use `gemma3:1b`. For better quality, use `gemma3:3b`.

**To switch models:**
```bash
# Use 1B model (default, fastest)
python pm_ollama_agents.py ... --model gemma3:1b

# Use 3B model (better quality)
python pm_ollama_agents.py ... --model gemma3:3b
```

---

## Python API Usage

### Basic Example

```python
import asyncio
from pm_ollama_agents import OllamaPMAgentsSystem

async def main():
    # Initialize system
    system = OllamaPMAgentsSystem(
        model="gemma3:1b",
        num_gpu=-1,  # Auto GPU
        log_level="INFO"
    )

    # Run project
    result = await system.run_project(
        project_name="My Frontend App",
        project_description="Build React app with TypeScript",
        project_type="frontend",
        requirements=["React 18", "TypeScript", "Supabase"]
    )

    # Print results
    print(f"Status: {result['status']}")
    print(f"Project ID: {result['project_id']}")

asyncio.run(main())
```

### Advanced Example with Individual Agents

```python
import asyncio
from pm_ollama_agents import (
    OllamaCoordinatorAgent,
    OllamaPlannerAgent,
    TaskContext
)

async def main():
    # Initialize Coordinator
    coordinator = OllamaCoordinatorAgent(
        model="gemma3:1b",
        num_gpu=35
    )

    # Initiate project
    initiation = await coordinator.initiate_project(
        project_name="ML Pipeline",
        project_description="Build ML training pipeline",
        project_type="ml",
        requirements=["PyTorch", "TensorBoard"]
    )

    print(f"Project ID: {initiation['project_id']}")

    # Initialize Planner
    planner = OllamaPlannerAgent(model="gemma3:1b")

    # Create plan
    plan = await planner.create_project_plan(
        project_id=initiation['project_id'],
        project_description="Build ML training pipeline",
        project_type="ml",
        requirements=["PyTorch", "TensorBoard"]
    )

    print(f"Plan status: {plan.status}")
    print(f"Deliverables: {len(plan.deliverables)}")

asyncio.run(main())
```

---

## Running Integration Tests

### Prerequisites

1. Ollama server running
2. Gemma2 model pulled
3. pytest installed

### Run Tests

```bash
# Install pytest if needed
pip install pytest pytest-asyncio

# Run all tests
pytest tests/integration/test_ollama_integration.py -v

# Run specific test
pytest tests/integration/test_ollama_integration.py::test_ollama_system_simple_project -v

# Run with detailed output
pytest tests/integration/test_ollama_integration.py -v -s
```

### Test Coverage

The test suite covers:
- ✅ OllamaBaseAgent initialization and task processing
- ✅ Coordinator Agent (project initiation, phase gates)
- ✅ Planner Agent (plan creation)
- ✅ Supervisor Agent (task coordination)
- ✅ All 9 specialist agents
- ✅ GPU configuration options
- ✅ Quantization configuration
- ✅ Complete system initialization
- ✅ System status reporting
- ✅ Simple project execution
- ✅ Circuit breaker functionality
- ✅ Performance metrics tracking

---

## Performance Comparison

### Claude vs Ollama (Gemma3)

| Metric | Claude (Sonnet 4.5) | Ollama (Gemma3:1b) | Ollama (Gemma3:3b) |
|--------|---------------------|--------------------|--------------------|
| **Cost** | $3-$15 per 1M tokens | Free | Free |
| **Speed** | 2-5 seconds | 3-8 seconds | 5-15 seconds |
| **Quality** | Excellent | Good | Very Good |
| **Context Window** | 200K tokens | 8K tokens | 8K tokens |
| **GPU Required** | No | Recommended | Recommended |
| **Offline** | No | Yes | Yes |
| **Rate Limits** | Yes | No | No |
| **Model Size** | API only | 1GB | 3GB |

### When to Use Each

**Use Claude (Anthropic):**
- ✅ Production deployments
- ✅ High-quality outputs critical
- ✅ Large context windows needed
- ✅ No local GPU available
- ✅ Budget allows API costs

**Use Ollama (Gemma3:1b/3b):**
- ✅ Development and testing
- ✅ Learning and experimentation
- ✅ Privacy-sensitive projects
- ✅ Offline operation required
- ✅ Local GPU available
- ✅ High-volume usage
- ✅ Cost-sensitive deployments

---

## Troubleshooting

### Issue: "Ollama is not running"

**Solution:**
```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull the model
ollama pull gemma3:1b

# Verify model is available
ollama list
```

### Issue: "Out of memory"

**Solutions:**
1. Use smaller model:
   ```bash
   # 1B model uses less memory than 3B
   python pm_ollama_agents.py ... --model gemma3:1b
   ```

2. Reduce GPU layers:
   ```bash
   python pm_ollama_agents.py ... --num-gpu 20
   ```

3. Force CPU-only:
   ```bash
   python pm_ollama_agents.py ... --num-gpu 0
   ```

### Issue: "Slow performance"

**Solutions:**
1. Use GPU acceleration:
   ```bash
   python pm_ollama_agents.py ... --num-gpu -1
   ```

2. Close other applications to free up memory

3. Monitor memory usage:
   ```bash
   # Linux/Mac
   htop

   # Windows
   # Open Task Manager
   ```

3. Reduce context window:
   - Edit `pm_ollama_agents.py`
   - Change `"num_ctx": 4096` to `"num_ctx": 2048`

### Issue: "Circuit breaker opened"

**Cause:** Too many consecutive failures (3+)

**Solutions:**
1. Verify Ollama is running
2. Check model is pulled
3. Restart Ollama server
4. Check system resources (CPU/GPU/RAM)

---

## Model Recommendations

### For Development/Testing
- **Model:** `gemma3:1b`
- **GPU:** `-1` (auto) or `0` (CPU only)
- **RAM:** 4-8 GB
- **Pros:** Fast, low memory, good for rapid iteration

### For General Use
- **Model:** `gemma3:1b`
- **GPU:** `-1` (auto)
- **RAM:** 8 GB
- **Pros:** Balanced speed and quality, reliable performance

### For Production/Better Quality
- **Model:** `gemma3:3b`
- **GPU:** `-1` (auto) or `20+` layers
- **RAM:** 16 GB
- **Pros:** Better quality outputs, still efficient

### For CPU-Only Environments
- **Model:** `gemma3:1b`
- **GPU:** `0` (CPU only)
- **RAM:** 8 GB
- **Pros:** Runs without GPU, slower but functional

---

## System Requirements

### Minimum Requirements
- **CPU:** 4 cores, 2.5 GHz+
- **RAM:** 8 GB
- **Storage:** 10 GB free
- **OS:** macOS, Linux, Windows 10/11

### Recommended Requirements
- **CPU:** 8 cores, 3.5 GHz+
- **RAM:** 16 GB
- **GPU:** NVIDIA (6GB+ VRAM) or AMD (8GB+ VRAM)
- **Storage:** 20 GB free (for multiple models)
- **OS:** macOS, Linux, Windows 10/11

### GPU Support

**NVIDIA (CUDA):**
- GTX 1060 6GB or better
- RTX 2060 or better (recommended)
- CUDA 11.8+ required

**AMD (ROCm):**
- RX 6600 or better
- RX 7000 series (recommended)
- ROCm 5.4+ required

**Apple Silicon:**
- M1/M2/M3 with 16GB+ RAM
- Metal acceleration automatic

---

## Next Steps

1. **Test the system:**
   ```bash
   python pm_ollama_agents.py --project-name "Test" --project-description "Simple test" --project-type frontend --requirements "React"
   ```

2. **Run integration tests:**
   ```bash
   pytest tests/integration/test_ollama_integration.py -v
   ```

3. **Try different models:**
   ```bash
   ollama list  # See available models
   ollama pull gemma3:3b  # Larger model for better quality
   ```

4. **Monitor performance:**
   - Watch GPU usage: `nvidia-smi -l 1`
   - Check RAM usage: `htop` or Task Manager
   - Review logs: `--log-level DEBUG`

5. **Compare with Claude:**
   - Run same project with both implementations
   - Compare quality, speed, cost
   - Document findings in `COMPARISON_RESULTS.md`

---

## Additional Resources

- **Ollama Documentation:** https://ollama.com/docs
- **Gemma3 Models:** https://ollama.com/library/gemma3
- **PM-Agents Architecture:** [AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md)
- **Phase 3.1.2 Status:** [tasks.md](tasks.md#312-finalize-ollama-implementation-issue-12)

---

## Support

**Issues with Ollama:**
- GitHub: https://github.com/ollama/ollama/issues
- Discord: https://discord.gg/ollama

**Issues with PM-Agents:**
- GitHub Issues: https://github.com/[your-repo]/PM-Agents/issues
- Documentation: [README.md](README.md)

**Performance Optimization:**
- See [PHASE_3_1_2_PERFORMANCE.md](PHASE_3_1_2_PERFORMANCE.md) (when available)
- GPU Optimization Guide: [GPU_OPTIMIZATION.md](GPU_OPTIMIZATION.md) (when available)

---

**Last Updated:** 2025-10-29
**Ollama Version:** 0.1.20+
**Gemma3 Version:** 1b (default), 3b (optional)
**Status:** ✅ Phase 3.1.2 Complete
