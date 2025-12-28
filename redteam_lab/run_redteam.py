#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Red Team Lab - Main Runner Script
Integrates Garak framework with adaptive mutation engine

Usage:
    python run_redteam.py                    # Run with default seeds
    python run_redteam.py --seeds custom.txt # Load custom seeds
    python run_redteam.py --mode pair        # Run PAIR-only mode
    python run_redteam.py --mode react       # Run ReAct-only mode
    python run_redteam.py --interactive      # Interactive mutation mode
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # If it fails, ASCII output will be used as fallback

# Local imports
from config import ATTACKER_MODEL, TARGET_MODEL, MAX_ITERATIONS
from attack_orchestrator import AttackOrchestrator
from mutation_engine import MutationEngine, MutationStrategy
from probes.adaptive_probe import AdaptiveMutatingProbe, ReActInjectionProbe, PAIRProbe


def check_ollama_models():
    """Verify required models are available in Ollama"""
    import ollama

    print("Checking Ollama models...")
    try:
        models_response = ollama.list()
        
        # Debug: print raw response
        print(f"[DEBUG] Response type: {type(models_response)}")
        print(f"[DEBUG] Response: {models_response}")
        
        # Extract model list from response
        if hasattr(models_response, 'models'):
            models_list = models_response.models
        elif isinstance(models_response, dict):
            models_list = models_response.get('models', [])
        else:
            models_list = models_response
        
        available_models = []
        for m in models_list:
            try:
                # Handle Model objects (newer Ollama versions)
                if hasattr(m, 'model'):
                    available_models.append(m.model)
                # Handle dict format (older versions)
                elif isinstance(m, dict):
                    # Try both 'name' and 'model' keys
                    name = m.get('model') or m.get('name')
                    if name:
                        available_models.append(name)
                # Handle string format
                elif isinstance(m, str):
                    available_models.append(m)
            except Exception as parse_error:
                print(f"[WARN] Failed to parse model entry {m}: {parse_error}")
                continue
        
        print(f"[DEBUG] Available models: {available_models}")
        print(f"[DEBUG] Looking for: {ATTACKER_MODEL}, {TARGET_MODEL}")
        
        # Simple exact match
        attacker_found = ATTACKER_MODEL in available_models
        target_found = TARGET_MODEL in available_models
        
        if attacker_found:
            print(f"+ Attacker model: {ATTACKER_MODEL}")
        else:
            print(f"x Attacker model not found: {ATTACKER_MODEL}")
            
        if target_found:
            print(f"+ Target model: {TARGET_MODEL}")
        else:
            print(f"x Target model not found: {TARGET_MODEL}")
        
        if not (attacker_found and target_found):
            print("\nRun: ollama pull <model_name>")
            return False
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Cannot connect to Ollama: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        import traceback
        print(f"[DEBUG] Traceback:\n{traceback.format_exc()}")
        print("Make sure Ollama is running: ollama serve")
        return False


def run_standard_assessment(seeds: list, verbose: bool = True):
    """Run standard red team assessment with mutation"""
    orchestrator = AttackOrchestrator()
    return orchestrator.run_full_assessment(seeds, verbose=verbose)


