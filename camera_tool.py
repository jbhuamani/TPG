import streamlit as st
import re
import pytesseract
from PIL import Image
import io

def camera_data_collection():
    """
    Use camera to scan images for "CIS-" references.
    Persist scanned CIS numbers (only digits) in st.session_state,
    so they stay even if the user clears the camera photo.
    """

    st.subheader("Test Equipment Scanner")

    # 1) Initialize the list in session_state if it doesn't exist yet
    if "cis_numbers" not in st.session_state:
        st.session_state["cis_numbers"] = []

    # 2) Camera input: returns an image or None
    captured_image = st.camera_input("Take a picture to scan")

    # 3) If a photo is captured, run OCR to find "CIS-####" patterns
    if captured_image is not None:
        # Convert the uploaded image to a Pillow Image
        image = Image.open(io.BytesIO(captured_image.getvalue()))

        # Perform OCR (pytesseract requires Tesseract installed)
        ocr_text = pytesseract.image_to_string(image)

        # Regex: find “CIS-” followed by digits
        pattern = r"CIS-(\d+)"
        found_numbers = re.findall(pattern, ocr_text)

        # Add each newly found number (digits only) to st.session_state
        if found_numbers:
            for number in found_numbers:
                if number not in st.session_state["cis_numbers"]:
                    st.session_state["cis_numbers"].append(number)

    # 4) Display the stored CIS numbers in two ways

    st.write("### 1) Vertical List (with remove buttons)")

    # We'll gather indices for removal if the user clicks an X button
    indices_to_delete = []
    for idx, num in enumerate(st.session_state["cis_numbers"]):
        cols = st.columns([4, 1])  
        with cols[0]:
            st.write(num)  # Show the number (digits only)
        with cols[1]:
            if st.button("X", key=f"del_{idx}"):
                indices_to_delete.append(idx)

    # Remove any numbers requested for deletion
    if indices_to_delete:
        # Remove from the end to avoid messing up indexes
        for i in sorted(indices_to_delete, reverse=True):
            st.session_state["cis_numbers"].pop(i)
        st.experimental_rerun()

    st.write("### 2) Horizontal (comma-separated) List")
    if st.session_state["cis_numbers"]:
        # Join them with commas, no spaces
        csv_list = ",".join(st.session_state["cis_numbers"])
        st.write(csv_list)
    else:
        st.write("No numbers collected yet.")
