import streamlit as st
import os
from PIL import Image
import psycopg2
from psycopg2 import sql
from ultralytics import YOLO
from streamlit import session_state

import uuid
import time
import os.path
import ultralytics
import subprocess


# Function to save uploaded image to server
def save_uploaded_file(uploaded_file, session_uuid):
    save_dir = os.path.join("uploads", session_uuid)
    os.makedirs(save_dir, exist_ok=True)
    try:
        # Save the file with the uploads directory
        with open(os.path.join(save_dir, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True  # Success
    except Exception as e:
        print(f"Error saving file: {e}")
        return False  # Failure


def connect_to_db():
    connection = psycopg2.connect(
        host='',
        port=5432,
        database='postgres',
        user='postgres',
        password=''
    )
    return connection


# Function to check the database status
def check_database_status():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Execute a sample query to check the status
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        return f"Database status: Connected, Result: {result[0]}"

    except Exception as e:
        return f"Database status: Error - {str(e)}"

    finally:
        if connection:
            connection.close()


def update_database(filename):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        #        insert_query = sql.SQL("INSERT INTO record (filename) VALUES ({})").format(sql.Literal(file.filename))
        #        cursor.execute(insert_query)

        insert_query = sql.SQL('INSERT INTO test.result ("FILENAME") VALUES ({})').format(
            sql.Literal(filename)
        )
        cursor.execute(insert_query)

        # Commit the changes to the database
        connection.commit()

    except Exception as e:
        # Handle the exception (e.g., log the error)
        print(f"Error updating database: {str(e)}")

    finally:
        if connection:
            connection.close()


def get_trained_model(folder_path):
    folder_names = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    return folder_names


def get_latest_prediction(path):
    #path = 'runs/detect'
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    newest_folder = max(folders, key=lambda x: os.path.getctime(os.path.join(path, x)))
    return newest_folder


def main():
    st.title("Streamlit Webapp")
    menu = ["Upload Image", "Check DBConnection", "Yolov8", "About"]
    choice = st.sidebar.selectbox("Menu", menu)
    # Generate a unique session ID
    session_id = str(uuid.uuid4())

    if choice == "Upload Image":
        st.subheader("Home")
        image_file = st.file_uploader("Upload Image", type=['png', 'jpeg', 'jpg'])
        if image_file is not None:
            # Display uploaded image
            file_details = {"Filename": image_file.name, "FileType": image_file.type, "FileSize": image_file.size}
            st.write(file_details)
            st.image(image_file, caption="Uploaded Image", use_column_width=True)
            # Save the uploaded file
            save_button = st.button("Save File")
            if save_button:
                if save_uploaded_file(image_file, session_id):

                    session_state[session_id] = {'filename': image_file.name}  # Store filename for this session
                    print("File saved successfully. Performing detection for session:", session_id)
                    st.write(st.session_state)
                else:
                    print("File save failed.")

    elif choice == "Check DBConnection":
        st.subheader("Database Connection")
        db_status = check_database_status()
        st.write(db_status)

    elif choice == "Yolov8":
        st.subheader("Waste detection by Yolov8")
        training_result_path = "waste-detection/training_results/"  # Specify the path to your directory here
        #session_id = str(uuid.uuid4())

        selected_model = st.selectbox("Select a folder", get_trained_model(training_result_path))   # choose model format  train_<numb>batch_<numb>epoch
        st.write(f"You selected: {selected_model}")

        if 'file_uploaded' not in st.session_state:
            st.session_state.file_uploaded = False

        # upload / show the images for predicting
        image_file = st.file_uploader("Upload Image", type=['png', 'jpeg', 'jpg'])

        st.info("Waiting for choosing image")
        if image_file is not None:
            # Display uploaded image
            file_details = {"Filename": image_file.name, "Type": image_file.type}
            st.write(file_details)
            st.image(image_file, caption="Uploaded Image", use_column_width=True)
            # Save the uploaded file
            save_button = st.button("Save File")
            if save_button:
                if save_uploaded_file(image_file, session_id):
                    session_state[session_id] = {'filename': image_file.name}  # Store filename for this session
                    st.session_state.file_uploaded = True
                    print("File saved successfully. Performing detection for session:", session_id)
                    st.write("File saved successfully. Performing detection for session:", session_id)
                    time.sleep(5)
                else:
                    print("File save failed. Cannot proceed with detection.")
                    exit(1)
            if st.session_state.file_uploaded:
                st.info("Ready to run prediction")
                # Perform detection
                yolo = YOLO(f'{training_result_path}{selected_model}/weights/best.pt')
                # Create a subfolder for predictions
                session_prediction_folder = os.path.join('runs', 'detect', session_id)
                os.makedirs(session_prediction_folder, exist_ok=True)
                source_predict = os.path.join("uploads", session_id)
                time.sleep(5)
                st.info("Waiting for creating folder")
                st.write("Project folder: ", session_prediction_folder)
                st.write("Source folder: ", source_predict)

                if os.path.exists(session_prediction_folder):
                    print("Folder created successfully:", session_prediction_folder)
                    detection = yolo.predict(source=source_predict, save=True, conf=0.01, project=session_prediction_folder)  # Save predictions in session folder
                else:
                    print("Folder creation failed:", session_prediction_folder)

                st.write("Detection Result:")

                time.sleep(5)
                # Retrieve prediction results from the session-specific folder
                #predict_path = get_latest_prediction('runs/detect')
                # st.info('The prediction result:' + predict_path)
                prediction_result_folder = os.path.join('runs', 'detect', session_id, 'predict')
                image_filenames = [filename for filename in os.listdir(prediction_result_folder) if
                                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for image in image_filenames:
                    st.write(image)
                    st.image(f'{prediction_result_folder}/{image}', caption="Uploaded Image", use_column_width=True)

    else:
        st.subheader("About")
        st.info("Testing Streamlit app")
        session_id = str(uuid.uuid4())
        st.write("Performing detection for session:  " + session_id)
        training_result_path = "waste-detection/training_results/"  # Specify the path to your directory here
        selected_model = st.selectbox("Select a folder", get_trained_model(training_result_path))  # choose model format  train_<numb>batch_<numb>epoch
        st.write(f"You selected: {selected_model}")
        yolo = YOLO(f'{training_result_path}{selected_model}/weights/best.pt')
        detection = yolo.predict(source='uploads', save=True, conf=0.01,project='runs/detect')  # Save predictions in session folder


if __name__ == '__main__':
    main()