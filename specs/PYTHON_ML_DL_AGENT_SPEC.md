# Python ML/DL Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Machine Learning & Deep Learning (PyTorch)
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The Python ML/DL Agent generates PyTorch models, training pipelines, and Jupyter notebooks for machine learning and deep learning projects. It integrates TensorBoard for experiment tracking and follows ML engineering best practices.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: Spec-Kit Agent (initialization), Qdrant Vector Agent (context), TypeScript Validator Agent (Python validation), Reporter Agent (documentation)
- **Primary responsibility**: ML model development, training pipelines, experiment tracking

### 1.3 Key Responsibilities
1. **Model Architecture**: Design and implement PyTorch model architectures
2. **Training Pipelines**: Create training loops with validation and checkpointing
3. **Data Processing**: Implement data loading and preprocessing pipelines
4. **Experiment Tracking**: Integrate TensorBoard for metrics and visualizations
5. **Hyperparameter Tuning**: Implement hyperparameter search strategies
6. **Model Evaluation**: Generate evaluation metrics and performance reports
7. **Deployment Preparation**: Export models for inference (ONNX, TorchScript)
8. **Notebook Generation**: Create Jupyter notebooks for exploration and documentation

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `PythonMLDLRequest`

```json
{
  "request_id": "string (UUID)",
  "task_type": "model|training|evaluation|deployment|notebook",
  "ml_task": {
    "type": "classification|regression|detection|segmentation|generation|nlp",
    "problem_description": "string (natural language)",
    "dataset_info": {
      "dataset_name": "string",
      "dataset_path": "string (local or URL)",
      "input_shape": "tuple (e.g., [3, 224, 224] for images)",
      "output_shape": "tuple or integer (num_classes)",
      "num_samples": "integer",
      "train_val_test_split": "[0.7, 0.15, 0.15]"
    },
    "performance_requirements": {
      "target_metric": "accuracy|f1|mse|iou|bleu",
      "target_value": "float (e.g., 0.95 for 95% accuracy)",
      "max_training_time_hours": "float",
      "max_inference_time_ms": "float"
    }
  },
  "model_config": {
    "architecture": "resnet|vit|bert|gpt|unet|custom",
    "pretrained": "boolean",
    "pretrained_source": "torchvision|huggingface|custom",
    "backbone": "string (if applicable)",
    "num_layers": "integer",
    "hidden_dim": "integer",
    "dropout": "float",
    "activation": "relu|gelu|silu|tanh"
  },
  "training_config": {
    "optimizer": "adam|adamw|sgd|lion",
    "learning_rate": "float",
    "lr_scheduler": "cosine|step|exponential|plateau",
    "batch_size": "integer",
    "num_epochs": "integer",
    "early_stopping": {
      "enabled": "boolean",
      "patience": "integer",
      "min_delta": "float"
    },
    "gradient_clipping": "float (optional)",
    "mixed_precision": "boolean",
    "distributed": "boolean"
  },
  "data_config": {
    "data_loader": "torch|huggingface|custom",
    "augmentation": ["string (augmentation names)", ...],
    "normalization": {
      "mean": "[float, ...]",
      "std": "[float, ...]"
    },
    "preprocessing": ["resize", "crop", "tokenize", ...]
  },
  "experiment_config": {
    "tensorboard_enabled": "boolean",
    "tensorboard_log_dir": "string",
    "checkpoint_dir": "string",
    "save_frequency": "integer (epochs)",
    "wandb_enabled": "boolean",
    "wandb_project": "string (optional)"
  },
  "context": {
    "existing_codebase": "boolean",
    "codebase_path": "string (if existing)",
    "baseline_model": "string (path or name)",
    "compute_resources": {
      "gpus": "integer",
      "memory_gb": "float",
      "cpu_cores": "integer"
    }
  }
}
```

