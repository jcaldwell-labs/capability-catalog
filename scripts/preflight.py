#!/usr/bin/env python3
"""
Capability Pre-flight Check

Validates that capability requirements are satisfied before execution.
Surfaces known gaps and blockers BEFORE you waste time on the wrong path.

Usage:
    python preflight.py capabilities/my-domain/my-capability.yaml
    python preflight.py --all capabilities/
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Install PyYAML: pip install pyyaml")
    sys.exit(1)


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def check_mark(passed: bool) -> str:
    if passed:
        return f"{Colors.GREEN}✓{Colors.END}"
    return f"{Colors.RED}✗{Colors.END}"


def warn_mark() -> str:
    return f"{Colors.YELLOW}⚠{Colors.END}"


def run_validation(command: str) -> tuple[bool, str]:
    """Run a validation command and return (success, output)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout or result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_sources_of_truth(sources: list) -> list[dict]:
    """Validate sources of truth are accessible."""
    results = []
    for source in sources:
        name = source.get('name', 'Unknown')
        location = source.get('location', '')
        validation = source.get('validation', '')
        freshness = source.get('freshness', 'unknown')

        result = {
            'name': name,
            'location': location,
            'freshness': freshness,
            'passed': False,
            'message': ''
        }

        if validation:
            passed, output = run_validation(validation)
            result['passed'] = passed
            result['message'] = output.strip()[:100] if output else ''
        else:
            # No validation command - check if it's a file path
            if location.startswith('/') or location.startswith('~'):
                expanded = os.path.expanduser(location)
                result['passed'] = os.path.exists(expanded)
                result['message'] = 'File exists' if result['passed'] else 'File not found'
            else:
                result['passed'] = None  # Unknown - can't validate
                result['message'] = 'No validation command'

        results.append(result)
    return results


def check_environment(env_reqs: list) -> list[dict]:
    """Check environment requirements."""
    results = []
    for req in env_reqs:
        result = {'requirement': req, 'passed': None, 'message': ''}

        # Try to detect common patterns
        req_lower = req.lower()
        if 'installed' in req_lower:
            # Extract tool name and check if it exists
            words = req.split()
            for word in words:
                if word.endswith('+'):
                    tool = word.rstrip('+').rstrip('v').rstrip(' ')
                    passed, _ = run_validation(f"which {tool}")
                    result['passed'] = passed
                    result['message'] = f"{tool} {'found' if passed else 'not found'}"
                    break

        results.append(result)
    return results


def check_access(access_reqs: list) -> list[dict]:
    """Check access requirements (mostly manual verification needed)."""
    results = []
    for req in access_reqs:
        result = {'requirement': req, 'passed': None, 'message': 'Manual verification needed'}

        # Try to detect VPN
        if 'vpn' in req.lower():
            # Check for common VPN interfaces
            passed, output = run_validation("ip addr show | grep -E 'tun|tap|wg' | head -1")
            if passed and output.strip():
                result['passed'] = True
                result['message'] = 'VPN interface detected'
            else:
                result['passed'] = None
                result['message'] = 'VPN status unknown'

        # Check for AWS credentials
        if 'aws' in req.lower() or 'sso' in req.lower():
            passed, output = run_validation("aws sts get-caller-identity 2>&1 | head -1")
            if passed:
                result['passed'] = True
                result['message'] = 'AWS credentials valid'
            else:
                result['passed'] = False
                result['message'] = 'AWS credentials invalid or expired'

        results.append(result)
    return results


