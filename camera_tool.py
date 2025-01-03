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

    Now each CIS number in the vertical list is a clickable button:
    when pressed, that number is removed from the list.
    """

    st.subheader("Test Equipment Scanner")

    # 1) Initialize the list in session_state if not present
    if "cis_numbers" not in st.session_state:
        st.session_state["cis_numbers"] = []

    # 2) Camera input
    captured_image = st.camera_input("Take a picture to scan")

    # 3) If a photo is captured, do OCR and find CIS-#### patterns
    if captured_image is not None:
        image = Image.open(io.BytesIO(captured_image.getvalue()))
        ocr_text = pytesseract.image_to_string(image)

        pattern = r"CIS-(\d+)"
        found_numbers = re.findall(pattern, ocr_text)

        # Append new digits to session_state, skipping duplicates if desired
        for number in found_numbers:
            if number not in st.session_state["cis_numbers"]:
                st.session_state["cis_numbers"].append(number)

    # 4) Display the list in two ways:
    #    (A) Vertical List -> each CIS number is now a button that deletes itself
    #    (B) Horizontal comma-separated

    st.write("### 1) Vertical List (each CIS digit is a clickable button)")

    # local copy to display them all
    numbers_copy = st.session_state["cis_numbers"].copy()
    indices_to_delete = []

    for idx, num in enumerate(numbers_copy):
        # Each 'number' is itself a button. If clicked, remove that item.
        if st.button(str(num), key=f"cis_btn_{idx}"):
            # Mark it for deletion
            indices_to_delete.append(idx)

    # Remove any numbers user clicked
    if indices_to_delete:
        for i in sorted(indices_to_delete, reverse=True):
            st.session_state["cis_numbers"].pop(i)

    st.write("### 2) Horizontal (comma-separated) List")
    if st.session_state["cis_numbers"]:
        csv_list = ",".join(st.session_state["cis_numbers"])
        st.write(csv_list)
    else:
        st.write("No numbers collected yet.")
