from google.cloud import storage
from datetime import timedelta
from app.models import Video

def get_blob_name_from_video_id(video_id, bucket_name):
    video = Video.query.get(video_id)
    if not video:
        return None

    gcs_url = video.gcs_url
    prefix = f"https://storage.googleapis.com/{bucket_name}/"
    return gcs_url.replace(prefix, "")

def generate_signed_url(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    return blob.generate_signed_url(
        expiration=timedelta(minutes=10),
        method="GET",
        version="v4"
    )
