import streamlit as st
import requests
import base64
import os
import uuid
from db import create_user, verify_user, save_video_record, get_user_videos, get_user_stats, get_user_video_timeline, get_recent_videos
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="MAVISE AI", page_icon="🎙️", layout="wide")

# Initialize session state for Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# Custom CSS for glassmorphism, animated backgrounds, and dynamic aesthetics
st.markdown("""
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
/* Animated Gradient Background */
.stApp { background: linear-gradient(-45deg, #0f172a, #1e1b4b, #2e1065, #0f172a) !important; background-size: 400% 400% !important; animation: gradientBG 15s ease infinite !important; color: white; }
@keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
/* Floating Orbs in Background */
.orb { position: fixed; border-radius: 50%; filter: blur(100px); z-index: 0; opacity: 0.6; animation: float 10s infinite ease-in-out alternate; pointer-events: none; }
.orb-1 { width: 400px; height: 400px; background: #4facfe; top: -100px; left: -100px; }
.orb-2 { width: 500px; height: 500px; background: #764ba2; bottom: -150px; right: -100px; animation-delay: -5s; }
@keyframes float { 0% { transform: translateY(0px) scale(1); } 100% { transform: translateY(50px) scale(1.1); } }
/* Dynamic Glass Panels with Fade-In */
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
.glass-panel { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); border-top: 1px solid rgba(255, 255, 255, 0.2); padding: 2.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 2rem; animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; transition: transform 0.4s ease, box-shadow 0.4s ease, background 0.4s ease; position: relative; z-index: 1; }
.glass-panel:hover { transform: translateY(-8px); box-shadow: 0 15px 45px rgba(0, 240, 255, 0.15); background: rgba(255, 255, 255, 0.05); }
/* Animated Gradient Text */
@keyframes shine { to { background-position: 200% center; } }
.gradient-text { background: linear-gradient(to right, #4facfe, #00f2fe, #4facfe); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; font-weight: 800; margin-bottom: 0; animation: shine 3s linear infinite; }
h1, h2, h3, p { color: #e2e8f0 !important; }
/* Pulsing & Glowing Buttons */
.stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 700; border-radius: 12px; border: none; padding: 0.6rem 2rem; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4); }
.stButton>button:hover { transform: translateY(-4px) scale(1.03); box-shadow: 0 12px 25px rgba(118, 75, 162, 0.6); background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); }
/* Style text inputs */
.stTextInput>div>div>input { background-color: rgba(255, 255, 255, 0.05) !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 8px !important; transition: all 0.3s ease !important; }
.stTextInput>div>div>input:focus { border-color: #4facfe !important; box-shadow: 0 0 10px rgba(79, 172, 254, 0.5) !important; }
</style>
""", unsafe_allow_html=True)

SAVED_VIDEOS_DIR = "saved_videos"
os.makedirs(SAVED_VIDEOS_DIR, exist_ok=True)

# ----- Top Navigation Bar -----
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Analytics Dashboard"

