#!/usr/bin/env python3
"""
Capability Schema Validator

Validates capability YAML files against the schema.
Catches missing fields, invalid values, and structural issues.

Usage:
    python validate.py capabilities/my-capability.yaml
    python validate.py --all capabilities/
"""

import argparse
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


VALID_DOMAINS = [
    'context-management',
    'payment-services',
    'development-tooling',
    'observability',
    'ci-cd',
    'data-engineering',
]

VALID_MATURITY = ['experimental', 'developing', 'stable', 'battle-tested']

VALID_FRESHNESS = ['real-time', 'minutes', 'hours', 'daily', 'weekly', 'static']

REQUIRED_TOP_LEVEL = ['id', 'name', 'domain', 'version', 'action', 'requires', 'produces', 'confidence', 'metadata']

REQUIRED_ACTION = ['description', 'trigger']

REQUIRED_CONFIDENCE = ['maturity']

REQUIRED_METADATA = ['author', 'created']


def validate_capability(cap: dict, filepath: str) -> list[str]:
    """Validate a capability dict and return list of errors."""
    errors = []

    # Check required top-level fields
    for field in REQUIRED_TOP_LEVEL:
        if field not in cap:
            errors.append(f"Missing required field: {field}")

    # Validate id format
    cap_id = cap.get('id', '')
    if cap_id and not cap_id.replace('-', '').isalnum():
        errors.append(f"Invalid id format: {cap_id} (must be lowercase alphanumeric with hyphens)")

    # Validate domain
    domain = cap.get('domain', '')
    if domain and domain not in VALID_DOMAINS:
        errors.append(f"Invalid domain: {domain}. Must be one of: {', '.join(VALID_DOMAINS)}")

    # Validate version format
    version = cap.get('version', '')
    if version:
        parts = version.split('.')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            errors.append(f"Invalid version format: {version} (must be X.Y.Z)")

    # Validate action
    action = cap.get('action', {})
    if action:
        for field in REQUIRED_ACTION:
            if field not in action:
                errors.append(f"Missing action.{field}")

    # Validate requires
    requires = cap.get('requires', {})
    if requires:
        sources = requires.get('sources_of_truth', [])
        for i, source in enumerate(sources):
            if 'name' not in source:
                errors.append(f"sources_of_truth[{i}] missing 'name'")
            if 'location' not in source:
                errors.append(f"sources_of_truth[{i}] missing 'location'")
            if 'freshness' not in source:
                errors.append(f"sources_of_truth[{i}] missing 'freshness'")
            elif source.get('freshness') not in VALID_FRESHNESS:
                errors.append(f"sources_of_truth[{i}] invalid freshness: {source.get('freshness')}")

    # Validate produces
    produces = cap.get('produces', {})
    if produces:
        outputs = produces.get('outputs', [])
        for i, output in enumerate(outputs):
            if 'format' not in output:
                errors.append(f"outputs[{i}] missing 'format'")
            if 'destination' not in output:
                errors.append(f"outputs[{i}] missing 'destination'")

    # Validate confidence
    confidence = cap.get('confidence', {})
    if confidence:
        for field in REQUIRED_CONFIDENCE:
            if field not in confidence:
                errors.append(f"Missing confidence.{field}")
        maturity = confidence.get('maturity', '')
        if maturity and maturity not in VALID_MATURITY:
            errors.append(f"Invalid maturity: {maturity}. Must be one of: {', '.join(VALID_MATURITY)}")

    # Validate metadata
    metadata = cap.get('metadata', {})
    if metadata:
        for field in REQUIRED_METADATA:
            if field not in metadata:
                errors.append(f"Missing metadata.{field}")

    # Quality checks (warnings, not errors)
    warnings = []

    # Check for empty known_gaps (suspicious)
    known_gaps = confidence.get('known_gaps', [])
    if not known_gaps:
        warnings.append("No known_gaps documented - are you being honest about limitations?")

    # Check for empty failure_modes
    failure_modes = confidence.get('failure_modes', [])
    if not failure_modes:
        warnings.append("No failure_modes documented - how does this capability fail?")

    return errors, warnings


def print_validation_result(filepath: str, errors: list, warnings: list):
    """Print validation results for a file."""
    filename = Path(filepath).name

    if not errors and not warnings:
        print(f"{Colors.GREEN}✓{Colors.END} {filename}")
        return True

    if errors:
        print(f"{Colors.RED}✗{Colors.END} {filename}")
        for err in errors:
            print(f"  {Colors.RED}ERROR:{Colors.END} {err}")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} {filename}")

    for warn in warnings:
        print(f"  {Colors.YELLOW}WARN:{Colors.END} {warn}")

    return len(errors) == 0


def validate_file(filepath: Path) -> bool:
    """Validate a single capability file."""
    try:
        with open(filepath) as f:
            cap = yaml.safe_load(f)

        if not isinstance(cap, dict):
            print(f"{Colors.RED}✗{Colors.END} {filepath.name}")
            print(f"  {Colors.RED}ERROR:{Colors.END} File is not a valid YAML mapping")
            return False

        errors, warnings = validate_capability(cap, str(filepath))
        return print_validation_result(str(filepath), errors, warnings)

    except yaml.YAMLError as e:
        print(f"{Colors.RED}✗{Colors.END} {filepath.name}")
        print(f"  {Colors.RED}ERROR:{Colors.END} Invalid YAML: {e}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {filepath.name}")
        print(f"  {Colors.RED}ERROR:{Colors.END} {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Validate capability YAML files against schema',
        epilog='Catches missing fields and invalid values before they cause problems.'
    )
    parser.add_argument('path', help='Path to capability YAML file or directory')
    parser.add_argument('--all', action='store_true', help='Validate all files in directory')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')

    args = parser.parse_args()
    path = Path(args.path)

    print(f"\n{Colors.BOLD}Capability Validator{Colors.END}\n")

    if args.all or path.is_dir():
        yaml_files = list(path.glob('**/*.yaml')) + list(path.glob('**/*.yml'))
        yaml_files = [f for f in yaml_files if 'schema' not in str(f)]

        if not yaml_files:
            print(f"No capability files found in {path}")
            sys.exit(1)

        results = [validate_file(f) for f in yaml_files]

        passed = sum(results)
        total = len(results)
        print(f"\n{Colors.BOLD}Results:{Colors.END} {passed}/{total} valid")

        sys.exit(0 if all(results) else 1)
    else:
        if not path.exists():
            print(f"File not found: {path}")
            sys.exit(1)

        success = validate_file(path)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
