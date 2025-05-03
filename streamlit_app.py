import streamlit as st
import yt_dlp
import os
from urllib.parse import urlparse, parse_qs
import time
from streamlit_lottie import st_lottie
import json
import requests

# Set page title and icon with wider layout
st.set_page_config(
    page_title="YouTube Video Downloader Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Try to load animations (fallback if not available)
loading_anim = None
success_anim = None
download_anim = None

try:
    loading_anim = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_raiw2hpe.json")
    success_anim = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_pmvvftcc.json")
    download_anim = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_soCRuE.json")
except:
    pass

# Custom CSS for better appearance
st.markdown("""
    <style>
    /* Main container */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #ff4b4b, #ff0000);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #ff4b4b, #ff0000);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 28px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, #ff0000, #cc0000);
    }
    
    /* Download button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 28px;
        font-weight: bold;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #2E7D32, #1B5E20);
    }
    
    /* Input field */
    .stTextInput>div>div>input {
        border-radius: 20px;
        padding: 10px 15px;
    }
    
    /* Progress bar */
    .stProgress>div>div>div>div {
        background: linear-gradient(90deg, #ff4b4b, #ff0000);
    }
    
    /* Card styling for video info */
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    /* Custom spinner */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .custom-spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid rgba(255, 75, 75, 0.3);
        border-radius: 50%;
        border-top: 4px solid #ff4b4b;
        animation: spin 1s linear infinite;
    }
    </style>
    """, unsafe_allow_html=True)

# App title and description with animation
def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="header">
            <h1 style="margin:0; padding:0;">🎬 YouTube Video Downloader Pro</h1>
            <p style="margin:0; padding:0; opacity:0.9;">Download videos from YouTube in various formats and qualities with style!</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if download_anim:
            st_lottie(download_anim, height=100, key="header-anim")

# Function to validate YouTube URL
def is_valid_youtube_url(url):
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.hostname in ('www.youtube.com', 'youtube.com', 'youtu.be'):
        if 'v=' in parsed.query:
            return True
        if parsed.path.startswith('/watch'):
            return True
        if parsed.hostname == 'youtu.be':
            return True
    return False

# Function to extract video info with progress animation
def get_video_info(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            with st.spinner("Fetching video information..."):
                if loading_anim:
                    st_lottie(loading_anim, height=100, key="loading-info")
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

# Function to download video with enhanced progress
def download_video(url, quality, download_path="downloads"):
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1)
            progress_bar.progress(percent)
            status_text.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="custom-spinner"></div>
                <div>
                    Downloading: <b>{d.get('_percent_str', '0%')}</b><br>
                    Speed: {d.get('_speed_str', 'N/A')} | ETA: {d.get('_eta_str', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    ydl_opts = {
        'format': quality,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'progress_hooks': [progress_hook],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Show success animation
            progress_bar.empty()
            status_text.empty()
            if success_anim:
                st_lottie(success_anim, height=150, key="download-success")
            
            return filename
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None

# Main app
def main():
    render_header()
    
    # URL input with nice placeholder
    url = st.text_input(
        "Enter YouTube Video URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        key="url_input"
    )
    
    if url:
        if is_valid_youtube_url(url):
            # Get video info
            video_info = get_video_info(url)
            
            if video_info:
                # Display video info in a card
                with st.container():
                    st.markdown("""<div class="card">""", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.image(
                            video_info.get('thumbnail', ''),
                            width=300,
                            caption="Video Thumbnail",
                            use_column_width=True
                        )
                    
                    with col2:
                        st.subheader(video_info.get('title', 'No title'))
                        st.markdown("---")
                        
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric("Duration", f"{video_info.get('duration', 0) // 60}:{video_info.get('duration', 0) % 60:02d}")
                            st.metric("Uploader", video_info.get('uploader', 'Unknown'))
                        with col_info2:
                            st.metric("Views", f"{video_info.get('view_count', 0):,}")
                            st.metric("Rating", f"{video_info.get('average_rating', 0):.1f}/5" if video_info.get('average_rating') else "N/A")
                        
                        st.markdown("---")
                    
                    st.markdown("""</div>""", unsafe_allow_html=True)
                
                # Get available formats
                formats = []
                if 'formats' in video_info:
                    for f in video_info['formats']:
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':  # Video+audio
                            resolution = f.get('resolution', 'unknown')
                            ext = f.get('ext', 'unknown')
                            format_id = f.get('format_id', 'unknown')
                            filesize = f.get('filesize', 0) or f.get('filesize_approx', 0)
                            filesize_mb = f"{filesize / (1024 * 1024):.1f} MB" if filesize else "unknown"
                            formats.append((f"{resolution} ({ext}) - {filesize_mb}", format_id))
                
                # Remove duplicates and sort
                formats = sorted(list(set(formats)), key=lambda x: x[0], reverse=True)
                
                # Quality selection
                st.subheader("Download Options")
                quality = st.selectbox(
                    "Select Video Quality:",
                    options=[f[1] for f in formats],
                    format_func=lambda x: next((f[0] for f in formats if f[1] == x), x),
                    key="quality_select"
                )
                
                # Download button with animation
                if st.button("🚀 Download Video", key="download_btn"):
                    with st.spinner("Preparing download..."):
                        time.sleep(1)  # Small delay for animation
                    
                    downloaded_file = download_video(url, quality)
                    if downloaded_file:
                        st.balloons()
                        
                        # Offer download button
                        with open(downloaded_file, "rb") as f:
                            st.download_button(
                                label="💾 Save Video to Your Device",
                                data=f,
                                file_name=os.path.basename(downloaded_file),
                                mime="video/mp4",
                                key="final_download"
                            )
        else:
            st.warning("⚠️ Please enter a valid YouTube URL")

if __name__ == "__main__":
    main()
