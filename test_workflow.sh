#!/bin/bash
# Complete SOA DSL Workflow Test

echo "========================================="
echo "SOA DSL - Complete Workflow Test"
echo "========================================="
echo ""

# Test 1: Validate YAML
echo "Test 1: Validating YAML file..."
venv/bin/python3 soa-dsl validate examples/soa_rules.yaml
echo ""

# Test 2: Generate from YAML
echo "Test 2: Generating Spectre code from YAML..."
venv/bin/python3 soa-dsl generate examples/soa_rules.yaml -o output/from_yaml.scs --no-validate
echo ""

# Test 3: Full compile
echo "Test 3: Full compile (validate + generate)..."
venv/bin/python3 soa-dsl compile examples/soa_rules.yaml -o output/final_output.scs
echo ""

# Test 4: Check output
echo "Test 4: Checking generated output..."
if [ -f output/final_output.scs ]; then
    lines=$(wc -l < output/final_output.scs)
    size=$(du -h output/final_output.scs | cut -f1)
    echo "✅ Output file created: $lines lines, $size"
    echo ""
    echo "First 20 lines of generated code:"
    head -20 output/final_output.scs
else
    echo "❌ Output file not created"
fi

echo ""
echo "========================================="
echo "All tests completed!"
echo "========================================="