### 2.2 Output Schema: `PythonMLDLResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|partial|failed",
  "execution_time_seconds": "float",
  "deliverables": {
    "files_created": [
      {
        "path": "string (relative path)",
        "type": "model|training|data|utils|config|notebook",
        "lines_of_code": "integer",
        "content": "string (file content)"
      }
    ],
    "model_architecture": {
      "name": "string",
      "path": "string",
      "num_parameters": "integer",
      "num_trainable_parameters": "integer",
      "input_shape": "tuple",
      "output_shape": "tuple",
      "model_summary": "string (torchinfo output)"
    },
    "training_pipeline": {
      "training_script_path": "string",
      "data_loader_path": "string",
      "config_path": "string",
      "supports_distributed": "boolean",
      "supports_mixed_precision": "boolean"
    },
    "experiment_tracking": {
      "tensorboard_log_dir": "string",
      "tensorboard_command": "string (how to launch TensorBoard)",
      "metrics_tracked": ["loss", "accuracy", "learning_rate", ...],
      "checkpoints_dir": "string"
    },
    "notebooks": [
      {
        "path": "string",
        "purpose": "exploration|training|evaluation|visualization",
        "description": "string"
      }
    ]
  },
  "validation": {
    "model_loads": "boolean",
    "forward_pass_works": "boolean",
    "backward_pass_works": "boolean",
    "training_loop_runs": "boolean",
    "tensorboard_logs_generated": "boolean",
    "tests_pass": "boolean"
  },
  "metrics": {
    "model_size_mb": "float",
    "estimated_training_time_hours": "float",
    "estimated_inference_time_ms": "float",
    "memory_usage_gb": "float",
    "flops": "integer"
  },
  "performance_report": {
    "baseline_metric": "float (if baseline provided)",
    "expected_metric": "float (based on architecture)",
    "convergence_estimate": "string (fast|medium|slow)",
    "recommendations": ["string (optimization suggestions)", ...]
  },
  "next_steps": [
    "string (actionable recommendations)",
    "e.g., 'Run training script: python train.py --config config.yaml'",
    "e.g., 'Launch TensorBoard: tensorboard --logdir logs/'"
  ],
  "errors": [
    {
      "type": "model_error|data_error|training_error|validation_error",
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
   - **Usage**: Read/write model code, notebooks, data
   - **Operations**:
     - `read_file`: Read existing models, data
     - `write_file`: Create model files, training scripts
     - `list_directory`: Discover project structure

2. **qdrant** (via Supervisor delegation)
   - **Usage**: Retrieve ML code patterns and examples
   - **Operations**: Search for similar model architectures

3. **tensorboard** (Background Service, NOT MCP)
   - **Usage**: Experiment tracking and visualization
   - **Launch**: `tensorboard --logdir logs/`

### 3.2 Optional Tools

1. **github** (MCP Server)
   - **Usage**: Search for model implementations, pretrained weights
   - **Operations**: Search code, get file contents

2. **brave-search** (MCP Server)
   - **Usage**: Look up PyTorch documentation, research papers
   - **Operations**: Search for API references, best practices

---

## 4. Algorithms & Workflows

### 4.1 Model Generation Algorithm

```python
def generate_model(request: PythonMLDLRequest) -> PythonMLDLResponse:
    """
    Generate a PyTorch model and training pipeline.

    Steps:
    1. Retrieve context from codebase and research
    2. Design model architecture
    3. Generate model implementation
    4. Generate data loading pipeline
    5. Generate training loop
    6. Generate evaluation code
    7. Set up TensorBoard logging
    8. Validate and test
    9. Return deliverables
    """

    # Step 1: Retrieve Context
    context = retrieve_context(
        ml_task=request.ml_task,
        model_config=request.model_config,
        codebase_path=request.context.codebase_path
    )

    # Step 2: Design Architecture
    architecture = design_model_architecture(
        ml_task=request.ml_task,
        model_config=request.model_config,
        context=context
    )

    # Step 3: Generate Model Implementation
    model_code = generate_model_code(
        architecture=architecture,
        model_config=request.model_config
    )

    # Step 4: Generate Data Pipeline
    data_code = generate_data_pipeline(
        dataset_info=request.ml_task.dataset_info,
        data_config=request.data_config
    )

    # Step 5: Generate Training Loop
    training_code = generate_training_loop(
        architecture=architecture,
        training_config=request.training_config,
        experiment_config=request.experiment_config
    )

    # Step 6: Generate Evaluation Code
    evaluation_code = generate_evaluation_code(
        architecture=architecture,
        ml_task=request.ml_task
    )

    # Step 7: Set Up TensorBoard
    tensorboard_config = setup_tensorboard(
        experiment_config=request.experiment_config
    )

    # Step 8: Validate and Test
    validation = validate_pipeline(
        model_code=model_code,
        data_code=data_code,
        training_code=training_code,
        dataset_info=request.ml_task.dataset_info
    )

    # Step 9: Return Deliverables
    return create_response(
        status="success" if validation.passed else "partial",
        deliverables={
            "files_created": [
                {"path": "models/model.py", "content": model_code},
                {"path": "data/dataloader.py", "content": data_code},
                {"path": "train.py", "content": training_code},
                {"path": "evaluate.py", "content": evaluation_code}
            ],
            "model_architecture": architecture.to_dict(),
            "experiment_tracking": tensorboard_config.to_dict(),
            "validation": validation.to_dict()
        }
    )
```

### 4.2 Architecture Design

```python
def design_model_architecture(
    ml_task: MLTask,
    model_config: ModelConfig,
    context: Context
) -> ModelArchitecture:
    """
    Design PyTorch model architecture based on task and requirements.

    Architecture Selection Strategy:
    - Classification (images): ResNet, ViT, EfficientNet
    - Object Detection: YOLO, Faster R-CNN, DETR
    - Segmentation: U-Net, DeepLab, Mask R-CNN
    - NLP: BERT, GPT, T5
    - Generation: VAE, GAN, Diffusion

    Considerations:
    - Dataset size (pretrained vs. from scratch)
    - Compute resources (model size)
    - Inference time requirements
    - Accuracy requirements
    """

    # Select base architecture
    if model_config.architecture == "custom":
        base_arch = design_custom_architecture(ml_task, model_config)
    else:
        base_arch = get_pretrained_architecture(
            model_config.architecture,
            model_config.pretrained_source
        )

    # Customize for task
    if ml_task.type == "classification":
        # Add classification head
        base_arch.add_head(
            nn.Linear(base_arch.feature_dim, ml_task.dataset_info.output_shape)
        )
    elif ml_task.type == "detection":
        # Add detection heads
        base_arch.add_detection_heads(ml_task.dataset_info.output_shape)
    elif ml_task.type == "segmentation":
        # Add decoder
        base_arch.add_decoder(ml_task.dataset_info.output_shape)

    # Calculate model statistics
    num_params = sum(p.numel() for p in base_arch.parameters())
    num_trainable = sum(p.numel() for p in base_arch.parameters() if p.requires_grad)

    return ModelArchitecture(
        name=generate_model_name(ml_task, model_config),
        base_architecture=base_arch,
        num_parameters=num_params,
        num_trainable_parameters=num_trainable,
        input_shape=ml_task.dataset_info.input_shape,
        output_shape=ml_task.dataset_info.output_shape,
        pretrained=model_config.pretrained
    )
```

### 4.3 Model Code Generation

```python
def generate_model_code(
    architecture: ModelArchitecture,
    model_config: ModelConfig
) -> str:
    """
    Generate PyTorch model code.

    Example Output:
    ```python
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torchvision.models import resnet50, ResNet50_Weights

    class ImageClassifier(nn.Module):
        '''
        Image classification model based on ResNet50.

        Args:
            num_classes (int): Number of output classes
            pretrained (bool): Use pretrained weights from ImageNet
            dropout (float): Dropout probability
        '''

        def __init__(
            self,
            num_classes: int = 1000,
            pretrained: bool = True,
            dropout: float = 0.5
        ):
            super().__init__()

            # Load pretrained ResNet50
            if pretrained:
                self.backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
            else:
                self.backbone = resnet50(weights=None)

            # Replace final fully connected layer
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()  # Remove original FC

            # Add custom classification head
            self.classifier = nn.Sequential(
                nn.Dropout(p=dropout),
                nn.Linear(num_features, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(p=dropout),
                nn.Linear(512, num_classes)
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            '''
            Forward pass.

            Args:
                x (torch.Tensor): Input tensor of shape (batch_size, 3, 224, 224)

            Returns:
                torch.Tensor: Logits of shape (batch_size, num_classes)
            '''
            features = self.backbone(x)
            logits = self.classifier(features)
            return logits

        def get_num_parameters(self) -> int:
            '''Get total number of parameters.'''
            return sum(p.numel() for p in self.parameters())

        def freeze_backbone(self):
            '''Freeze backbone for fine-tuning.'''
            for param in self.backbone.parameters():
                param.requires_grad = False

        def unfreeze_backbone(self):
            '''Unfreeze backbone for full training.'''
            for param in self.backbone.parameters():
                param.requires_grad = True
    ```
    """

    template = get_model_template(architecture.base_architecture)

    code = template.render(
        model_name=architecture.name,
        base_architecture=architecture.base_architecture,
        num_classes=architecture.output_shape,
        pretrained=architecture.pretrained,
        dropout=model_config.dropout,
        activation=model_config.activation,
        input_shape=architecture.input_shape
    )

    return format_python_code(code)
```

### 4.4 Training Loop Generation

```python
def generate_training_loop(
    architecture: ModelArchitecture,
    training_config: TrainingConfig,
    experiment_config: ExperimentConfig
) -> str:
    """
    Generate training script with TensorBoard integration.

    Example Output:
    ```python
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader
    from torch.utils.tensorboard import SummaryWriter
    from tqdm import tqdm
    import os

    from models.model import ImageClassifier
    from data.dataloader import get_dataloaders

    def train_one_epoch(
        model: nn.Module,
        train_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        device: torch.device,
        epoch: int,
        writer: SummaryWriter
    ) -> float:
        '''Train for one epoch.'''

        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1} [Train]')
        for batch_idx, (inputs, targets) in enumerate(pbar):
            inputs, targets = inputs.to(device), targets.to(device)

            # Forward pass
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            # Backward pass
            loss.backward()
            optimizer.step()

            # Metrics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

            # Update progress bar
            pbar.set_postfix({
                'loss': running_loss / (batch_idx + 1),
                'acc': 100. * correct / total
            })

            # TensorBoard logging (every 100 batches)
            if batch_idx % 100 == 0:
                global_step = epoch * len(train_loader) + batch_idx
                writer.add_scalar('train/loss', loss.item(), global_step)
                writer.add_scalar('train/accuracy', 100. * correct / total, global_step)

        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total

        return epoch_loss, epoch_acc

    def validate(
        model: nn.Module,
        val_loader: DataLoader,
        criterion: nn.Module,
        device: torch.device
    ) -> tuple[float, float]:
        '''Validate the model.'''

        model.eval()
        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, targets in tqdm(val_loader, desc='Validation'):
                inputs, targets = inputs.to(device), targets.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, targets)

                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()

        val_loss = running_loss / len(val_loader)
        val_acc = 100. * correct / total

        return val_loss, val_acc

    def train(
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        scheduler: torch.optim.lr_scheduler._LRScheduler,
        criterion: nn.Module,
        device: torch.device,
        num_epochs: int,
        checkpoint_dir: str,
        log_dir: str
    ):
        '''Full training loop with checkpointing and TensorBoard logging.'''

        # Create directories
        os.makedirs(checkpoint_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        # TensorBoard writer
        writer = SummaryWriter(log_dir)

        # Early stopping
        best_val_loss = float('inf')
        patience_counter = 0
        patience = 5

        for epoch in range(num_epochs):
            # Train
            train_loss, train_acc = train_one_epoch(
                model, train_loader, optimizer, criterion, device, epoch, writer
            )

            # Validate
            val_loss, val_acc = validate(model, val_loader, criterion, device)

            # TensorBoard logging
            writer.add_scalar('epoch/train_loss', train_loss, epoch)
            writer.add_scalar('epoch/train_accuracy', train_acc, epoch)
            writer.add_scalar('epoch/val_loss', val_loss, epoch)
            writer.add_scalar('epoch/val_accuracy', val_acc, epoch)
            writer.add_scalar('epoch/learning_rate', optimizer.param_groups[0]['lr'], epoch)

            # Learning rate scheduling
            scheduler.step()

            # Checkpointing
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0

                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_loss': val_loss,
                    'val_accuracy': val_acc
                }
                torch.save(checkpoint, os.path.join(checkpoint_dir, 'best_model.pt'))
                print(f'Saved best model (val_loss: {val_loss:.4f})')
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f'Early stopping triggered after {epoch+1} epochs')
                    break

        writer.close()
        print('Training complete!')

    if __name__ == '__main__':
        # Device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f'Using device: {device}')

        # Data
        train_loader, val_loader, test_loader = get_dataloaders(
            batch_size=32,
            num_workers=4
        )

        # Model
        model = ImageClassifier(num_classes=10, pretrained=True, dropout=0.5)
        model = model.to(device)

        # Optimizer and scheduler
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

        # Loss
        criterion = nn.CrossEntropyLoss()

        # Train
        train(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer=optimizer,
            scheduler=scheduler,
            criterion=criterion,
            device=device,
            num_epochs=100,
            checkpoint_dir='checkpoints/',
            log_dir='logs/'
        )
    ```
    """

    template = get_training_template(training_config.optimizer)

    code = template.render(
        model_name=architecture.name,
        optimizer=training_config.optimizer,
        learning_rate=training_config.learning_rate,
        lr_scheduler=training_config.lr_scheduler,
        batch_size=training_config.batch_size,
        num_epochs=training_config.num_epochs,
        early_stopping=training_config.early_stopping,
        gradient_clipping=training_config.gradient_clipping,
        mixed_precision=training_config.mixed_precision,
        tensorboard_enabled=experiment_config.tensorboard_enabled,
        tensorboard_log_dir=experiment_config.tensorboard_log_dir,
        checkpoint_dir=experiment_config.checkpoint_dir
    )

    return format_python_code(code)
```

### 4.5 TensorBoard Integration

```python
def setup_tensorboard(experiment_config: ExperimentConfig) -> TensorBoardConfig:
    """
    Set up TensorBoard logging.

    Metrics to Track:
    - Training loss (per batch and per epoch)
    - Validation loss (per epoch)
    - Training accuracy (per batch and per epoch)
    - Validation accuracy (per epoch)
    - Learning rate (per epoch)
    - Gradient norms (per batch, optional)
    - Model weights histograms (per epoch, optional)
    """

    if not experiment_config.tensorboard_enabled:
        return TensorBoardConfig(enabled=False)

    log_dir = experiment_config.tensorboard_log_dir or "logs/"

    # TensorBoard launch command
    launch_command = f"tensorboard --logdir {log_dir}"

    return TensorBoardConfig(
        enabled=True,
        log_dir=log_dir,
        launch_command=launch_command,
        metrics_tracked=[
            "train/loss",
            "train/accuracy",
            "epoch/train_loss",
            "epoch/train_accuracy",
            "epoch/val_loss",
            "epoch/val_accuracy",
            "epoch/learning_rate"
        ]
    )
```

---

## 5. Success Criteria

### 5.1 Functional Requirements
- ✅ Model initializes without errors
- ✅ Forward pass produces correct output shape
- ✅ Backward pass updates gradients
- ✅ Training loop runs for multiple epochs
- ✅ Checkpointing saves and loads models
- ✅ TensorBoard logs metrics correctly

### 5.2 Quality Requirements
- ✅ Code follows PyTorch best practices
- ✅ Type hints for all functions
- ✅ Docstrings for all classes and methods
- ✅ No memory leaks (validated with profiling)
- ✅ Reproducible results (seed setting)

### 5.3 Performance Requirements
- ✅ Training uses GPU efficiently (>80% utilization)
- ✅ Data loading not bottlenecked (<10% idle time)
- ✅ Model converges within expected epochs
- ✅ Inference time meets requirements

### 5.4 Integration Requirements
- ✅ Compatible with TypeScript Validator Agent (Python linting)
- ✅ TensorBoard accessible via browser
- ✅ Models exportable to ONNX/TorchScript
- ✅ Jupyter notebooks executable

---

## 6. Error Handling

### 6.1 Error Categories

1. **Model Errors**
   - Shape mismatches
   - Invalid architecture
   - Out of memory
   - **Recovery**: Adjust architecture, reduce batch size

2. **Data Errors**
   - Dataset not found
   - Invalid data format
   - Corrupted files
   - **Recovery**: Validate dataset, skip corrupted samples

3. **Training Errors**
   - NaN/Inf loss
   - Gradient explosion
   - Convergence failure
   - **Recovery**: Reduce learning rate, gradient clipping, adjust architecture

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Framework**: PyTorch 2.0+
- **Experiment Tracking**: TensorBoard
- **Data Processing**: torchvision, torchtext, torchaudio
- **Optimization**: pytorch-lightning (optional)
- **Export**: ONNX, TorchScript

### 7.2 Dependencies
```python
dependencies = [
    "torch>=2.0.0",
    "torchvision>=0.15.0",
    "tensorboard>=2.13.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scikit-learn>=1.3.0",
    "tqdm>=4.65.0",
    "jupyter>=1.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0"
]
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
- ✅ Model forward pass
- ✅ Loss computation
- ✅ Data loading
- ✅ Augmentation pipeline

### 8.2 Integration Tests
- ✅ Full training loop (1 epoch)
- ✅ Checkpointing and loading
- ✅ TensorBoard logging

---

## 9. Future Enhancements

1. **Distributed Training**: Multi-GPU and multi-node support
2. **AutoML**: Neural architecture search
3. **Model Compression**: Quantization, pruning, distillation
4. **MLOps Integration**: MLflow, W&B integration
5. **Deployment**: Docker containers, TorchServe integration

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
