import streamlit as st
import os

import subprocess
import uuid
import time
import os.path
from streamlit import session_state
import PIL

import psycopg2
from psycopg2 import sql
from ultralytics import YOLO

# Local Modules
import settings


# import helper

def get_trained_model(folder_path):
    folder_names = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    return folder_names


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
        # host='rds ??',
        host='localhost',
        port=5432,
        database='capstone',
        user='postgres',
        password='12345trewq'
    )
    return connection


# Function to check the database status
def check_database_status():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        # Execute a sample query to check the status
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        return f"Database status: Connected, Result: {result[0]}"

    except Exception as e:
        return f"Database status: Error - {str(e)}"

    finally:
        if conn:
            conn.close()


def update_database2(session_id, filename, predicted_value):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        insert_query = sql.SQL("INSERT INTO result (uuid, filename, predicted_value) VALUES (%s, %s, %s)")
        cursor.execute(insert_query, (session_id, filename, predicted_value))

        connection.commit()
    except Exception as e:
        print(f"Error updating database: {str(e)}")
    finally:
        if connection:
            connection.close()


def update_truth_variable(truth_var, session_id):
    try:
        connection = connect_to_db()  # Assuming you have a function to establish the connection
        cursor = connection.cursor()
        update_query = sql.SQL("UPDATE result SET truth = %s WHERE uuid= %s")
        cursor.execute(update_query, (truth_var, session_id))
        connection.commit()
    except Exception as e:
        print(f"Error updating database: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if 'session_id' not in st.session_state:  # Check if it exists already
    st.session_state.session_id = str(uuid.uuid4())

choice = st.sidebar.radio(
    "Choose features ", ["Yolov8", "Update Database", "Train Model", "About"])

st.title("Streamlit Webapp")
# menu = ["Yolov8", "Update Database", "Train Model", "About"]
# choice = st.sidebar.selectbox("Menu", menu)

training_result_path = "waste-detection/training_results/"  # Specify the path to your directory here

selected_model = st.sidebar.selectbox("Select a folder", get_trained_model(
    training_result_path))  # choose model format  train_<numb>batch_<numb>epoch

# Sidebar slider
confidence = float(st.sidebar.slider(
    "Select Model Confidence", 0, 100, 40)) / 100

if choice == "Yolov8":
    source_img = st.sidebar.file_uploader("Choose an image...", type=("jpg", "jpeg", "png"))
    st.info("Waste detection by Yolov8")
    # session_id = str(uuid.uuid4())

    detect_button = st.sidebar.button('Detect Objects')
    col1, col2 = st.columns(2)
    with col1:
        try:
            if source_img is None:
                default_image_path = str(settings.DEFAULT_IMAGE)
                default_image = PIL.Image.open(default_image_path)
                # st.write("session_id", session_id)
                st.info("Default Imag")
                st.image(default_image_path, caption="Default Image", use_column_width=True)
            else:
                uploaded_image = PIL.Image.open(source_img)
                st.image(source_img, caption="Uploaded Image", use_column_width=True)
                if st.button('Save Images'):
                    save_uploaded_file(source_img, st.session_state.session_id)
                    print("File saved successfully. Performing detection for session:", st.session_state.session_id)
                    st.write("File saved successfully. Performing detection for session:", st.session_state.session_id)
        except Exception as ex:
            st.error("Error occurred while opening the image.")
            st.error(ex)
    with col2:
        if source_img is None:
            default_detected_image_path = str(settings.DEFAULT_DETECT_IMAGE)
            default_detected_image = PIL.Image.open(default_detected_image_path)
            st.info("Default Detected Image")
            st.image(default_detected_image_path, caption='Detected Image',
                     use_column_width=True)
        else:
            if 'detected_images' not in st.session_state:  # Initialize if not present
                st.session_state.detected_images = []
                st.session_state.class_objects = []
                st.session_state.predicted_values = []
            image_container = st.empty()
            if detect_button:

                # Perform detection
                yolo = YOLO(f'{training_result_path}{selected_model}/weights/best.pt')
                # Create a subfolder for predictions
                session_prediction_folder = os.path.join('runs', 'detect', st.session_state.session_id)
                os.makedirs(session_prediction_folder, exist_ok=True)
                source_predict = os.path.join("uploads", st.session_state.session_id)
                print("Waiting for creating folder")
                print("Project folder: ", session_prediction_folder)
                print("Source folder: ", source_predict)
                if os.path.exists(session_prediction_folder):
                    print("Folder created successfully:", session_prediction_folder)
                    print("Ready to run prediction")
                    detection = yolo.predict(source=source_predict, save=True, conf=0.01,
                                             project=session_prediction_folder)
                else:
                    print("Folder creation failed:", session_prediction_folder)

                prediction_result_folder = os.path.join('runs', 'detect', st.session_state.session_id, 'predict')
                image_filenames = [filename for filename in os.listdir(prediction_result_folder) if
                                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
                st.session_state.detected_images = []
                st.session_state.predicted_values = []
                st.session_state.class_objects = []

                for image in image_filenames:
                    st.session_state.detected_images.append(f'{prediction_result_folder}/{image}')
                    # st.image(f'{prediction_result_folder}/{image}', caption="Detected Image", use_column_width=True)

                for result in detection:
                    if result:
                        boxes = result.boxes
                        # class_prob = result.probs
                        # st.write("boxes:", boxes)  # names: {0: 'organic', 1: 'landfill', 2: 'plastic', 3: 'refundable'}
                        for box in boxes:
                            if box:
                                if box.cls == 0:
                                    st.info("organic")
                                    st.write(box.cls.item())
                                    class_object = "Organic"
                                    st.info("Confidence")
                                    predicted_value = round(box.conf.item(), 3)
                                    st.write(predicted_value)
                                    st.session_state.predicted_values.append(predicted_value)
                                    st.session_state.class_objects.append(class_object)
                                elif box.cls == 1:
                                    st.info("landfill")
                                    st.write(box.cls.item())
                                    class_object = "Landfill"
                                    st.info("Confidence")
                                    predicted_value = round(box.conf.item(), 3)
                                    st.write(predicted_value)
                                    st.session_state.predicted_values.append(predicted_value)
                                    st.session_state.class_objects.append(class_object)
                                elif box.cls == 2:
                                    st.info("Plastic")
                                    st.write(box.cls.item())
                                    class_object = "Plastic"
                                    st.info("Confidence")
                                    predicted_value = round(box.conf.item(), 3)
                                    st.write(predicted_value)
                                    st.session_state.predicted_values.append(predicted_value)
                                    st.session_state.class_objects.append(class_object)
                                else:
                                    st.info("Refundable")
                                    st.write(box.cls.item())
                                    class_object = "Refundable"
                                    st.info("Confidence")
                                    predicted_value = round(box.conf.item(), 3)
                                    st.write(predicted_value)
                                    st.session_state.predicted_values.append(predicted_value)
                                    st.session_state.class_objects.append(class_object)

                image_container.empty()
                for i in range(len(st.session_state.detected_images)):
                    image_container.image(st.session_state.detected_images[i], use_column_width=True)
                    # caption=f"Predicted Value: {st.session_state.predicted_values[i]}",
                    # use_column_width=True)

                update_database2(st.session_state.session_id, source_img.name, predicted_value)
            if len(st.session_state.detected_images) > 0:
                for i in range(len(st.session_state.detected_images)):
                    image_container.image(st.session_state.detected_images[i], use_column_width=True)
                    # caption=f"Predicted Value: {st.session_state.predicted_values[i]}",
                    # use_column_width=True)
    # if detect_button:
    truth_var = st.radio(
        "Verify your prediction result, correct = 1, wrong = 0", ["1", "0"])
    truth_button = st.button('Update Truth Value')
    if truth_button:
        update_truth_variable(truth_var, st.session_state.session_id)
        st.success("Truth variable updated!")

elif choice == "Update Database":
    st.subheader("Database Connection")
    db_status = check_database_status()
    if "Connected" in db_status:
        st.success("Database is available")
    else:
        st.error("Database is down")
    #st.write(db_status)

elif choice == "Train Model":
    st.warning("Check the jupiter file to train model")
else:
    st.subheader("About")
    st.info("Streamlit web application")
