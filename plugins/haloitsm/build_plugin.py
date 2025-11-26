#!/usr/bin/env python3
"""
Simple plugin builder for HaloITSM
Builds Docker image and exports as .plg file (gzipped Docker image)
"""
import os
import subprocess
import yaml
from pathlib import Path

def build_plugin():
    """Build the plugin Docker image and export as .plg file"""
    
    # Read plugin spec to get version
    with open('plugin.spec.yaml', 'r') as f:
        spec = yaml.safe_load(f)
    
    plugin_name = spec['name']
    vendor = spec['vendor']
    version = spec['version']
    docker_image = f"{vendor}/{plugin_name}:{version}"
    output_file = f"{vendor}_{plugin_name}_{version}.plg"
    
    print(f"Building {plugin_name} v{version}...")
    print(f"Docker image: {docker_image}")
    print(f"Output: {output_file}")
    
    
    # Step 1: Build Docker image
    print(f"\n[1/3] Building Docker image...")
    build_cmd = ['sudo', 'docker', 'build', '-t', docker_image, '.']
    result = subprocess.run(build_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Docker build failed:")
        print(result.stderr)
        return None
    
    print(f"  ✓ Docker image built successfully")
    
    # Step 2: Save Docker image to tar file
    print(f"\n[2/3] Exporting Docker image...")
    temp_tar = f"{vendor}_{plugin_name}_{version}_temp.tar"
    save_cmd = ['sudo', 'docker', 'save', docker_image]
    
    with open(temp_tar, 'wb') as f:
        result = subprocess.run(save_cmd, stdout=f, stderr=subprocess.PIPE, text=False)
    
    if result.returncode != 0:
        print(f"❌ Docker save failed:")
        print(result.stderr.decode())
        return None
    
    print(f"  ✓ Docker image exported to tar")
    
    # Step 3: Compress with gzip
    print(f"\n[3/3] Compressing...")
    gzip_cmd = ['gzip', '-f', temp_tar]
    result = subprocess.run(gzip_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Gzip compression failed:")
        print(result.stderr)
        return None
    
    # Rename to .plg extension
    gzipped_file = f"{temp_tar}.gz"
    if os.path.exists(gzipped_file):
        os.rename(gzipped_file, output_file)
    
    file_size = os.path.getsize(output_file)
    print(f"  ✓ Compressed to .plg format")
    
    print(f"\n✅ Plugin built successfully!")
    print(f"   Output: {output_file}")
    print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    print(f"\n   Ready to upload to Rapid7 InsightConnect!")
    
    return output_file

if __name__ == '__main__':
    build_plugin()
