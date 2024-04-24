import streamlit as st
import os
from PIL import Image


# Function to save uploaded image to server
def save_uploaded_file(uploaded_file):
    os.makedirs("uploads", exist_ok=True)
    # Save the file with the uploads directory
    with open(os.path.join("uploads", uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success("File saved successfully")


def main():
    st.title("Upload File")

    menu = ["Upload Image", "About"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Upload Image":
        st.subheader("Home")
        image_file = st.file_uploader("Upload Image", type=['png', 'jpeg', 'jpg'])
        if image_file is not None:
            # Display uploaded image
            st.image(image_file, caption="Uploaded Image", use_column_width=True)
            # Save the uploaded file
            save_button = st.button("Save File")
            if save_button:
                save_uploaded_file(image_file)

    else:
        st.subheader("About")
        st.info("Testing Streamlit app")


if __name__ == '__main__':
    main()
