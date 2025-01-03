# camera_tool.py
import streamlit as st
import re
import pytesseract
from PIL import Image
import io

def camera_data_collection():
    """
    Provide a simple interface to capture images and run OCR
    to find text matching "CIS-..." patterns.
    """
    st.subheader("Test Equipment Scanner")
    st.write("Use your camera to scan text containing 'CIS-' references.")

    captured_image = st.camera_input("Take a picture to scan")

    if captured_image is not None:
        # Convert the uploaded image (BytesIO) to a Pillow Image
        image = Image.open(io.BytesIO(captured_image.getvalue()))
        
        # Run OCR with pytesseract
        # Make sure Tesseract is installed on your system & pytesseract is installed in Python
        ocr_text = pytesseract.image_to_string(image)

        # Now search the OCR text for CIS- patterns
        pattern = r"CIS-(\d+)"
        found_numbers = re.findall(pattern, ocr_text)

        if found_numbers:
            st.write("**Test Equipment**")
            for number in found_numbers:
                st.write(f"CIS-{number}")
        else:
            st.write("No 'CIS-' references found in the scanned image.")

        # If you want to see the raw text for debugging:
        # st.write("DEBUG: OCR text:\n", ocr_text)
