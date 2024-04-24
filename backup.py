import streamlit as st
import os
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Web app",
    layout="wide"
)

# title for the web app
st.title("File Uploader")


# Upload file
def upload_file():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        try:
            # path to the "images" folder
            images_folder = os.path.abspath("D:\Data_Analytics\streamlit\images")
            st.write("Absolute path to 'images' folder:", images_folder)

            # Check if the folder exists
            if not os.path.exists(images_folder):
                st.error("Error: 'images' folder does not exist.")
                return

            # Save the file to the "images" folder
            file_path = os.path.join(images_folder, uploaded_file.name)
            st.write("Saving file to:", file_path)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


def folder_exists(folder_path):
    return os.path.exists(folder_path) and os.path.isdir(folder_path)


def check_folder():
    if folder_exists("images"):
        print("The 'images' folder exists.")
    else:
        print("The 'images' folder does not exist.")


if st.button("Check Folder"):
    check_folder()

# Button to upload file
if st.button("Upload File"):
    upload_file()
