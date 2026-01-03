#!/usr/bin/env python3
"""
Tesseract OCR Processor - Offline OCR using Tesseract
Pure offline OCR processing without cloud dependencies
"""

import cv2
import numpy as np
from PIL import Image
import io
import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid

# Try to import pytesseract, fallback to mock if not available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available, using mock OCR")

logger = logging.getLogger(__name__)