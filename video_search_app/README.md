# Overview
This is the frontend for the video upload and search application, built with React and Next.js. The frontend allows 
users to upload videos to the backend server and search for specific video frames based on a natural language query. 
This is done using the power of CLIP embeddings on the backend, which match the user's query with extracted video frames.

## Features
### Video Upload:
- Users can upload videos via an intuitive UI. 
- A progress bar is displayed to track the upload process. 
- Once the video is successfully uploaded, a confirmation message is shown.
- It is NOT supported for video which time > 3min.
### Search Functionality:
- Users can enter a natural language query in the search bar. 
- The system fetches the most relevant video frames from the backend based on the query. 
- Results are displayed with frame images and their corresponding similarity scores.
- By default, it returns the TOP5 relevant frames.

## Setup and Installation
### Install Dependencies:
```
npm install
```

### Start the Frontend Development Server:

```
npm run dev
```

### Access the Application: 
Open a browser and navigate to http://localhost:3000 to access the frontend.
