#!/usr/bin/env python3
"""
SOA Rule Creator - Web Interface Launcher
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("SOA Rule Creator - Web Interface")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and navigate to:")
    print("  http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
