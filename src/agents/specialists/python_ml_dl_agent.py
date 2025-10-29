"""
Python ML/DL Agent - Machine Learning & Deep Learning Specialist
Generates PyTorch models, training pipelines, and Jupyter notebooks
Based on PYTHON_ML_DL_AGENT_SPEC.md
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


class PythonMLDLAgent(BaseAgent):
    """
    Python ML/DL Agent - Machine Learning & Deep Learning specialist

    Responsibilities:
    - Generate PyTorch model architectures
    - Create training pipelines with validation and checkpointing
    - Implement data loading and preprocessing pipelines
    - Set up TensorBoard experiment tracking
    - Generate Jupyter notebooks for exploration
    - Validate and test model implementations

    Uses filesystem and tensorboard MCP servers
    """

    def __init__(
        self,
        agent_id: str = "python-ml-dl-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Python ML/DL Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.PYTHON_ML_DL,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers required by ML/DL agent
        self.required_mcp_servers = ["filesystem", "tensorboard"]

        # Supported ML task types
        self.ml_task_types = [
            "classification", "regression", "detection",
            "segmentation", "generation", "nlp"
        ]

        # Supported model architectures
        self.model_architectures = {
            "resnet": "ResNet (Image Classification)",
            "vit": "Vision Transformer (Image Classification)",
            "bert": "BERT (NLP)",
            "gpt": "GPT (Language Models)",
            "unet": "U-Net (Segmentation)",
            "yolo": "YOLO (Object Detection)",
            "custom": "Custom Architecture"
        }

        self.logger.info("Python ML/DL Agent initialized with supported architectures")

    def get_system_prompt(self) -> str:
        """Get ML/DL-specific system prompt"""
        return """You are the Python ML/DL Agent, a machine learning and deep learning specialist in the PM-Agents system.

**Your Role**:
- Design and implement PyTorch model architectures
- Create training pipelines with validation, early stopping, and checkpointing
- Implement data loading and preprocessing pipelines
- Set up TensorBoard for experiment tracking and visualization
- Generate Jupyter notebooks for exploration and documentation
- Validate models and provide performance recommendations

**Core Responsibilities**:
1. **Model Architecture**: Design PyTorch models (ResNet, ViT, BERT, U-Net, YOLO, custom)
2. **Training Pipeline**: Implement training loops with optimizers, schedulers, loss functions
3. **Data Pipeline**: Create DataLoaders with augmentation and normalization
4. **Experiment Tracking**: Configure TensorBoard logging and checkpointing
5. **Evaluation**: Generate metrics, performance reports, and recommendations
6. **Validation**: Test forward/backward passes, training loops, and TensorBoard logging
7. **Documentation**: Create Jupyter notebooks and usage instructions

**Supported ML Tasks**:
- Classification (image, text, tabular)
- Regression (continuous prediction)
- Object Detection (localization + classification)
- Segmentation (pixel-level classification)
- Generation (VAE, GAN, Diffusion)
- NLP (text classification, sequence models)

**Model Architectures**:
- ResNet, EfficientNet (Image Classification)
- Vision Transformer (ViT) - Images and patches
- BERT, GPT, T5 (NLP)
- U-Net (Segmentation)
- YOLO, Faster R-CNN (Detection)
- Custom architectures based on requirements

**Technology Stack**:
- PyTorch 2.0+ (nn.Module, autograd)
- TensorBoard (SummaryWriter, metrics logging)
- torchvision (pretrained models, transforms)
- torchtext/transformers (NLP)
- Jupyter/JupyterLab (notebooks)
- NumPy, Pandas, scikit-learn (data handling)

**Output Format**: Always provide structured JSON with:
```json
{
  "deliverables": [
    {
      "type": "model|training|data|notebook|config",
      "name": "string",
      "path": "relative/path/to/file",
      "content": "file content or description"
    }
  ],
  "model_info": {
    "architecture": "string (e.g., ResNet50)",
    "num_parameters": "integer",
    "num_trainable_parameters": "integer",
    "input_shape": "tuple",
    "output_shape": "tuple"
  },
  "training_info": {
    "optimizer": "string (e.g., AdamW)",
    "learning_rate": "float",
    "batch_size": "integer",
    "num_epochs": "integer",
    "early_stopping": "boolean"
  },
  "tensorboard_config": {
    "enabled": "boolean",
    "log_dir": "string",
    "launch_command": "string"
  },
  "validation": {
    "model_loads": "boolean",
    "forward_pass_works": "boolean",
    "backward_pass_works": "boolean",
    "training_loop_runs": "boolean"
  },
  "metrics": {
    "model_size_mb": "float",
    "estimated_training_time_hours": "float",
    "estimated_inference_time_ms": "float"
  },
  "recommendations": ["string", ...],
  "next_steps": ["string", ...]
}
```

**Best Practices**:
- Use type hints (torch.Tensor, nn.Module)
- Write comprehensive docstrings
- Implement proper device handling (CPU/GPU)
- Use gradient clipping for stability
- Include early stopping and checkpointing
- Log metrics to TensorBoard at appropriate frequencies
- Provide reproducible results (set seeds)
- Test forward/backward passes before training
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return Python ML/DL capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "pytorch_modeling",
                "model_training",
                "data_pipelines",
                "experiment_tracking",
                "jupyter_notebooks",
                "model_validation",
                "hyperparameter_optimization"
            ],
            "ml_task_types": self.ml_task_types,
            "model_architectures": list(self.model_architectures.keys()),
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute ML/DL task (model generation, training pipeline, etc.)"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Python ML/DL Agent executing: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_ml_prompt(task, context)
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
                task_id=self.current_task or "python-ml-dl-task",
                status=TaskStatus.COMPLETED,
                deliverables=result_data.get("deliverables", []),
                risks_identified=result_data.get("risks_identified", []),
                issues=result_data.get("issues", []),
                next_steps=result_data.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata={
                    "model_architecture": result_data.get("model_info", {}).get("architecture"),
                    "ml_task": result_data.get("ml_task_type"),
                    "tensorboard_enabled": result_data.get("tensorboard_config", {}).get("enabled")
                }
            )

            self.logger.info(f"Python ML/DL Agent completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Python ML/DL Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "python-ml-dl-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"ML/DL task failed: {str(e)}",
                    "resolution": "Check task requirements and available resources"
                }],
                next_steps=["Review error details", "Adjust task parameters", "Retry"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_ml_prompt(self, task: str, context: TaskContext) -> str:
        """Build ML/DL prompt for Claude"""
        prompt = f"""## Machine Learning/Deep Learning Task

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Previous Outputs**: {json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else "None"}

**Available ML Architectures**: {', '.join(self.model_architectures.keys())}

**Available MCP Tools**: {', '.join(context.mcp_tools_available)}

---

Please complete the ML/DL task by:
1. Analyzing requirements and selecting appropriate architecture
2. Generating model code with proper structure and type hints
3. Creating training pipeline with optimizer, scheduler, loss function
4. Implementing data loading and preprocessing
5. Setting up TensorBoard logging configuration
6. Generating Jupyter notebook examples
7. Providing validation and performance estimates
8. Suggesting next steps and improvements

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
                    "description": "Failed to parse ML/DL agent response",
                    "resolution": "Retry task with simplified requirements"
                }],
                "next_steps": []
            }
