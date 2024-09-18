# Version 1
# import os
# import cv2
# import torch
# import logging
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.core.files.storage import FileSystemStorage
# from .models import Video
#
# logger = logging.getLogger(__name__)
#
# class UploadVideoView(APIView):
#     def post(self, request):
#         logger.info("Upload request received...")
#
#         # Check for video and title in request
#         if 'video' not in request.FILES or 'title' not in request.data:
#             logger.warning("Missing video or title in the request.")
#             return Response({'error': 'Missing video or title'}, status=400)
#
#         video_file = request.FILES['video']
#         title = request.data.get('title')
#
#         # Save the video file to 'media/videos/'
#         fs = FileSystemStorage(location='media/videos/')
#         filename = fs.save(video_file.name, video_file)
#         video_path = fs.path(filename)
#         logger.info(f"Video saved: {video_path}")
#
#         # Extract frames from the video
#         frames_dir = self.extract_frames(video_path)
#
#         # Create a new Video entry in the database
#         video = Video.objects.create(title=title, video_file=filename)
#
#         # Run object detection on the extracted frames
#         detected_objects = self.detect_objects(frames_dir)
#
#         # Save detected objects to the database
#         video.detected_objects = detected_objects
#         video.save()
#
#         logger.info("Video upload and object detection complete.")
#         return Response({
#             'message': 'Video uploaded successfully!',
#             'video_id': video.id,
#             'title': video.title,
#             'detected_objects': detected_objects,
#         }, status=201)
#
#     def extract_frames(self, video_path, frame_interval=30):
#         """Extracts frames from the uploaded video."""
#         output_dir = os.path.join('media', 'frames', os.path.basename(video_path).split('.')[0])
#         os.makedirs(output_dir, exist_ok=True)
#         logger.info(f"Frames will be saved in {output_dir}")
#
#         video = cv2.VideoCapture(video_path)
#         frame_count = 0
#
#         while True:
#             success, frame = video.read()
#             if not success:
#                 break
#
#             # Save one frame every `frame_interval`
#             if frame_count % frame_interval == 0:
#                 frame_path = os.path.join(output_dir, f'frame_{frame_count}.jpg')
#                 cv2.imwrite(frame_path, frame)
#                 logger.debug(f"Frame {frame_count} saved as {frame_path}")
#
#             frame_count += 1
#
#         video.release()
#         return output_dir
#
# class SearchVideoView(APIView):
#     def get(self, request):
#         logger.info('Search request received...')
#         query = request.GET.get('query', '').lower()
#         logger.info(f'Search query: {query}')
#
#         if not query:
#             logger.warning('No search query provided.')
#             return Response({'message': 'No search query provided'}, status=400)
#
#         # Search across all videos
#         all_videos = Video.objects.all()
#         matching_frames = []
#
#         # Loop through each video and search within detected objects
#         for video in all_videos:
#             logger.info(f'Searching in video: {video.title}, path : {video.video_file.path}')
#             for frame_data in video.detected_objects:
#                 logger.info(f'Frame path in data: {frame_data["frame"]}')  # Debugging
#
#                 if any(query in obj for obj in frame_data.get('objects', [])):
#                     # Construct the correct path without duplicating /media/frames/
#                     sub_folder = os.path.splitext(os.path.basename(video.video_file.path))[0]
#                     frame_name = frame_data["frame"]
#
#                     # Construct the full path only if frame_path doesn't start with "/media/frames/"
#                     full_frame_path = f'{sub_folder}/{frame_name}'
#
#                     matching_frames.append({
#                         'video_id': video.id,
#                         'video_title': video.title,
#                         'frame': full_frame_path,  # Correct full path with subfolder
#                     })
#
#         if matching_frames:
#             logger.info(f'Matching frames found: {matching_frames}')
#             return Response({'frames': matching_frames}, status=200)
#         else:
#             logger.info('No matching frames found.')
#             return Response({'message': 'No matching frames found'}, status=404)
#

