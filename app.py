from flask import Flask, render_template, Response
from deepface import DeepFace
import cv2
import time
import mysql.connector
import base64

app = Flask(__name__)

# MySQL connection configuration
mysql_connection = mysql.connector.connect(
    host="",
    port="3307",
    user="root",
    password="",
    database="database"
)

def insert_result_into_database(result):
    cursor = mysql_connection.cursor()

    # Define the MySQL query to insert the result
    insert_query = "INSERT INTO face_recognition_results (age, gender, emotion) VALUES (%s, %s, %s)"

    # Check if result is a list
    if isinstance(result, list):
        for res in result:
            age = res.get('age')
            gender = res.get('dominant_gender')
            dominant_emotion = res.get('dominant_emotion')

            # Check if all values are present
            if age is not None and gender is not None and dominant_emotion is not None:
                # Convert age to int if applicable
                try:
                    age = int(age)
                except ValueError:
                    age = None

                # Convert gender and dominant_emotion to strings
                gender = str(gender)
                dominant_emotion = str(dominant_emotion)

                # Insert data into the database
                if age is not None:
                    values = (age, gender, dominant_emotion)
                    cursor.execute(insert_query, values)
                    mysql_connection.commit()
                else:
                    print("Invalid age value, skipping insertion")
            else:
                print("Missing required data in result, skipping insertion")
    else:
        # Handle the case when result is not a list (assume it's a single dictionary)
        age = result.get('age')
        gender = result.get('gender')
        dominant_emotion = result.get('dominant_emotion')

        # Check if all values are present
        if age is not None and gender is not None and dominant_emotion is not None:
            # Convert age to int if applicable
            try:
                age = int(age)
            except ValueError:
                age = None

            # Convert gender and dominant_emotion to strings
            gender = str(gender)
            dominant_emotion = str(dominant_emotion)

            # Insert data into the database
            if age is not None:
                values = (age, gender, dominant_emotion)
                cursor.execute(insert_query, values)
                mysql_connection.commit()
            else:
                print("Invalid age value, skipping insertion")
        else:
            print("Missing required data in result, skipping insertion")

    # Commit the transaction
    mysql_connection.commit()

def save_image_to_database(image_data):
    cursor = mysql_connection.cursor()

    try:
        # Define the MySQL query to insert the image data
        insert_query = "INSERT INTO captured_images (base64_data, jpeg_data) VALUES (%s, %s)"

        # Encode the image data as base64
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        # Insert both base64 and JPEG data into the database
        cursor.execute(insert_query, (image_data_base64, image_data))
        mysql_connection.commit()
        print("Image saved to database successfully!")
    except mysql.connector.Error as err:
        print(f"Error saving image to database: {err}")
    finally:
        cursor.close()


def save_base64_and_image_to_database(base64_data, jpeg_data):
    cursor = mysql_connection.cursor()

    try:
        # Define the MySQL query to insert both Base64 and JPEG data
        insert_query = "INSERT INTO images (base64_data, jpeg_data) VALUES (%s, %s)"

        # Insert data into the database
        cursor.execute(insert_query, (base64_data, jpeg_data))
        mysql_connection.commit()
        print("Data saved to database successfully!")
    except mysql.connector.Error as err:
        print(f"Error saving data to database: {err}")
    finally:
        cursor.close()

def save_base64_image_and_convert_to_jpeg(base64_data):
    # Decode Base64 data back to binary
    binary_data = base64.b64decode(base64_data)
    
    # Convert binary data to JPEG format
    jpeg_data = binary_data  # In this example, we're keeping the binary data as is
    
    # Save both Base64 and JPEG data to the database
    save_base64_and_image_to_database(base64_data, jpeg_data)

def detect_faces():
    video_capture = cv2.VideoCapture(0)  # Access the webcam (change to the appropriate device index if necessary)

    start_time = time.time()  # Record the start time
    while True:
        _, frame = video_capture.read()  # Read a frame from the webcam

        # Check if 5 seconds have elapsed
        if time.time() - start_time > 5:
            # Stop processing frames after 5 seconds
            break

        # Perform face recognition using DeepFace
        result = DeepFace.analyze(frame)

        # Insert the result into MySQL database
        insert_result_into_database(result)

        # Save the image to the database
        save_image_to_database(cv2.imencode('.jpg', frame)[1].tobytes())

        # Process the result as needed
        # For example, you can print the result to the console
        print(result)

        # Encode the analyzed frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()

        # Yield the frame bytes as a response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Return a response with the streaming video feed
    return Response(detect_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