if st.session_state.logged_in:
    nav_cols = st.columns([2, 1.2, 1, 1.2, 0.8, 1])
    with nav_cols[0]:
        st.markdown("<h2 style='margin: 0; color: #e2e8f0; padding-top: 0.2rem;'>MAVISE AI 🎙️</h2>", unsafe_allow_html=True)
    with nav_cols[1]:
        if st.button("Analytics Dashboard", use_container_width=True, type="primary" if st.session_state.current_nav == "Analytics Dashboard" else "secondary"):
            st.session_state.current_nav = "Analytics Dashboard"
            st.rerun()
    with nav_cols[2]:
        if st.button("Enhance Studio", use_container_width=True, type="primary" if st.session_state.current_nav == "Enhance Studio" else "secondary"):
            st.session_state.current_nav = "Enhance Studio"
            st.rerun()
    with nav_cols[3]:
        if st.button("My Saved Videos", use_container_width=True, type="primary" if st.session_state.current_nav == "My Saved Videos" else "secondary"):
            st.session_state.current_nav = "My Saved Videos"
            st.rerun()
    with nav_cols[4]:
        if st.button("Logout", use_container_width=True):
            st.session_state.current_nav = "Logout"
            st.rerun()
    with nav_cols[5]:
        st.markdown(f"<div style='color: #94a3b8; padding-top: 0.8rem; text-align: right;'><b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
        
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 2rem; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    nav = st.session_state.current_nav
else:
    nav = "Login"
# ----- Page Routing -----
if nav == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()

elif nav == "Login":
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    st.markdown('<h1 class="gradient-text">Welcome to MAVISE</h1>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.4rem; font-weight: 300; color:#cbd5e1; margin-bottom:2rem; letter-spacing: 1px;'>Clarity, Reimagined.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if not st.session_state.show_signup:
            st.subheader("Login")
            l_user = st.text_input("Username", key="l_user")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("Log In", use_container_width=True):
                uid = verify_user(l_user, l_pass)
                if uid:
                    st.session_state.logged_in = True
                    st.session_state.user_id = uid
                    st.session_state.username = l_user
                    st.toast("Logged in successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            if st.button("Create new account", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        else:
            st.subheader("Sign Up")
            r_user = st.text_input("New Username", key="r_user")
            r_pass = st.text_input("New Password", type="password", key="r_pass")
            if st.button("Create Account", use_container_width=True):
                if r_user and r_pass:
                    if create_user(r_user, r_pass):
                        st.toast("Account created successfully! You can now log in.", icon="🎉")
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error("Username already exists.")
                else:
                    st.error("Please provide both username and password.")
            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            if st.button("Already have an account? Log In", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Analytics Dashboard":
    st.markdown('<h1 class="gradient-text">Analytics Dashboard 📊</h1>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem; color:#94a3b8; margin-bottom:2rem;'>Track your system usage and enhancement history.</p>", unsafe_allow_html=True)
    
    # Fetch data
    total_videos = get_user_stats(st.session_state.user_id)
    timeline_data = get_user_video_timeline(st.session_state.user_id)
    recent_vids = get_recent_videos(st.session_state.user_id, limit=5)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
            <div class="glass-panel" style="text-align: center; padding: 1.5rem;">
                <h3 style="color:#94a3b8; font-size:1.1rem; margin-bottom:0.5rem;">Total Enhancements</h3>
                <h1 style="color:#4facfe; font-size:3rem; margin:0;">{total_videos}</h1>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown('''
            <div class="glass-panel" style="text-align: center; padding: 1.5rem;">
                <h3 style="color:#94a3b8; font-size:1.1rem; margin-bottom:0.5rem;">Model Version</h3>
                <h1 style="color:#764ba2; font-size:2.2rem; margin:0; line-height:1.4;">MAVISE v2.1</h1>
            </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown('''
            <div class="glass-panel" style="text-align: center; padding: 1.5rem;">
                <h3 style="color:#94a3b8; font-size:1.1rem; margin-bottom:0.5rem;">System Status</h3>
                <h1 style="color:#10b981; font-size:2.2rem; margin:0; line-height:1.4;">Online 🟢</h1>
            </div>
        ''', unsafe_allow_html=True)
        
    st.markdown("### 📈 Enhancement Activity")
    col_chart, col_recent = st.columns([2, 1], gap="large")
    
    with col_chart:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if timeline_data:
            df = pd.DataFrame(timeline_data, columns=['Date', 'Videos Processed'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            fig = px.area(df, x='Date', y='Videos Processed', 
                          color_discrete_sequence=['#4facfe'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis=dict(showgrid=False, title="Date"),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Videos Enhanced"),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            fig.update_traces(fillcolor='rgba(79, 172, 254, 0.3)', line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activity data yet. Start enhancing videos in the Studio!")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_recent:
        st.markdown('<div class="glass-panel" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#e2e8f0; margin-bottom:1rem;'>🕒 Recent Activity</h4>", unsafe_allow_html=True)
        if recent_vids:
            for fname, c_date, _ in recent_vids:
                # Truncate filename if too long
                short_fname = fname if len(fname) < 20 else fname[:17] + "..."
                date_str = c_date.split(" ")[0] if " " in c_date else c_date
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #764ba2;">
                    <div style="font-weight: 600; color: #e2e8f0;">{short_fname}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">{date_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No recent videos.")
        st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Enhance Studio":
    st.markdown('<h1 class="gradient-text">Enhance Studio ✨</h1>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem; color:#94a3b8; margin-bottom:2rem;'>Multimodal Audio-Visual Speech Enhancement Workspace.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🎯 Inputs")
        st.markdown("<p style='color:#cbd5e1'>Upload noisy video of a person speaking to isolate and enhance their voice using visual cues (Lip Reading).</p>", unsafe_allow_html=True)
        
        input_method = st.radio("Choose Video Source", ["📁 Upload File", "📷 Record from Camera"], horizontal=True)
        
        video_file = None
        if input_method == "📁 Upload File":
            video_file = st.file_uploader("Upload Video File (MP4, AVI, WEBM)", type=["mp4", "avi", "mov", "webm"])
        else:
            # Inject JS to style the file uploader as a camera button and add capture attribute
            components.html("""
            <style>
                body { margin: 0; background: transparent; }
                .cam-btn {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    border-radius: 16px;
                    width: 150px;
                    height: 110px;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(118,75,162,0.5);
                    transition: all 0.3s ease;
                    border: none;
                    font-family: sans-serif;
                }
                .cam-btn:hover { transform: translateY(-4px) scale(1.04); box-shadow: 0 12px 30px rgba(118,75,162,0.7); }
                .cam-icon { font-size: 42px; margin-bottom: 6px; }
                .cam-text { font-size: 14px; font-weight: 700; }
                input[type=file] { display: none; }
                #status { color: #10b981; font-weight: 700; margin-top: 12px; font-size: 15px; display: none; font-family: sans-serif; }
            </style>
            <label class="cam-btn" for="camInput">
                <span class="cam-icon">&#128247;</span>
                <span class="cam-text">Open Camera</span>
                <input type="file" id="camInput" accept="video/*" capture="camcorder">
            </label>
            <div id="status"></div>
            <script>
                document.getElementById('camInput').addEventListener('change', function(e) {
                    var f = e.target.files[0];
                    if (f) {
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('status').innerText = '\u2705 ' + f.name + ' selected!';
                    }
                });
            <\/script>
            """, height=160)
            st.info("📷 Click the camera button above, then use the file uploader below to submit your recorded video.")
            video_file = st.file_uploader("Upload Recorded Video", type=["mp4", "mov", "webm", "avi"], label_visibility="collapsed")

        audio_file = st.file_uploader("Upload External Noisy Audio (Defaults to video's track)", type=["wav", "mp3"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("⚙️ Advanced Processing Settings (Studio Features)"):
            st.slider("Noise Reduction Aggressiveness", min_value=0.0, max_value=1.0, value=0.8, step=0.1)
            st.selectbox("AI Model Selection", ["MAVISE v2.1 (Recommended)", "MAVISE v1.0 (Legacy)"])
            st.checkbox("Enable High-Fidelity Audio Output", value=True)
        
        if video_file is not None:
            st.video(video_file)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Enhance Speech Now", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.markdown("**🧠 Initializing Deep Learning Encoders...**")
                time.sleep(0.5)
                progress_bar.progress(30)
                status_text.markdown("**⚙️ Processing Audio-Visual Features...**")
                
                api_url = "http://localhost:8000/enhance"
                files = {"video": (video_file.name, video_file.getvalue(), "video/mp4")}
                if audio_file is not None:
                    files["audio"] = (audio_file.name, audio_file.getvalue(), "audio/wav")
                try:
                    response = requests.post(api_url, files=files)
                    progress_bar.progress(80)
                    status_text.markdown("**✨ Finalizing Output...**")
                    time.sleep(0.5)
                    if response.status_code == 200:
                        # v2 API returns JSON with video_url and subtitle_url
                        result_json = response.json()
                        video_url = result_json.get("video_url")
                        subtitle_url = result_json.get("subtitle_url")
                        
                        # Download the enhanced video from API
                        base_api = "http://localhost:8000"
                        video_resp = requests.get(f"{base_api}{video_url}")
                        st.session_state["enhanced_video"] = video_resp.content
                        
                        # Download subtitles if available
                        if subtitle_url:
                            try:
                                vtt_resp = requests.get(f"{base_api}{subtitle_url}")
                                st.session_state["subtitles_vtt"] = vtt_resp.text
                            except:
                                st.session_state["subtitles_vtt"] = None
                        else:
                            st.session_state["subtitles_vtt"] = None
                            
                        st.session_state["success"] = True
                        st.session_state["video_name"] = video_file.name
                        progress_bar.progress(100)
                        status_text.markdown("**✅ Enhancement Complete!**")
                        st.toast("Enhancement complete!", icon="✅")
                    else:
                        st.error(f"Error from API: {response.text}")
                        status_text.empty(); progress_bar.empty()
                except Exception as e:
                    st.error(f"Failed to connect to Local API: {e}. Make sure you run 'uvicorn api.main:app' in your backend terminal.")
                    status_text.empty(); progress_bar.empty()
        elif audio_file is not None:
            st.warning("⚠️ MAVISE is a **Multi-Modal AI**! It strictly requires the speaker's **Video File** (for Lip Reading) to reconstruct the voice. Please upload the Video file first to unlock the engine.")

    with col2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🎵 Enhanced Output")
        
        if "enhanced_video" in st.session_state and st.session_state.get("success"):
            st.success("✅ Speech enhancement and merging complete!")
            st.markdown("**Clean Video Output:**")
            
            # Play with subtitles if available
            subtitles = None
            if st.session_state.get("subtitles_vtt"):
                import io
                subtitles = {"English": io.BytesIO(st.session_state["subtitles_vtt"].encode('utf-8'))}
            st.video(st.session_state["enhanced_video"], format="video/mp4", subtitles=subtitles)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    label="⬇️ Download Video",
                    data=st.session_state["enhanced_video"],
                    file_name=f"enhanced_{st.session_state.get('video_name', 'video.mp4')}",
                    mime="video/mp4",
                    use_container_width=True
                )
            with col_b:
                if st.button("💾 Save to Account", use_container_width=True, key="save_btn"):
                    save_name = f"enhanced_{uuid.uuid4().hex[:8]}.mp4"
                    save_path = os.path.join(SAVED_VIDEOS_DIR, save_name)
                    with open(save_path, "wb") as f:
                        f.write(st.session_state["enhanced_video"])
                        
                    # Save subtitles if they exist
                    vtt_content = st.session_state.get("subtitles_vtt")
                    if vtt_content:
                        vtt_save_path = save_path.replace(".mp4", ".vtt")
                        with open(vtt_save_path, "w", encoding="utf-8") as f:
                            f.write(vtt_content)
                            
                    save_video_record(st.session_state.user_id, st.session_state.get("video_name", "Unknown.mp4"), save_path)
                    st.toast("Video saved to your account history! View it in the 'My Saved Videos' tab.", icon="💾")
        else:
            st.info("Awaiting video upload and processing... ⏳")
            st.image("https://images.unsplash.com/photo-1516280440502-86f3750eb363?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif nav == "My Saved Videos":
    st.markdown('<h1 class="gradient-text">My Saved Videos 🗂️</h1>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem; color:#94a3b8; margin-bottom:2rem;'>Your history of enhanced videos.</p>", unsafe_allow_html=True)
    
    videos = get_user_videos(st.session_state.user_id)
    if not videos:
        st.info("You haven't saved any enhanced videos yet.")
    else:
        # Create a grid layout for videos
        cols = st.columns(2)
        for idx, (vid_id, og_name, file_path, created_at) in enumerate(videos):
            with cols[idx % 2]:
                st.markdown('<div class="glass-panel" style="padding: 1.5rem;">', unsafe_allow_html=True)
                st.subheader(f"📄 {og_name}")
                st.write(f"**Saved on:** {created_at}")
                if os.path.exists(file_path):
                    # Load subtitles if VTT exists
                    vtt_path = file_path.replace(".mp4", ".vtt")
                    subtitles = None
                    if os.path.exists(vtt_path):
                        with open(vtt_path, "rb") as f:
                            subtitles = {"English": f.read()}
                    st.video(file_path, subtitles=subtitles)
                    
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Video",
                            data=f.read(),
                            file_name=f"history_{og_name}",
                            mime="video/mp4",
                            key=f"dl_{vid_id}",
                            use_container_width=True
                        )
                else:
                    st.error("Video file not found on disk.")
                st.markdown('</div>', unsafe_allow_html=True)
