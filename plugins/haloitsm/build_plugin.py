#!/usr/bin/env python3
"""
Simple plugin builder for HaloITSM
Creates a .plg file (TAR.GZ archive) with the required structure
"""
import os
import tarfile
import yaml
from pathlib import Path

def build_plugin():
    """Build the plugin .plg file"""
    
    # Read plugin spec to get version
    with open('plugin.spec.yaml', 'r') as f:
        spec = yaml.safe_load(f)
    
    plugin_name = spec['name']
    version = spec['version']
    output_file = f"{plugin_name}-{version}.plg"
    
    print(f"Building {plugin_name} v{version}...")
    
    # Files and directories to include
    include_patterns = [
        'plugin.spec.yaml',
        'setup.py',
        'help.md',
        'CONFIGURATION.md',
        'Dockerfile',
        'requirements.txt',
        'komand_haloitsm/**/*.py',
        'komand_haloitsm/**/*.yaml',
    ]
    
    # Create TAR.GZ file
    with tarfile.open(output_file, 'w:gz') as tar:
        # Add plugin.spec.yaml
        tar.add('plugin.spec.yaml')
        print(f"  ✓ Added plugin.spec.yaml")
        
        # Add setup.py
        if os.path.exists('setup.py'):
            tar.add('setup.py')
            print(f"  ✓ Added setup.py")
        
        # Add help.md
        if os.path.exists('help.md'):
            tar.add('help.md')
            print(f"  ✓ Added help.md")
            
        # Add CONFIGURATION.md
        if os.path.exists('CONFIGURATION.md'):
            tar.add('CONFIGURATION.md')
            print(f"  ✓ Added CONFIGURATION.md")
        
        # Add Dockerfile
        if os.path.exists('Dockerfile'):
            tar.add('Dockerfile')
            print(f"  ✓ Added Dockerfile")
            
        # Add requirements.txt
        if os.path.exists('requirements.txt'):
            tar.add('requirements.txt')
            print(f"  ✓ Added requirements.txt")
        
        # Add all Python files from komand_haloitsm
        base_path = Path('komand_haloitsm')
        if base_path.exists():
            tar.add(str(base_path), recursive=True)
            print(f"  ✓ Added komand_haloitsm directory with all files")
    
    file_size = os.path.getsize(output_file)
    print(f"\n✅ Plugin built successfully!")
    print(f"   Output: {output_file}")
    print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"\n   Ready to upload to Rapid7 InsightConnect!")
    
    return output_file

if __name__ == '__main__':
    build_plugin()
