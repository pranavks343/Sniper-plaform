#!/usr/bin/env python3
"""
Verification script for Sniper Test Suite setup.
Checks that all dependencies are installed and tests can run.
"""
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Python version: {version_str}")
    
    if version.major == 3 and version.minor >= 11:
        print_success(f"Python {version_str} is compatible")
        return True
    else:
        print_error(f"Python {version_str} is not compatible. Requires Python 3.11+")
        return False


def check_dependencies():
    """Check if all dependencies are installed."""
    print_header("Checking Dependencies")
    
    required_packages = [
        'pytest',
        'numpy',
        'pandas',
        'scipy',
        'sklearn',
        'xgboost',
        'joblib'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            all_installed = False
    
    return all_installed


def check_test_files():
    """Check if all test files exist."""
    print_header("Checking Test Files")
    
    test_dirs = {
        'unit': ['test_strategy_engine.py', 'test_execution_engine.py', 'test_risk_engine.py', 'test_quantum.py'],
        'integration': ['test_signal_to_order_flow.py', 'test_position_management_flow.py', 'test_risk_breach_flow.py'],
        'performance': ['test_latency.py', 'test_throughput.py', 'test_quantum_performance.py'],
        'system': ['test_backtest_validation.py', 'test_circuit_breaker.py']
    }
    
    all_exist = True
    test_count = 0
    
    for dir_name, files in test_dirs.items():
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print_error(f"Directory {dir_name}/ does not exist")
            all_exist = False
            continue
        
        for file_name in files:
            file_path = dir_path / file_name
            if file_path.exists():
                print_success(f"{dir_name}/{file_name}")
                test_count += 1
            else:
                print_error(f"{dir_name}/{file_name} does not exist")
                all_exist = False
    
    print(f"\nTotal test files found: {test_count}")
    
    return all_exist


def check_documentation():
    """Check if documentation files exist."""
    print_header("Checking Documentation")
    
    docs = [
        'README.md',
        'QUICKSTART.md',
        'INSTALLATION.md',
        'TEST_SUMMARY.md',
        'INDEX.md',
        'conftest.py',
        'pytest.ini',
        'requirements.txt',
        'run_tests.sh'
    ]
    
    all_exist = True
    
    for doc in docs:
        doc_path = Path(doc)
        if doc_path.exists():
            print_success(f"{doc}")
        else:
            print_error(f"{doc} does not exist")
            all_exist = False
    
    return all_exist


def run_sample_test():
    """Run a sample test to verify pytest works."""
    print_header("Running Sample Test")
    
    try:
        result = subprocess.run(
            ['pytest', '--collect-only', '-q'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-5:]:
                print(line)
            
            print_success("Pytest can collect tests successfully")
            return True
        else:
            print_error("Pytest failed to collect tests")
            print(result.stderr)
            return False
    
    except subprocess.TimeoutExpired:
        print_error("Test collection timed out")
        return False
    except FileNotFoundError:
        print_error("pytest command not found. Install with: pip install pytest")
        return False
    except Exception as e:
        print_error(f"Error running pytest: {e}")
        return False


def print_summary(results):
    """Print summary of verification."""
    print_header("Verification Summary")
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        if passed:
            print_success(f"{check}: PASSED")
        else:
            print_error(f"{check}: FAILED")
    
    print()
    
    if all_passed:
        print("🎉 All checks passed! Setup is complete.")
        print("\nNext steps:")
        print("  1. Run tests: ./run_tests.sh all")
        print("  2. Read QUICKSTART.md for more commands")
        print("  3. Check TEST_SUMMARY.md for test overview")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Check Python version: python --version")
        print("  3. Read INSTALLATION.md for detailed setup")
        return 1


def main():
    """Main verification function."""
    print("\n🧪 Sniper Test Suite - Setup Verification")
    print("=" * 60)
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Test Files': check_test_files(),
        'Documentation': check_documentation(),
        'Pytest Functionality': run_sample_test()
    }
    
    return print_summary(results)


if __name__ == '__main__':
    sys.exit(main())
