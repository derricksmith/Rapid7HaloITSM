# Correct Build Process for HaloITSM Plugin

## ✅ Solution: Use Official Rapid7 Build Method

After investigating the [official Rapid7 InsightConnect plugins repository](https://github.com/rapid7/insightconnect-plugins), the correct build process is:

### Key Findings

1. **NO `insight-plugin` Python package needed** - The official plugins don't use this
2. **File format is `.tar` not `.plg`** - The extension doesn't matter, it's a gzipped Docker image
3. **Build command**: `docker save <image> | gzip > vendor_name_version.tar`
4. **Schema generation** uses `icon-plugin` (optional, for regenerating schema from spec)

### Correct Build Commands

```bash
cd /media/derrick/0011-8D39/Derrick/Code/Rapid7HaloITSM/plugins/haloitsm

# Build and export in one command
make export

# Or manually:
# 1. Build Docker image
sudo docker build --no-cache -t derricksmith/haloitsm:1.0.0 .

# 2. Export as gzipped tar
sudo docker save derricksmith/haloitsm:1.0.0 | gzip > derricksmith_haloitsm_1.0.0.tar
```

### Result

**File**: `derricksmith_haloitsm_1.0.0.tar`  
**Size**: 78MB (reduced from 91MB)  
**Format**: Gzipped Docker image export  
**Ready to upload**: ✅

---

## Upload to InsightConnect

1. Navigate to https://us.insight.rapid7.com/
2. Click **Settings** → **Plugins & Tools**
3. Click **Import** → **From Local Drive**
4. Select: `/media/derrick/0011-8D39/Derrick/Code/Rapid7HaloITSM/plugins/haloitsm/derricksmith_haloitsm_1.0.0.tar`
5. Click **Upload**

---

## What Was Wrong Before

### ❌ Incorrect Approaches Tried:
1. **Using `insight-plugin export`** - Package has Python 3.12 compatibility issues
2. **Creating `.plg` files** - Extension doesn't matter, format is what counts
3. **Using custom Python build scripts** - Unnecessary complexity
4. **Wrong Docker export format** - Used plain tar or wrong compression

### ✅ Correct Approach:
- Use standard Docker build with official Rapid7 base image
- Export with `docker save | gzip` 
- Follow exact Makefile pattern from rapid7/insightconnect-plugins
- File extension can be `.tar` or `.plg` (both work, it's just a gzipped Docker image)

---

## References

- **Official Plugins**: https://github.com/rapid7/insightconnect-plugins
- **Example Makefile**: https://github.com/rapid7/insightconnect-plugins/blob/main/plugins/rest/Makefile
- **Build Pattern**: All official plugins use: `docker save $(VENDOR)/$(NAME):$(VERSION) | gzip > $(VENDOR)_$(NAME)_$(VERSION).tar`

---

**Updated**: November 26, 2025  
**Build File**: `derricksmith_haloitsm_1.0.0.tar` (78MB)  
**Status**: Ready for upload ✅
