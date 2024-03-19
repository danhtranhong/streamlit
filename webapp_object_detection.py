import streamlit as st
import os

# Set up a title for the web app
st.title("File Uploader")


# Function to upload file
def upload_file():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        try:
            # Get the absolute path to the "images" folder
            images_folder = os.path.abspath("images_111")
            st.write("Absolute path to 'images' folder:", images_folder)

            # Check if the folder exists
            if not os.path.exists(images_folder):
                st.error("Error: 'images' folder does not exist.")
                return

            # Save the file to the "images" folder on the web server
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