def run_interactive_mode():
    """Interactive mode for manual prompt refinement"""
    import ollama

    engine = MutationEngine()

    print("\n" + "="*60)
    print("INTERACTIVE MUTATION MODE")
    print("="*60)
    print("Enter a seed prompt and goal. The system will help you refine it.")
    print("Commands: /quit, /reset, /strategy <name>, /save")
    print("="*60 + "\n")

    current_prompt = ""
    goal = ""
    iteration = 0
    history = []

    while True:
        if not current_prompt:
            print("Enter your seed prompt (end with empty line):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            current_prompt = "\n".join(lines)

            goal = input("Enter attack goal: ")
            iteration = 0

        print(
            f"\n[Iteration {iteration}] Sending to target model ({TARGET_MODEL})...")

        try:
            response = ollama.chat(
                model=TARGET_MODEL,
                messages=[{"role": "user", "content": current_prompt}],
                options={"temperature": 0.7}
            )
            target_response = response['message']['content']
        except Exception as e:
            print(f"[ERROR] {e}")
            continue

        print(f"\n--- TARGET RESPONSE ---\n{target_response}\n---")

        # Analyze response
        analysis = engine.analyze_response(target_response)
        print(f"\nAnalysis:")
        print(
            f"  Defense Detected: {analysis.get('defense_detected', 'unknown')}")
        print(f"  Compliance Level: {analysis.get('compliance_level', 0)}%")
        print(f"  Weaknesses: {analysis.get('weaknesses', [])}")

        # Store in history
        history.append({
            "iteration": iteration,
            "prompt": current_prompt,
            "response": target_response,
            "analysis": analysis
        })

        # Get user action
        print("\nOptions:")
        print("  [enter] Auto-mutate")
        print("  [p] PAIR mutation")
        print("  [r] ReAct injection")
        print("  [c] Crescendo")
        print("  [o] Obfuscation")
        print("  [m] Manual edit")
        print("  [s] Save and exit")
        print("  [q] Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == 'q':
            break
        elif choice == 's':
            filename = f"interactive_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(history, f, indent=2)
            print(f"Session saved to {filename}")
            break
        elif choice == 'm':
            print("Enter new prompt (end with empty line):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            current_prompt = "\n".join(lines)
        else:
            # Auto-mutate
            strategy_map = {
                'p': engine.mutate_pair,
                'r': engine.mutate_react,
                'c': engine.mutate_crescendo,
                'o': engine.mutate_obfuscation,
                '': engine.auto_mutate
            }

            mutate_func = strategy_map.get(choice, engine.auto_mutate)

            print("\n[Generating mutation using attacker model...]")
            result = mutate_func(
                current_prompt, target_response, goal, iteration + 1)

            print(f"\n--- MUTATED PROMPT ---\n{result.mutated_prompt}\n---")
            print(f"Strategy: {result.strategy.value}")

            use_mutation = input(
                "\nUse this mutation? [Y/n]: ").strip().lower()
            if use_mutation != 'n':
                current_prompt = result.mutated_prompt
                iteration += 1


def run_garak_integration(probe_type: str = "adaptive"):
    """Run using Garak framework integration"""
    try:
        import garak
        from garak.generators.ollama import OllamaGenerator
    except ImportError:
        print("[ERROR] Garak not installed. Install with: pip install garak")
        return

    print(f"\nRunning Garak integration with {probe_type} probe...")

    # Select probe
    if probe_type == "react":
        probe = ReActInjectionProbe()
    elif probe_type == "pair":
        probe = PAIRProbe()
    else:
        probe = AdaptiveMutatingProbe()

    print(f"Probe: {probe.name}")
    print(f"Prompts loaded: {len(probe.prompts)}")

    # Note: For full Garak CLI integration, use:
    # garak --model_type ollama --model_name qwen3:30b --probes adaptive_probe

    print("\nTo run via Garak CLI:")
    print(
        f"  garak --model_type ollama --model_name {TARGET_MODEL} --probes probes.adaptive_probe.AdaptiveMutatingProbe")

    return probe


def main():
    parser = argparse.ArgumentParser(
        description="Red Team Lab - Adaptive LLM Security Testing"
    )
    parser.add_argument(
        "--mode",
        choices=["standard", "interactive", "garak", "pair", "react"],
        default="standard",
        help="Execution mode"
    )
    parser.add_argument(
        "--seeds",
        type=str,
        nargs="+",
        help="Path to seed files (one prompt per line)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=MAX_ITERATIONS,
        help="Max mutation iterations per seed"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip Ollama model check"
    )

    args = parser.parse_args()

    print("""
    ============================================================
               RED TEAM LAB - LLM Security Testing            
                   Adaptive Mutation Engine                  
    ============================================================
    """)

    # Check models
    if not args.skip_check:
        if not check_ollama_models():
            print("\n[!] Model check failed. Use --skip-check to bypass.")
            sys.exit(1)

    # Load seeds
    if args.mode in ["standard", "pair", "react"]:
        probe = AdaptiveMutatingProbe(dataset_paths=args.seeds)
        seeds = probe.get_seeds()

        if args.mode == "pair":
            seeds = [s for s in seeds if s.get("category") in [
                "pair", "academic_bypass", "crescendo"]]
        elif args.mode == "react":
            seeds = [s for s in seeds if s.get("category") in [
                "react_injection", "context_poison"]]

    # Execute based on mode
    if args.mode == "interactive":
        run_interactive_mode()
    elif args.mode == "garak":
        run_garak_integration()
    else:
        # Update config if iterations specified
        if args.iterations != MAX_ITERATIONS:
            import config
            config.MAX_ITERATIONS = args.iterations

        run_standard_assessment(seeds, verbose=not args.quiet)


if __name__ == "__main__":
    main()