# Version 2
import os
import cv2
import logging
import torch
import torch.nn.functional as F
import warnings
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import FileSystemStorage
from .models import Video

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=FutureWarning, module='transformers.tokenization_utils_base')

# Load CLIP model and processor once to reuse
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Helper function to generate embeddings for frames using CLIP
def describe_frame(frame_path):
    image = Image.open(frame_path)
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)
    return image_features

# Helper function to generate embeddings for questions using CLIP
def embed_question(question):
    inputs = processor(text=question, return_tensors="pt", padding=True)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    return text_features

class UploadVideoView(APIView):
    def post(self, request):
        logger.info("Upload request received...")
        if 'video' not in request.FILES or 'title' not in request.data:
            return Response({'error': 'Missing video or title'}, status=400)

        video_file = request.FILES['video']
        title = request.data.get('title')

        # Save the video file to 'media/videos/'
        fs = FileSystemStorage(location='media/videos/')
        filename = fs.save(video_file.name, video_file)
        video_path = fs.path(filename)

        # Extract frames from the video
        frames_dir = self.extract_frames(video_path)

        # Create a new Video entry in the database
        video = Video.objects.create(title=title, video_file=filename)

        # Generate embeddings and save detected objects for each frame
        detected_objects = self.generate_frame_embeddings(frames_dir)
        video.detected_objects = detected_objects
        video.save()

        return Response({
            'message': 'Video uploaded successfully!',
            'video_id': video.id,
            'title': video.title,
            'detected_objects': detected_objects,
        }, status=201)

    def extract_frames(self, video_path, frame_interval=30):
        output_dir = os.path.join('media', 'frames', os.path.basename(video_path).split('.')[0])
        os.makedirs(output_dir, exist_ok=True)

        video = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            success, frame = video.read()
            if not success:
                break
            if frame_count % frame_interval == 0:
                frame_path = os.path.join(output_dir, f'frame_{frame_count}.jpg')
                cv2.imwrite(frame_path, frame)
            frame_count += 1

        video.release()
        return output_dir

    def generate_frame_embeddings(self, frames_dir):
        detected_objects = []
        frame_files = os.listdir(frames_dir)

        for frame in frame_files:
            frame_path = os.path.join(frames_dir, frame)
            frame_embedding = describe_frame(frame_path)  # Get embedding using CLIP

            # Convert tensor to list to make it JSON serializable
            frame_embedding_list = frame_embedding.cpu().numpy().tolist()

            detected_objects.append({'frame': frame, 'embedding': frame_embedding_list})
        return detected_objects

class SearchVideoView(APIView):
    def get(self, request):
        question = request.GET.get('query', '').lower()
        logger.info(f"Search request received. Question: {question}")

        if not question:
            return Response({'message': 'No search query provided'}, status=400)

        # Generate the embedding for the question
        question_embedding = embed_question(question)

        # Search across all video frames and compare using cosine similarity
        all_videos = Video.objects.all()
        matching_frames = []

        for video in all_videos:
            for frame_data in video.detected_objects:
                sub_folder = os.path.splitext(os.path.basename(video.video_file.path))[0]
                frame_name = frame_data["frame"]
                full_frame_path = f'media/frames/{sub_folder}/{frame_name}'
                frame_embedding = torch.tensor(frame_data['embedding'])  # Load saved embedding

                similarity = F.cosine_similarity(question_embedding, frame_embedding)
                matching_frames.append({
                    'frame': full_frame_path,
                    'similarity': similarity.item()
                })

        # Sort frames by similarity and return the TOP5 frames.
        matching_frames = sorted(matching_frames, key=lambda x: x['similarity'], reverse=True)[:5]


        if matching_frames:
            logger.info(f'matching_frames: {matching_frames}')
            return Response({'frames': matching_frames})
            # best_match = matching_frames[0]
            # return Response({'frame': best_match['frame'], 'similarity': best_match['similarity']})
        else:
            return Response({'message': 'No matching frames found'}, status=404)
