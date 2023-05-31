import os
import hashlib
from datetime import datetime
from flask import Flask
from flask import request, jsonify, stream_with_context, Response
from celery import Celery
from celery.utils.log import get_task_logger
from pymongo import MongoClient
from dotenv import load_dotenv

from wrangler import music_play_data

logger = get_task_logger(__name__)


app = Flask(__name__)


load_dotenv()

app.config["CELERY_RESULT_BACKEND"] = os.environ.get("CELERY_RESULT_BACKEND")
app.config["CELERY_BROKER_URL"] = os.environ.get("CELERY_BROKER_URL")

# Initialize Celery
celery = Celery(
    app.name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"]
)
celery.conf.update(app.config)

# Init mongo db
client = MongoClient(os.environ.get("MONGO_URI"))
db = client.app_db


@app.route("/")
def check():
    return jsonify({"message": "Welcome to ping wrangler!!!"})


# Endpoints
@app.route("/upload", methods=["POST"])
def upload():
    md5_hash_obj = hashlib.md5()
    file_path = f"./uploads/raw_{datetime.now().isoformat()}.csv"
    with open(file_path, "bw") as file:
        chunk_size = 4096
        while True:
            chunk = request.stream.read(chunk_size)
            md5_hash_obj.update(chunk)
            if len(chunk) == 0:
                break
            file.write(chunk)
    md5_hash = md5_hash_obj.hexdigest()
    task_id = get_processing_file_task_id(file_path, md5_hash)
    return jsonify({
        "task_id": task_id,
        "hash": md5_hash,
    }, 201)


@app.route("/download/<task_id>")
def download_file(task_id):
    task = db.tasks.find_one({"task_id": task_id})
    if not task:
        return jsonify({
            "message": "Not Found"
        }, 404)
    # Still processing
    status = task.get("status", None)
    if status != "SUCCESS":
        return jsonify({
            "status": status,
            "task_id": task["task_id"]
        }, 200)
    # if is done processing
    file_download_path = task.get("dest_file_path", None)
    if file_download_path:
        return Response(
            stream_with_context(download_file(file_download_path)),
            mimetype='text/csv'
        )


# Helper functions
def get_processing_file_task_id(file_path, file_hash):
    """
    Check if file hash exists, for already processed files
    if the hash doesn't exist for new files.
    Queue if for process and save it's details to the tasks document.
    Returns: task_id 
    """
    task = db.tasks.find_one({"file_hash": file_hash})
    if task:
        task_id = task.get("task_id", None)
    else:
        db.tasks.insert_one({"file_hash": file_hash, "status": "PENDING"})
        task_res = process_music_plays.delay(file_path, file_hash)
        task_id = task_res.id
        db.tasks.update_one(
            {"file_hash": file_hash},
            {"$set": {"task_id": task_id}}
        )
    return task_id


def download_file(path):
    chunk_size = 4096
    with open(path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if len(chunk) == 0:
                break
            yield chunk


# Async tasks
@celery.task()
def process_music_plays(file_path, file_hash):
    dest_file_path = music_play_data(file_path)
    db.tasks.update_one(
        {"file_hash": file_hash},
        {"$set": {
            "dest_file_path": dest_file_path,
            "status": "SUCCESS"
            }
        }
    )
    return dest_file_path


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
