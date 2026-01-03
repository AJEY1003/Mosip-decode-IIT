#!/usr/bin/env python3
"""
QR Code Analyzer and Resizer
- Decodes QR codes to show their content
- Resizes QR codes to meet minimum file size requirements (10KB for Inji Verify)
- Analyzes different QR code formats

Usage:
    py -m qr_analyzer_resizer
"""

try:
    import cv2
    import numpy as np
except ImportError:
    print("❌ OpenCV not found. Install with: pip install opencv-python")
    cv2 = None

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ PIL not found. Install with: pip install Pillow")
    Image = None

import os
import json
import base64
from datetime import datetime
import qrcode

def get_file_size_kb(filepath):
    """Get file size in KB"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        return size_bytes / 1024
    return 0

def decode_qr_with_opencv(image_path):
    """Decode QR code using OpenCV"""
    if not cv2:
        return {"success": False, "error": "OpenCV not available"}
    
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {"success": False, "error": "Could not read image"}
        
        # Initialize QR code detector
        detector = cv2.QRCodeDetector()
        
        # Detect and decode QR code
        data, vertices_array, binary_qrcode = detector.detectAndDecode(image)
        
        if data:
            return {
                "success": True,
                "qr_data": data,
                "data_length": len(data),
                "data_type": "JSON" if data.strip().startswith('{') else "Text"
            }
        else:
            return {"success": False, "error": "No QR code detected"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def decode_qr_with_pyzbar(image_path):
    """Decode QR code using pyzbar (alternative method)"""
    try:
        from pyzbar import pyzbar
        from PIL import Image
        
        # Open image
        image = Image.open(image_path)
        
        # Decode QR codes
        qr_codes = pyzbar.decode(image)
        
        if qr_codes:
            qr_data = qr_codes[0].data.decode('utf-8')
            return {
                "success": True,
                "qr_data": qr_data,
                "data_length": len(qr_data),
                "data_type": "JSON" if qr_data.strip().startswith('{') else "Text"
            }
        else:
            return {"success": False, "error": "No QR code detected"}
            
    except ImportError:
        return {"success": False, "error": "pyzbar not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def resize_qr_to_target_size(image_path, target_size_kb=10, output_path=None):
    """Resize QR code image to meet minimum file size requirement"""
    if not Image:
        return {"success": False, "error": "PIL not available"}
    
    try:
        # Open original image
        original_image = Image.open(image_path)
        original_size_kb = get_file_size_kb(image_path)
        
        if output_path is None:
            name, ext = os.path.splitext(image_path)
            output_path = f"{name}_resized_{target_size_kb}kb{ext}"
        
        print(f"📏 Original size: {original_size_kb:.2f} KB")
        print(f"🎯 Target size: {target_size_kb} KB")
        
        if original_size_kb >= target_size_kb:
            print(f"✅ Image already meets size requirement")
            # Just copy the file
            original_image.save(output_path, quality=95)
            return {
                "success": True,
                "output_path": output_path,
                "original_size_kb": original_size_kb,
                "final_size_kb": get_file_size_kb(output_path),
                "resized": False
            }
        
        # Calculate scaling factor to reach target size
        # File size roughly scales with pixel count (width * height)
        scale_factor = (target_size_kb / original_size_kb) ** 0.5
        scale_factor = max(scale_factor, 2.0)  # Minimum 2x scaling
        
        # Calculate new dimensions
        new_width = int(original_image.width * scale_factor)
        new_height = int(original_image.height * scale_factor)
        
        print(f"🔧 Scaling from {original_image.width}x{original_image.height} to {new_width}x{new_height}")
        
        # Resize image using high-quality resampling
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with high quality
        resized_image.save(output_path, quality=95, optimize=False)
        
        final_size_kb = get_file_size_kb(output_path)
        
        # If still not big enough, try adding a border or increasing quality
        if final_size_kb < target_size_kb:
            print(f"🔄 Still too small ({final_size_kb:.2f} KB), adding border...")
            
            # Add a white border to increase file size
            border_size = 50
            bordered_image = Image.new('RGB', 
                                     (new_width + 2*border_size, new_height + 2*border_size), 
                                     'white')
            bordered_image.paste(resized_image, (border_size, border_size))
            
            # Add some text to increase file size
            try:
                draw = ImageDraw.Draw(bordered_image)
                text = f"QR Code - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                draw.text((10, 10), text, fill='black')
                draw.text((10, bordered_image.height - 30), f"File size: {target_size_kb}KB target", fill='black')
            except:
                pass  # If font loading fails, continue without text
            
            bordered_image.save(output_path, quality=100, optimize=False)
            final_size_kb = get_file_size_kb(output_path)
        
        return {
            "success": True,
            "output_path": output_path,
            "original_size_kb": original_size_kb,
            "final_size_kb": final_size_kb,
            "scale_factor": scale_factor,
            "new_dimensions": f"{new_width}x{new_height}",
            "resized": True
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_qr_file(filepath):
    """Analyze a QR code file - decode content and show file info"""
    print(f"\n🔍 Analyzing: {filepath}")
    print("=" * 60)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    # File info
    size_kb = get_file_size_kb(filepath)
    print(f"📁 File size: {size_kb:.2f} KB")
    
    if Image:
        try:
            img = Image.open(filepath)
            print(f"📐 Dimensions: {img.width}x{img.height} pixels")
            print(f"🎨 Mode: {img.mode}")
        except:
            print("❌ Could not read image info")
    
    # Try to decode QR content
    print(f"\n🔓 Decoding QR content...")
    
    # Try OpenCV first
    opencv_result = decode_qr_with_opencv(filepath)
    if opencv_result["success"]:
        print(f"✅ OpenCV decode successful")
        print(f"📊 Data length: {opencv_result['data_length']} characters")
        print(f"📋 Data type: {opencv_result['data_type']}")
        
        qr_data = opencv_result["qr_data"]
        
        # Show preview of content
        if opencv_result["data_type"] == "JSON":
            try:
                parsed_json = json.loads(qr_data)
                print(f"🔍 JSON Preview:")
                if isinstance(parsed_json, dict):
                    for key, value in list(parsed_json.items())[:5]:  # Show first 5 keys
                        if isinstance(value, str) and len(value) > 50:
                            print(f"  {key}: {value[:50]}...")
                        else:
                            print(f"  {key}: {value}")
                    if len(parsed_json) > 5:
                        print(f"  ... and {len(parsed_json) - 5} more fields")
            except:
                print(f"🔍 Raw content preview: {qr_data[:200]}...")
        else:
            print(f"🔍 Text content:")
            lines = qr_data.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                print(f"  {line}")
            if len(lines) > 10:
                print(f"  ... and {len(lines) - 10} more lines")
    else:
        print(f"❌ OpenCV decode failed: {opencv_result['error']}")
        
        # Try pyzbar as fallback
        pyzbar_result = decode_qr_with_pyzbar(filepath)
        if pyzbar_result["success"]:
            print(f"✅ pyzbar decode successful")
            print(f"📊 Data length: {pyzbar_result['data_length']} characters")
            print(f"🔍 Content preview: {pyzbar_result['qr_data'][:200]}...")
        else:
            print(f"❌ pyzbar decode also failed: {pyzbar_result['error']}")

def main():
    """Main function to analyze and resize QR codes"""
    print("🔍 QR Code Analyzer and Resizer")
    print("=" * 60)
    
    # Find QR code files in current directory
    qr_files = []
    for file in os.listdir('.'):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')) and 'qr' in file.lower():
            qr_files.append(file)
    
    if not qr_files:
        print("❌ No QR code files found in current directory")
        print("💡 Looking for files with 'qr' in the name and .png/.jpg extension")
        return
    
    print(f"📁 Found {len(qr_files)} QR code files:")
    for file in qr_files:
        print(f"  • {file}")
    
    # Analyze each QR file
    for qr_file in qr_files:
        analyze_qr_file(qr_file)
        
        # Check if resizing is needed for Inji Verify (10KB minimum)
        size_kb = get_file_size_kb(qr_file)
        if size_kb < 10:
            print(f"\n🔧 Resizing for Inji Verify (needs 10KB minimum)...")
            resize_result = resize_qr_to_target_size(qr_file, target_size_kb=10)
            
            if resize_result["success"]:
                print(f"✅ Resized successfully:")
                print(f"  📁 Output: {resize_result['output_path']}")
                print(f"  📏 Final size: {resize_result['final_size_kb']:.2f} KB")
                if resize_result["resized"]:
                    print(f"  🔧 Scale factor: {resize_result['scale_factor']:.2f}x")
                    print(f"  📐 New dimensions: {resize_result['new_dimensions']}")
            else:
                print(f"❌ Resize failed: {resize_result['error']}")
        else:
            print(f"✅ File size OK for Inji Verify ({size_kb:.2f} KB >= 10 KB)")
    
    print(f"\n🎯 Summary:")
    print(f"• Analyzed {len(qr_files)} QR code files")
    print(f"• Files ending with '_resized_10kb.png' are ready for Inji Verify")
    print(f"• Use these resized files for testing with Inji Verify portal")

if __name__ == "__main__":
    main()