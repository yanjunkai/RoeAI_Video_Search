# Overview
This is a video upload and search application using Django REST Framework on the backend and
CLIP (Contrastive Language–Image Pretraining) from OpenAI for finding video frames based on natural language queries.
The system allows users to upload videos, automatically extracts frames from the video, and generates embeddings
for those frames using CLIP. Users can then perform a natural language search query, and the application returns frames
from the video that are semantically similar to the query.

## Code Breakdown
### Frame Embedding and Search
- CLIP Model:
    - The CLIP model is loaded once and reused to generate embeddings for both frames and text queries.
    - Frame embeddings are calculated using describe_frame() and stored in the database.
    - Search queries are embedded with embed_question() and compared against frame embeddings using cosine similarity.
Cosine Similarity:

- Cosine similarity is calculated between the query embedding and frame embeddings to determine how similar the frames are to the query.
Models 
  - Video Model: Stores video metadata and links to the video file and extracted frames. 
  - Frame Embeddings: Each frame's embedding is stored as part of the detected_objects field in the Video model, along with its file path.

## Running the Project
### Clone the repository:
```
git clone <repo-url>
```
### Install the dependencies:
Ensure you have the following Python libraries installed:
```
cd RoeAI_Video_Search
source venv/bin/activate 
pip install torch transformers opencv-python pillow django djangorestframework django-cors-headers django-extensions
```
- torch: PyTorch, used for loading and running the CLIP model.
- transformers: Hugging Face Transformers, used for loading the CLIP model and processor.
- opencv-python: OpenCV, used for video processing and frame extraction.
- pillow: Used to handle image files.
- django: Web framework to handle the API and database interactions.

### Run migrations:

```
cd video_search
python manage.py makemigrations
python manage.py migrate
```

### Start the Django server:

```
python manage.py runserver
```

### Cleanup videos
```
rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete 
rm -rf media/videos/ media/frames/ 
mkdir -p media/videos/ media/frames/
python manage.py makemigrations
python manage.py migrate
```

## API Endpoints
### Upload Video (POST /upload/):
- Upload a video to the backend, where frames will be extracted and embedded using CLIP.
- Body:
  - video: The video file to upload.
  - title: The title of the video.
- Response: Confirmation of video upload and frame processing.

### Search for Frames (GET /search/):
- Search for frames based on a natural language query.
- Query Parameters:
  - query: The search query (e.g., "a person near a car").
  - Response: A list of the top 5 matching frames with their similarity scores.