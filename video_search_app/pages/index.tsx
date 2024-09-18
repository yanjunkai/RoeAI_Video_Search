import React, { useState } from 'react';
import axios from 'axios';

export default function Home() {
    const [video, setVideo] = useState<File | null>(null);
    const [title, setTitle] = useState('');
    const [uploadStatus, setUploadStatus] = useState<string | null>(null);
    const [uploadProgress, setUploadProgress] = useState<number>(0);
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [searchResult, setSearchResult] = useState<any[]>([]);
    const [error, setError] = useState<string | null>(null);

    const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files ? e.target.files[0] : null;
        if (file) {
            const videoElement = document.createElement('video');
            videoElement.src = URL.createObjectURL(file);

            // Check the duration when video metadata is loaded
            videoElement.onloadedmetadata = () => {
                if (videoElement.duration > 180) {
                    alert('The video is longer than 3 minutes and cannot be uploaded.');
                    setVideo(null);
                } else {
                    setVideo(file); // Only set video if duration is valid
                }
            };
        }
    };

    const handleUpload = async () => {
        if (!video || !title) {
            setUploadStatus('Please provide both a video and title.');
            return;
        }

        const formData = new FormData();
        formData.append('video', video);
        formData.append('title', title);

        try {
            const res = await axios.post('http://localhost:8000/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(percentCompleted);
                }
            });

            if (res.status === 201) {
                setUploadStatus(`Video uploaded successfully: ${res.data.title}`);
                setUploadProgress(0);
            }
        } catch (error) {
            console.error('Upload error:', error);
            setUploadStatus('Video upload failed. Please try again.');
            setUploadProgress(0);
        }
    };

    const handleSearch = async (e: React.MouseEvent<HTMLButtonElement>) => {
        e.preventDefault();
        if (!searchQuery) {
            alert('Please enter a search query.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/search/?query=${searchQuery}`);
            const data = await response.json();

            if (response.status === 200) {
                setSearchResult(data.frames);
                setError(null);
            } else {
                setError(data.message);
                setSearchResult([]);
            }
        } catch (error) {
            console.error('Error during search', error);
            setError('Search failed. Please try again.');
            setSearchResult([]);
        }
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>RoeAI Video Frame Search</h1>

            <div style={styles.uploadContainer}>
                <h2>Upload Video</h2>
                <input
                    type="file"
                    accept="video/*"
                    onChange={handleVideoChange} // Use handleVideoChange for duration check
                    style={styles.input}
                />
                <input
                    type="text"
                    placeholder="Enter video title"
                    onChange={(e) => setTitle(e.target.value)}
                    style={styles.input}
                />
                <button onClick={handleUpload} style={styles.button}>Upload</button>

                {uploadProgress > 0 && (
                    <div style={styles.progressBarContainer}>
                        <progress value={uploadProgress} max="100" style={styles.progressBar}></progress>
                        <p>{uploadProgress}%</p>
                    </div>
                )}

                {uploadStatus && <p style={styles.statusMessage}>{uploadStatus}</p>}
            </div>

            <div style={styles.searchContainer}>
                <h2>Search Video Frames</h2>
                <input
                    type="text"
                    placeholder="Enter your query"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={styles.input}
                />
                <button onClick={handleSearch} style={styles.button}>Search</button>
                {error && <p style={styles.errorMessage}>{error}</p>}
            </div>

            {searchResult.length > 0 ? (
                <div style={styles.resultsContainer}>
                    <h2>Search Results</h2>
                    {searchResult.map((frameData, index) => (
                        <div key={index} style={styles.frameResult}>
                            <img
                                src={`http://localhost:8000/${frameData.frame}`}
                                alt={`Frame ${frameData.frame}`}
                                style={styles.image}
                            />
                            <p>Similarity: {frameData.similarity.toFixed(4)}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <p style={styles.noResultsMessage}>No frames found.</p>
            )}
        </div>
    );
}

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column' as 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        fontFamily: "'Arial', sans-serif",
        backgroundColor: '#f5f5f5',
        color: '#333',
        minHeight: '100vh',
    },
    heading: {
        fontSize: '2.5rem',
        marginBottom: '30px',
    },
    uploadContainer: {
        marginBottom: '40px',
        padding: '20px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        boxShadow: '0 0 10px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '600px',
    },
    searchContainer: {
        marginBottom: '40px',
        padding: '20px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        boxShadow: '0 0 10px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '600px',
    },
    input: {
        display: 'block',
        width: '100%',
        padding: '10px',
        margin: '10px 0',
        fontSize: '1rem',
        borderRadius: '5px',
        border: '1px solid #ccc',
    },
    button: {
        padding: '10px 20px',
        fontSize: '1rem',
        borderRadius: '5px',
        backgroundColor: '#4CAF50',
        color: 'white',
        border: 'none',
        cursor: 'pointer',
    },
    progressBarContainer: {
        marginTop: '20px',
        width: '100%',
        textAlign: 'center',
    },
    progressBar: {
        width: '100%',
        height: '20px',
    },
    statusMessage: {
        marginTop: '10px',
        color: 'green',
    },
    errorMessage: {
        marginTop: '10px',
        color: 'red',
    },
    resultsContainer: {
        padding: '20px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        boxShadow: '0 0 10px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '800px',
    },
    frameResult: {
        marginBottom: '20px',
    },
    image: {
        maxWidth: '300px',
        maxHeight: '200px',
        marginBottom: '10px',
    },
    noResultsMessage: {
        fontSize: '1.2rem',
        color: '#777',
    },
};

