import streamlit as st
import re
import pytesseract
from PIL import Image
import io

def camera_data_collection():
    """
    Use camera to scan images for "CIS-####" references.
    Persist scanned digits in st.session_state, so they remain
    even if the user clears the camera photo.
    """

    st.subheader("Test Equipment Scanner")

    # 1) Initialize the list in session_state if it doesn't exist yet
    if "cis_numbers" not in st.session_state:
        st.session_state["cis_numbers"] = []

    # 2) Camera input widget
    captured_image = st.camera_input("Take a picture to scan")

    # 3) If a photo is captured, run OCR to find "CIS-####" patterns
    if captured_image is not None:
        image = Image.open(io.BytesIO(captured_image.getvalue()))
        ocr_text = pytesseract.image_to_string(image)

        pattern = r"CIS-(\d+)"
        found_numbers = re.findall(pattern, ocr_text)

        # Add new digits to the list (skip duplicates if desired)
        for number in found_numbers:
            if number not in st.session_state["cis_numbers"]:
                st.session_state["cis_numbers"].append(number)

    # 4) Let user remove numbers, then show vertical & horizontal lists

    # First, handle removal requests. We'll build a local copy
    # so we can modify st.session_state only after we detect all removals.
    numbers_copy = st.session_state["cis_numbers"].copy()
    indices_to_delete = []

    st.write("### 1) Vertical List (with remove buttons)")
    for idx, num in enumerate(numbers_copy):
        cols = st.columns([4, 1])
        with cols[0]:
            st.write(num)
        with cols[1]:
            if st.button("X", key=f"del_{idx}"):
                indices_to_delete.append(idx)

    # Remove them from session_state
    if indices_to_delete:
        for i in sorted(indices_to_delete, reverse=True):
            st.session_state["cis_numbers"].pop(i)

    # Now reflect the updated list in both vertical & horizontal forms

    st.write("### 2) Horizontal (comma-separated) List")
    if st.session_state["cis_numbers"]:
        csv_list = ",".join(st.session_state["cis_numbers"])
        st.write(csv_list)
    else:
        st.write("No numbers collected yet.")
