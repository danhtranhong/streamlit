import streamlit as st
import os
from PIL import Image
import psycopg2
from psycopg2 import sql

# Function to save uploaded image to server
def save_uploaded_file(uploaded_file):
    os.makedirs("uploads", exist_ok=True)
    # Save the file with the uploads directory
    with open(os.path.join("uploads", uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success("File saved successfully")

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

def main():
    st.title("Upload File")
    menu = ["Upload Image", "Check DBConnection", "About"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Upload Image":
        st.subheader("Home")
        image_file = st.file_uploader("Upload Image", type=['png', 'jpeg', 'jpg'])
        if image_file is not None:
            # Display uploaded image
            file_details = {"Filename": image_file.name, "FileType": image_file.type, "FileSize": image_file.size}
            st.write(file_details)
            st.image(image_file, caption="Uploaded Image", use_column_width=True)
            # Save the uploaded file
            save_button = st.button("SavTe File")
            if save_button:
                save_uploaded_file(image_file)
            upload_database = st.button("Update Database")
            if upload_database:
                update_database(image_file.name)

    elif choice == "Check DBConnection":
        st.subheader("Database Connection")
        db_status = check_database_status()
        st.write(db_status)
    else:
        st.subheader("About")
        st.info("Testing Streamlit app")


if __name__ == '__main__':
    main()
