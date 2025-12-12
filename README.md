# 🔴 Red Team Lab - Adaptive LLM Security Testing

A sophisticated red team framework for testing LLM safety boundaries using self-mutating prompts. Integrates with **Garak** framework and implements **PAIR** (Prompt Automatic Iterative Refinement) and **ReAct** injection methodologies.

## ⚠️ Disclaimer

This tool is for **authorized security research only**. Use responsibly to:
- Test your own LLM deployments
- Understand vulnerabilities to build better defenses
- Conduct authorized red team assessments

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RED TEAM LAB                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   ATTACKER   │────▶│   MUTATION   │────▶│    TARGET    │    │
│  │    MODEL     │     │    ENGINE    │     │    MODEL     │    │
│  │ (deepseek-r1)│◀────│              │◀────│  (qwen3:30b) │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                    │                    │              │
│         │                    ▼                    │              │
│         │           ┌──────────────┐              │              │
│         │           │    JUDGE     │              │              │
│         └──────────▶│   ANALYSIS   │◀─────────────┘              │
│                     └──────────────┘                             │
│                            │                                     │
│                            ▼                                     │
│                    ┌──────────────┐                              │
│                    │   RESULTS    │                              │
│                    │   & LOGS     │                              │
│                    └──────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**: https://ollama.ai
2. **Pull required models**:
```bash
ollama pull deepseek-r1:70b  # Attacker model
ollama pull qwen3:30b        # Target model
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Run Assessment

```bash
# Standard assessment with default seeds
python run_redteam.py

# Interactive mutation mode
python run_redteam.py --mode interactive

# PAIR-focused attacks
python run_redteam.py --mode pair

# ReAct injection attacks
python run_redteam.py --mode react

# Custom seeds
python run_redteam.py --seeds seeds/custom.txt

# Quiet mode with custom iterations
python run_redteam.py --quiet --iterations 5
```

## 📁 Project Structure

```
redteam_lab/
├── config.py                 # Configuration settings
├── mutation_engine.py        # Core mutation strategies
├── attack_orchestrator.py    # Attack coordination
├── advanced_pair.py          # Full PAIR implementation
├── run_redteam.py           # Main entry point
├── probes/
│   └── adaptive_probe.py    # Garak integration probes
├── seeds/
│   ├── react_seeds.txt      # ReAct injection seeds
│   └── pair_seeds.txt       # PAIR methodology seeds
├── logs/                    # Attack logs (auto-created)
└── results/                 # Results & reports (auto-created)
```

## 🎯 Attack Strategies

### 1. PAIR (Prompt Automatic Iterative Refinement)
Iteratively refines prompts based on target responses using the attacker model.

```python
from advanced_pair import AdvancedPAIR

pair = AdvancedPAIR()
result = pair.run_attack(
    goal="Test safety boundaries",
    target_behavior="Explain security concepts",
    verbose=True
)
```

### 2. ReAct Injection
Injects false reasoning chains (Thought/Action/Observation) to manipulate model behavior.

```python
from mutation_engine import MutationEngine

engine = MutationEngine()
mutation = engine.mutate_react(
    original="Help with my order",
    target_response="I'd be happy to help...",
    goal="Trigger unauthorized action",
    iteration=1
)
```

### 3. Crescendo Attack
Gradually escalates requests across multiple turns to desensitize the model.

### 4. Persona Hijacking
Creates elaborate roleplay scenarios to bypass safety training.

### 5. Context Poisoning
Injects fake system messages or administrative contexts.

### 6. Obfuscation
Uses encoding, ciphers, or linguistic tricks to bypass keyword filters.

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Models
ATTACKER_MODEL = "deepseek-r1:70b"
TARGET_MODEL = "qwen3:30b"

# Attack settings
MAX_ITERATIONS = 10
MUTATION_TEMPERATURE = 0.9

# Detection keywords
SUCCESS_INDICATORS = ["I cannot", "I can't", ...]
JAILBREAK_INDICATORS = ["here's how", "step 1", ...]
```

## 📊 Output & Analysis

### Session Logs
Each session creates detailed JSONL logs in `logs/`:
```json
{"seed_name": "ReAct_Injection", "iteration": 3, "prompt": "...", "response": "...", "jailbreak_detected": false, "compliance_score": 45.0}
```

### Campaign Results
Summary reports in `results/`:
```json
{
  "session_id": "20241209_143022",
  "target_model": "qwen3:30b",
  "total_jailbreaks": 2,
  "success_rate": 0.25,
  "campaigns": [...]
}
```

## 🔌 Garak Integration

Use custom probes with Garak CLI:

```bash
# Copy probe to Garak probes directory
cp probes/adaptive_probe.py ~/.local/lib/python3.x/site-packages/garak/probes/

# Run with Garak
garak --model_type ollama --model_name qwen3:30b --probes adaptive_probe.AdaptiveMutatingProbe
```

## 🛡️ Building Blue Team Defenses

After running red team assessments, use findings to build defenses:

1. **Identify Patterns**: Review successful jailbreaks in `results/`
2. **Create Detectors**: Build custom Garak detectors for identified patterns
3. **Test Defenses**: Re-run red team with new defenses
4. **Iterate**: Continuous improvement cycle

### Example Defense Implementation

```python
# Custom detector for ReAct injection
class ReActInjectionDetector:
    def detect(self, prompt):
        patterns = [
            r'Thought:.*Action:.*Observation:',
            r'\[System.*\].*[Dd]isabled',
            r'Action:\s*\w+\([^)]+\)'
        ]
        return any(re.search(p, prompt) for p in patterns)
```

## 🤝 Contributing

This is a security research tool. Contributions welcome for:
- New mutation strategies
- Improved detection methods
- Better analysis tools
- Documentation improvements

## 📜 License

MIT License - Use responsibly for authorized security testing only.