def print_preflight_report(capability: dict, results: dict):
    """Print a formatted pre-flight report."""
    name = capability.get('name', 'Unknown Capability')
    cap_id = capability.get('id', 'unknown')
    maturity = capability.get('confidence', {}).get('maturity', 'unknown')

    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}Pre-flight Check: {name}{Colors.END}")
    print(f"ID: {cap_id} | Maturity: {maturity}")
    print(f"{'='*60}\n")

    # Sources of Truth
    if results.get('sources'):
        print(f"{Colors.BOLD}Sources of Truth:{Colors.END}")
        for src in results['sources']:
            mark = check_mark(src['passed']) if src['passed'] is not None else warn_mark()
            print(f"  {mark} {src['name']}")
            if src['message']:
                print(f"      {Colors.CYAN}{src['message']}{Colors.END}")
        print()

    # Access
    if results.get('access'):
        print(f"{Colors.BOLD}Access Requirements:{Colors.END}")
        for acc in results['access']:
            mark = check_mark(acc['passed']) if acc['passed'] is not None else warn_mark()
            print(f"  {mark} {acc['requirement']}")
            if acc['message']:
                print(f"      {Colors.CYAN}{acc['message']}{Colors.END}")
        print()

    # Environment
    if results.get('environment'):
        print(f"{Colors.BOLD}Environment:{Colors.END}")
        for env in results['environment']:
            mark = check_mark(env['passed']) if env['passed'] is not None else warn_mark()
            print(f"  {mark} {env['requirement']}")
            if env['message']:
                print(f"      {Colors.CYAN}{env['message']}{Colors.END}")
        print()

    # Known Gaps (always show these)
    known_gaps = capability.get('confidence', {}).get('known_gaps', [])
    if known_gaps:
        print(f"{Colors.BOLD}Known Gaps (review before proceeding):{Colors.END}")
        for gap in known_gaps:
            print(f"  {warn_mark()} {gap}")
        print()

    # Failure Modes
    failure_modes = capability.get('confidence', {}).get('failure_modes', [])
    if failure_modes:
        print(f"{Colors.BOLD}Common Failure Modes:{Colors.END}")
        for mode in failure_modes:
            print(f"  {Colors.YELLOW}→{Colors.END} {mode}")
        print()

    # Summary
    all_checks = (
        results.get('sources', []) +
        results.get('access', []) +
        results.get('environment', [])
    )
    passed = sum(1 for c in all_checks if c.get('passed') is True)
    failed = sum(1 for c in all_checks if c.get('passed') is False)
    unknown = sum(1 for c in all_checks if c.get('passed') is None)

    print(f"{Colors.BOLD}Summary:{Colors.END}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.END} | {Colors.RED}Failed: {failed}{Colors.END} | {Colors.YELLOW}Unknown: {unknown}{Colors.END}")

    if failed > 0:
        print(f"\n{Colors.RED}⚠ BLOCKED: {failed} requirement(s) not met{Colors.END}")
        return False
    elif unknown > 0:
        print(f"\n{Colors.YELLOW}⚠ CAUTION: {unknown} requirement(s) need manual verification{Colors.END}")
        return True
    else:
        print(f"\n{Colors.GREEN}✓ READY: All requirements satisfied{Colors.END}")
        return True


def run_preflight(capability_path: Path) -> bool:
    """Run pre-flight check for a single capability file."""
    with open(capability_path) as f:
        capability = yaml.safe_load(f)

    requires = capability.get('requires', {})

    results = {
        'sources': check_sources_of_truth(requires.get('sources_of_truth', [])),
        'access': check_access(requires.get('access', [])),
        'environment': check_environment(requires.get('environment', [])),
    }

    return print_preflight_report(capability, results)


def main():
    parser = argparse.ArgumentParser(
        description='Capability Pre-flight Check',
        epilog='Check if you can actually execute a capability right now.'
    )
    parser.add_argument('path', help='Path to capability YAML file or directory')
    parser.add_argument('--all', action='store_true', help='Check all capabilities in directory')

    args = parser.parse_args()
    path = Path(args.path)

    if args.all or path.is_dir():
        yaml_files = list(path.glob('**/*.yaml')) + list(path.glob('**/*.yml'))
        yaml_files = [f for f in yaml_files if 'schema' not in str(f)]

        if not yaml_files:
            print(f"No capability files found in {path}")
            sys.exit(1)

        results = []
        for yaml_file in yaml_files:
            try:
                results.append(run_preflight(yaml_file))
            except Exception as e:
                print(f"Error processing {yaml_file}: {e}")
                results.append(False)

        passed = sum(results)
        print(f"\n{'='*60}")
        print(f"Total: {passed}/{len(results)} capabilities ready")
        sys.exit(0 if all(results) else 1)
    else:
        if not path.exists():
            print(f"File not found: {path}")
            sys.exit(1)

        success = run_preflight(path)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
