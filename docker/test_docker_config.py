#!/usr/bin/env python3
"""
Test Docker configuration files
"""

import os

def test_dockerfile():
    """Test Dockerfile syntax"""
    print("🐳 Testing Dockerfile...")

    if not os.path.exists('Dockerfile'):
        print("  ❌ Dockerfile not found")
        return False

    with open('Dockerfile', 'r') as f:
        content = f.read()

    required_instructions = ['FROM', 'WORKDIR', 'COPY', 'RUN', 'EXPOSE', 'CMD']
    for instruction in required_instructions:
        if instruction in content:
            print(f"  ✅ {instruction} instruction found")
        else:
            print(f"  ❌ {instruction} instruction missing")
            return False

    return True

def test_docker_compose():
    """Test docker-compose.yml syntax"""
    print("\n🐳 Testing docker-compose.yml...")

    if not os.path.exists('docker-compose.yml'):
        print("  ❌ docker-compose.yml not found")
        return False

    with open('docker-compose.yml', 'r') as f:
        content = f.read()

    required_elements = ['services:', 'experiment-bot:', 'build:', 'ports:', 'environment:']
    for element in required_elements:
        if element in content:
            print(f"  ✅ {element} found")
        else:
            print(f"  ❌ {element} missing")
            return False

    return True

def test_entrypoint_script():
    """Test entrypoint script"""
    print("\n🐳 Testing docker-entrypoint.sh...")

    if not os.path.exists('docker-entrypoint.sh'):
        print("  ❌ docker-entrypoint.sh not found")
        return False

    if not os.access('docker-entrypoint.sh', os.X_OK):
        print("  ❌ docker-entrypoint.sh not executable")
        return False

    with open('docker-entrypoint.sh', 'r') as f:
        content = f.read()

    required_elements = ['#!/bin/bash', 'TELEGRAM_BOT_TOKEN', 'start_bot', 'start_server']
    for element in required_elements:
        if element in content:
            print(f"  ✅ {element} found")
        else:
            print(f"  ❌ {element} missing")
            return False

    return True

def test_dockerignore():
    """Test .dockerignore file"""
    print("\n🐳 Testing .dockerignore...")

    if not os.path.exists('.dockerignore'):
        print("  ❌ .dockerignore not found")
        return False

    with open('.dockerignore', 'r') as f:
        content = f.read()

    important_ignores = ['__pycache__', '*.pyc', '.env', 'experiment_bot_env/']
    for ignore in important_ignores:
        if ignore in content:
            print(f"  ✅ {ignore} ignored")
        else:
            print(f"  ⚠️  {ignore} not ignored (recommended)")

    return True

def main():
    print("🚀 ExperimentBot Docker Configuration Test")
    print("=" * 50)

    tests = [
        ("Dockerfile", test_dockerfile),
        ("Docker Compose", test_docker_compose),
        ("Entrypoint Script", test_entrypoint_script),
        ("Dockerignore", test_dockerignore),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("📊 Test Results:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All Docker configuration tests passed!")
        print("\nTo use Docker:")
        print("1. Get bot token from @BotFather")
        print("2. Copy .env.docker to .env and set your token")
        print("3. Run: docker-compose up -d")
    else:
        print("❌ Some Docker configuration tests failed.")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)