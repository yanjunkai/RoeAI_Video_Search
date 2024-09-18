# Overview
This project is a full-stack application designed to upload videos, extract frames, and search for relevant frames 
based on a natural language query. It uses Next.js and React for the frontend and Django REST Framework for the backend.
The core of the search functionality is powered by OpenAI's CLIP (Contrastive Language–Image Pretraining) model, 
which allows users to find frames in a video that semantically match their search query.


## Key Features
### Video Upload:
- Users can upload videos via the frontend UI, and the backend will extract frames at regular intervals. 
- The backend uses OpenCV to process the video and extract frames.

### Search Functionality:
- Users can search for frames using natural language. 
- The search query is embedded using CLIP, and the system matches it with pre-computed embeddings for video frames.
The top 5 frames, ranked by similarity to the query, are returned.

### Backend:
- Built with Django REST Framework for handling video uploads and frame search. 
- Frames are embedded using CLIP during upload and stored in the database.
- Search functionality compares the user's query embedding with frame embeddings using cosine similarity.

### Frontend:
- Built with Next.js for a responsive and fast interface.
- Users can upload videos, track upload progress, and search for specific frames. 
- Results are displayed with the frame images and similarity scores.

## Project Structure

### Backend
```
video_search/
│
├── backend/
│   ├── models.py            # Defines the Video model for storing video files and their frame data
│   ├── views.py             # Handles API views for video uploads and search functionality
│   ├── urls.py              # URL routing for API endpoints in the backend app
│   ├── app.py               # Backedn config
│
├── media/                   # Stores uploaded videos and extracted video frames
│   ├── frames/              # Frames extracted from videos are saved here
│   ├── videos/              # Uploaded video files are saved here
│
├── video_search/
│   ├── settings.py          # Django settings for the entire project, including configuration for apps, middleware, and database
│   ├── urls.py              # Main URL routing for the project, which includes routing to the `backend` app's URLs
│
├── manage.py                # Django management script to run commands like runserver, makemigrations, migrate

```

### Frontend
```
video_search_app/
│
├── /pages/
│   └── index.tsx             # Main user interface with upload and search functionality
│
├── /public/
│   └── favicon.ico           # Favicon for the app
│
├── /styles/
│   └── globals.css           # Global styles for the app
│
└── package.json              # Project dependencies and scripts
```

## Installation
### Backend Setup
#### Clone the repository:
```
git clone https://github.com/yanjunkai/RoeAI_Video_Search
cd RoeAI_Video_Search
```
#### Set up a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies:
```
pip install torch transformers opencv-python pillow django djangorestframework django-cors-headers django-extensions
```

#### Run migrations:
```
cd video_search
python manage.py makemigrations
python manage.py migrate
```
#### Start the Django server:
```
python manage.py runserver
```
Check that the server is running by navigating to http://127.0.0.1:8000.

### Frontend Setup
#### Install frontend dependencies: Navigate to the frontend directory and run:
```
cd video_search_app
npm install
```

#### Start the development server:
```
npm run dev
```
Access the application at http://localhost:3000.

#### Play with it
- In the application http://localhost:3000. Upload the selected video under your local storage.
  - A sample video is stored in /sample_videos. Title is required. 
  - You can also choose other videos locally. Note it is not supported to upload videos > 3mins.
  - There will be an explicit message showed once the video is successfully uploaded.
- In the search bar
  - Try any sentences like `Show me something green` or `I like Rabbit`.
  - The app will show the TOP5 relevant frames together with the similarity value accordingly.



## Future Enhancements
### Deduplication:
Optionally, deduplicate frames based on the frame embedding or perceptual hashing to ensure that similar frames are not returned multiple times.
More Advanced Video Processing:

### Customed retrival settings
Optionally, the app can support customed number of relevant returning frames or the threshold of similarity.

### Implement object tracking or scene detection for more accurate frame extraction.
Consider processing audio content to enrich frame descriptions.