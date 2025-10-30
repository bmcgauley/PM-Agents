# Ollama PM-Agents Setup Guide

Complete guide for running PM-Agents with local Ollama models (Gemma2/Gemma3).

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

### 2. Pull Gemma2 Model

```bash
# Standard model (default)
ollama pull gemma2:latest

# Quantized models (faster, less memory)
ollama pull gemma2:Q4_0    # 4-bit quantization
ollama pull gemma2:Q8_0    # 8-bit quantization

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
  --model gemma2:latest \
  --num-gpu 35 \
  --log-level INFO
```

### Using Quantized Models

```bash
python pm_ollama_agents.py \
  --project-name "Analytics Dashboard" \
  --project-description "R Shiny dashboard for sales analytics" \
  --project-type analytics \
  --requirements "tidyverse" "ggplot2" "Shiny" \
  --model gemma2:Q4_0 \
  --num-gpu 0 \
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
| `--model` | Ollama model | `gemma2:latest` | Any Ollama model |
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

### Quantization Options

| Format | Size | Speed | Quality | Use Case |
|--------|------|-------|---------|----------|
| `Q4_0` | Smallest | Fastest | Lower | Development/testing |
| `Q4_1` | Small | Fast | Moderate | General use |
| `Q5_0` | Medium | Moderate | Good | Balanced |
| `Q8_0` | Large | Slower | High | Production |
| `F16` | Larger | Slow | Very high | High-quality outputs |
| `F32` | Largest | Slowest | Best | Maximum quality |

**To use quantized models:**
```bash
# Pull quantized model
ollama pull gemma2:Q4_0

# Use in command
python pm_ollama_agents.py ... --model gemma2:Q4_0
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
        model="gemma2:latest",
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
        model="gemma2:latest",
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
    planner = OllamaPlannerAgent(model="gemma2:latest")

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

### Claude vs Ollama (Gemma2)

| Metric | Claude (Sonnet 4.5) | Ollama (Gemma2) | Ollama (Gemma2 Q4_0) |
|--------|---------------------|-----------------|----------------------|
| **Cost** | $3-$15 per 1M tokens | Free | Free |
| **Speed** | 2-5 seconds | 5-15 seconds | 3-8 seconds |
| **Quality** | Excellent | Good | Moderate |
| **Context Window** | 200K tokens | 4K-8K tokens | 4K-8K tokens |
| **GPU Required** | No | Recommended | Recommended |
| **Offline** | No | Yes | Yes |
| **Rate Limits** | Yes | No | No |

### When to Use Each

**Use Claude (Anthropic):**
- ✅ Production deployments
- ✅ High-quality outputs critical
- ✅ Large context windows needed
- ✅ No local GPU available
- ✅ Budget allows API costs

**Use Ollama (Gemma2):**
- ✅ Development and testing
- ✅ Learning and experimentation
- ✅ Privacy-sensitive projects
- ✅ Offline operation required
- ✅ Local GPU available
- ✅ High-volume usage

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
ollama pull gemma2:latest

# Verify model is available
ollama list
```

### Issue: "Out of memory"

**Solutions:**
1. Use quantized model:
   ```bash
   ollama pull gemma2:Q4_0
   python pm_ollama_agents.py ... --model gemma2:Q4_0
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

2. Use smaller quantization:
   ```bash
   ollama pull gemma2:Q4_0
   python pm_ollama_agents.py ... --model gemma2:Q4_0
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
- **Model:** `gemma2:Q4_0`
- **GPU:** `-1` (auto) or `0` (CPU only)
- **Pros:** Fast, low memory, good enough for testing

### For General Use
- **Model:** `gemma2:latest`
- **GPU:** `-1` (auto)
- **Pros:** Balanced speed and quality

### For Production-Like Quality
- **Model:** `gemma2:Q8_0`
- **GPU:** `35+` layers
- **Pros:** High quality, good speed with GPU

### For Maximum Quality
- **Model:** `gemma2:F16`
- **GPU:** `40+` layers
- **Pros:** Best quality, requires significant resources

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
   ollama pull gemma3  # When available
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
- **Gemma Models:** https://ollama.com/library/gemma2
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
**Gemma2 Version:** latest
**Status:** ✅ Phase 3.1.2 Complete
