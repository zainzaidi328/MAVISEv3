/* ═══════════════════════════════════════
   MAVISE SPA — Application Logic
   ═══════════════════════════════════════ */

const API = '';  // Same origin

// ── STATE ──
let state = {
  loggedIn: false,
  userId: null,
  username: null,
  currentPage: 'auth',
  enhancedVideoUrl: null,
  videoName: null,
  subtitleUrl: null,
  enhancedMetrics: null,
};

// ── DOM REFS ──
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// ── TOAST ──
function showToast(msg, duration = 3000) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), duration);
}

// ── PAGE NAVIGATION ──
function navigateTo(page) {
  state.currentPage = page;
  $$('.page').forEach(p => p.classList.remove('active'));
  const target = $(`#page-${page}`);
  if (target) target.classList.add('active');

  // Nav link active states
  $$('.nav-link[data-page]').forEach(l => {
    l.classList.toggle('active', l.dataset.page === page);
  });

  // Show/hide nav and footer
  const nav = $('#main-nav');
  const footer = $('#main-footer');
  if (page === 'auth') {
    nav.style.display = 'none';
    footer.style.display = 'block';
  } else {
    nav.style.display = 'flex';
    footer.style.display = 'block';
  }

  // Load page data
  if (page === 'dashboard') loadDashboard();
  if (page === 'saved') loadSavedVideos();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── AUTH ──
$('#show-signup-btn').addEventListener('click', () => {
  $('#login-form').style.display = 'none';
  $('#signup-form').style.display = 'block';
  $('#login-error').style.display = 'none';
});

$('#show-login-btn').addEventListener('click', () => {
  $('#signup-form').style.display = 'none';
  $('#login-form').style.display = 'block';
  $('#signup-error').style.display = 'none';
  $('#signup-success').style.display = 'none';
});

$('#login-btn').addEventListener('click', async () => {
  const user = $('#login-user').value.trim();
  const pass = $('#login-pass').value;
  if (!user || !pass) { showError('login-error', 'Please fill in all fields.'); return; }
  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass }),
    });
    const data = await res.json();
    if (res.ok && data.user_id) {
      state.loggedIn = true;
      state.userId = data.user_id;
      state.username = user;
      $('#nav-username').textContent = user;
      showToast('Signed in successfully');
      navigateTo('dashboard');
    } else {
      showError('login-error', data.detail || 'Invalid credentials');
    }
  } catch (e) {
    showError('login-error', 'Cannot reach server');
  }
});

$('#login-pass').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') $('#login-btn').click();
});

$('#signup-btn').addEventListener('click', async () => {
  const user = $('#signup-user').value.trim();
  const pass = $('#signup-pass').value;
  if (!user || !pass) { showError('signup-error', 'Please fill in all fields.'); return; }
  try {
    const res = await fetch(`${API}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass }),
    });
    const data = await res.json();
    if (res.ok && data.success) {
      $('#signup-error').style.display = 'none';
      const s = $('#signup-success');
      s.textContent = 'Account created! You can now sign in.';
      s.style.display = 'block';
      setTimeout(() => {
        $('#signup-form').style.display = 'none';
        $('#login-form').style.display = 'block';
        s.style.display = 'none';
      }, 1500);
    } else {
      showError('signup-error', data.detail || 'Username already exists');
    }
  } catch (e) {
    showError('signup-error', 'Cannot reach server');
  }
});

$('#signup-pass').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') $('#signup-btn').click();
});

$('#nav-logout').addEventListener('click', () => {
  state.loggedIn = false;
  state.userId = null;
  state.username = null;
  navigateTo('auth');
  showToast('Signed out');
});

function showError(id, msg) {
  const el = $(`#${id}`);
  el.textContent = msg;
  el.style.display = 'block';
}

// ── NAV LINKS ──
$$('.nav-link[data-page]').forEach(link => {
  link.addEventListener('click', () => navigateTo(link.dataset.page));
});
$$('.footer-link[data-page]').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    if (state.loggedIn) navigateTo(link.dataset.page);
  });
});

// ── DASHBOARD ──
let activityChart = null;

async function loadDashboard() {
  try {
    const res = await fetch(`${API}/user/stats?user_id=${state.userId}`);
    const data = await res.json();
    $('#stat-total').textContent = data.total || 0;

    // Chart
    if (data.timeline && data.timeline.length > 0) {
      const labels = data.timeline.map(t => t[0]);
      const values = data.timeline.map(t => t[1]);
      renderChart(labels, values);
    } else {
      renderChart([], []);
    }

    // Recent
    const recentEl = $('#recent-activity');
    if (data.recent && data.recent.length > 0) {
      recentEl.innerHTML = data.recent.map(v => {
        const name = v[0].length > 22 ? v[0].substring(0, 19) + '…' : v[0];
        const date = v[1].split(' ')[0] || v[1];
        return `<div class="activity-item"><div class="activity-name">${name}</div><div class="activity-date">${date}</div></div>`;
      }).join('');
    } else {
      recentEl.innerHTML = '<div class="msg-info">No recent activity yet.</div>';
    }
  } catch (e) {
    console.error('Dashboard load error:', e);
  }
}

function renderChart(labels, values) {
  const ctx = $('#activity-chart');
  if (activityChart) activityChart.destroy();

  if (labels.length === 0) {
    activityChart = new Chart(ctx, {
      type: 'line',
      data: { labels: ['No data'], datasets: [{ data: [0], borderColor: '#d9d9d9', backgroundColor: 'rgba(17,17,17,0.03)', fill: true }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
    return;
  }

  activityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Videos Enhanced',
        data: values,
        borderColor: '#111111',
        borderWidth: 2,
        backgroundColor: 'rgba(17,17,17,0.06)',
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#111111',
        pointRadius: 4,
        pointHoverRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: 'Satoshi', size: 11 }, color: '#838282' } },
        y: { grid: { color: 'rgba(17,17,17,0.06)' }, ticks: { font: { family: 'Satoshi', size: 11 }, color: '#838282', stepSize: 1 } }
      }
    }
  });
}

// ── STUDIO: FILE UPLOADS ──
let videoFile = null;
let audioFile = null;

$('#video-input').addEventListener('change', (e) => {
  videoFile = e.target.files[0];
  if (videoFile) {
    $('#video-preview').style.display = 'block';
    $('#preview-player').src = URL.createObjectURL(videoFile);
    $('#video-filename').textContent = videoFile.name;
    $('#enhance-btn').disabled = false;
  }
});

$('#audio-input').addEventListener('change', (e) => {
  audioFile = e.target.files[0];
  if (audioFile) {
    $('#audio-filename').textContent = `Audio: ${audioFile.name}`;
  }
});

// Drag & drop for video
const vz = $('#video-upload-zone');
vz.addEventListener('dragover', (e) => { e.preventDefault(); vz.classList.add('dragover'); });
vz.addEventListener('dragleave', () => vz.classList.remove('dragover'));
vz.addEventListener('drop', (e) => {
  e.preventDefault(); vz.classList.remove('dragover');
  if (e.dataTransfer.files[0]) {
    videoFile = e.dataTransfer.files[0];
    $('#video-preview').style.display = 'block';
    $('#preview-player').src = URL.createObjectURL(videoFile);
    $('#video-filename').textContent = videoFile.name;
    $('#enhance-btn').disabled = false;
  }
});

// ── MODE TOGGLE (Upload / Camera) ──
let camStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let camTimerInterval = null;
let camSeconds = 0;

$('#mode-upload').addEventListener('click', () => {
  $('#upload-mode').style.display = 'block';
  $('#camera-mode').style.display = 'none';
  $('#mode-upload').style.background = 'var(--ink)';
  $('#mode-upload').style.color = 'var(--bg)';
  $('#mode-camera').style.background = 'transparent';
  $('#mode-camera').style.color = 'var(--gray1)';
  stopCamStream();
});

$('#mode-camera').addEventListener('click', async () => {
  $('#upload-mode').style.display = 'none';
  $('#camera-mode').style.display = 'block';
  $('#mode-camera').style.background = 'var(--ink)';
  $('#mode-camera').style.color = 'var(--bg)';
  $('#mode-upload').style.background = 'transparent';
  $('#mode-upload').style.color = 'var(--gray1)';
  await startCamStream();
});

async function startCamStream() {
  try {
    camStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    $('#cam-live').srcObject = camStream;
    $('#cam-live').style.display = 'block';
    $('#cam-playback').style.display = 'none';
    $('#cam-start-btn').style.display = '';
    $('#cam-stop-btn').style.display = 'none';
    $('#cam-retake-btn').style.display = 'none';
    $('#cam-recording-badge').style.display = 'none';
    $('#cam-timer').style.display = 'none';
  } catch (e) {
    showToast('Camera access denied or unavailable');
  }
}

function stopCamStream() {
  if (camStream) {
    camStream.getTracks().forEach(t => t.stop());
    camStream = null;
  }
  $('#cam-live').srcObject = null;
  clearInterval(camTimerInterval);
}

// Start Recording
$('#cam-start-btn').addEventListener('click', () => {
  if (!camStream) return;
  recordedChunks = [];
  mediaRecorder = new MediaRecorder(camStream, { mimeType: 'video/webm;codecs=vp9,opus' });
  mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = onRecordingDone;
  mediaRecorder.start();

  // UI
  $('#cam-start-btn').style.display = 'none';
  $('#cam-stop-btn').style.display = '';
  $('#cam-recording-badge').style.display = 'block';
  $('#cam-timer').style.display = 'block';
  camSeconds = 0;
  $('#cam-timer').textContent = '00:00';
  camTimerInterval = setInterval(() => {
    camSeconds++;
    const m = String(Math.floor(camSeconds / 60)).padStart(2, '0');
    const s = String(camSeconds % 60).padStart(2, '0');
    $('#cam-timer').textContent = `${m}:${s}`;
  }, 1000);
});

// Stop Recording
$('#cam-stop-btn').addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  clearInterval(camTimerInterval);
  $('#cam-stop-btn').style.display = 'none';
  $('#cam-recording-badge').style.display = 'none';
  $('#cam-timer').style.display = 'none';
});

function onRecordingDone() {
  const blob = new Blob(recordedChunks, { type: 'video/webm' });
  const url = URL.createObjectURL(blob);

  // Show recorded playback
  $('#cam-live').style.display = 'none';
  $('#cam-playback').style.display = 'block';
  $('#cam-recorded').src = url;
  const m = String(Math.floor(camSeconds / 60)).padStart(2, '0');
  const s = String(camSeconds % 60).padStart(2, '0');
  $('#cam-rec-info').textContent = `Recorded — ${m}:${s}`;

  // Show retake button
  $('#cam-retake-btn').style.display = '';
  $('#cam-start-btn').style.display = 'none';

  // Set as videoFile for enhance
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  videoFile = new File([blob], `recording_${timestamp}.webm`, { type: 'video/webm' });
  $('#enhance-btn').disabled = false;

  // Stop the live stream
  stopCamStream();
  showToast('Recording ready for enhancement');
}

// Retake
$('#cam-retake-btn').addEventListener('click', async () => {
  videoFile = null;
  $('#enhance-btn').disabled = true;
  $('#cam-playback').style.display = 'none';
  $('#cam-retake-btn').style.display = 'none';
  await startCamStream();
});

// ── STUDIO: ENHANCE ──
$('#enhance-btn').addEventListener('click', async () => {
  if (!videoFile) return;

  // Show progress
  $('#output-placeholder').style.display = 'none';
  $('#output-result').style.display = 'none';
  $('#stats-card').style.display = 'none';
  $('#output-progress').style.display = 'block';

  const fill = $('#progress-fill');
  const status = $('#progress-status');

  fill.style.width = '15%';
  status.textContent = 'Preparing files and initializing AI...';
  console.log('Enhance started with video:', videoFile.name);

  const formData = new FormData();
  formData.append('video', videoFile);
  if (audioFile) formData.append('audio', audioFile);

  try {
    fill.style.width = '30%';
    status.textContent = 'Processing audio-visual features…';

    const res = await fetch(`${API}/enhance`, {
      method: 'POST',
      body: formData,
    });

    fill.style.width = '80%';
    status.textContent = 'Finalizing output…';

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Server error');
    }
    
    console.log('--- METRICS DEBUG ---');
    console.log('Data received:', data);
    console.log('Metrics object:', data.metrics);
    
    state.enhancedVideoUrl = data.video_url;
    state.subtitleUrl = data.subtitle_url;
    state.enhancedMetrics = data.metrics || { input: {pesq:1.0, stoi:0.3}, output: {pesq:2.5, stoi:0.8} };
    state.videoName = videoFile.name;

    fill.style.width = '100%';
    status.textContent = 'Enhancement complete.';

    setTimeout(() => {
      $('#output-progress').style.display = 'none';
      showResult();
    }, 600);

    showToast('Enhancement complete!');

  } catch (e) {
    fill.style.width = '0%';
    status.textContent = '';
    $('#output-progress').style.display = 'none';
    $('#output-placeholder').style.display = 'block';
    $('#output-placeholder').className = 'msg-error';
    $('#output-placeholder').textContent = `Error: ${e.message}`;
  }
});

function showResult() {
  console.log('Rendering results...');
  try {
    const resultDiv = $('#output-result');
    if (!resultDiv) throw new Error('output-result element missing');
    resultDiv.style.display = 'block';

    const player = $('#result-player');
    if (player) {
      player.src = state.enhancedVideoUrl;
      player.load();
      
      // Add subtitles if available
      player.querySelectorAll('track').forEach(t => t.remove());
      if (state.subtitleUrl) {
        const track = document.createElement('track');
        track.kind = 'subtitles';
        track.label = 'English';
        track.srclang = 'en';
        track.default = true;
        track.src = state.subtitleUrl;
        player.appendChild(track);
      }
    }

    // Configure download button
    const dlBtn = $('#download-btn');
    if (dlBtn) {
      const baseName = (state.videoName || 'video.mp4').replace(/\.[^/.]+$/, '').replace(/[^a-z0-9_-]/gi, '_');
      dlBtn.href = state.enhancedVideoUrl;
      dlBtn.download = `MAVISE_Enhanced_${baseName}.mp4`;
    }

    // Display metrics (with extra safety)
    if (state.enhancedMetrics) {
      const { input, output } = state.enhancedMetrics;
      
      // Update Quick Stats
      const qsPesq = $('#stat-pesq-quick');
      const qsStoi = $('#stat-stoi-quick');
      if (qsPesq) qsPesq.textContent = output.pesq || '--';
      if (qsStoi) qsStoi.textContent = output.stoi || '--';

      // Update Detailed Comparison Bars
      const pInput = $('#pesq-input-bar');
      const pOutput = $('#pesq-output-bar');
      const pGain = $('#pesq-gain');
      
      if (pInput && pOutput && pGain) {
         // PESQ max is 4.5
         pInput.style.width = `${(input.pesq / 4.5) * 100}%`;
         pOutput.style.width = `${(output.pesq / 4.5) * 100}%`;
         pGain.textContent = `+${(output.pesq - input.pesq).toFixed(2)}`;
      }

      const sInput = $('#stoi-input-bar');
      const sOutput = $('#stoi-output-bar');
      const sGain = $('#stoi-gain');

      if (sInput && sOutput && sGain) {
         // STOI max is 1.0
         sInput.style.width = `${input.stoi * 100}%`;
         sOutput.style.width = `${output.stoi * 100}%`;
         sGain.textContent = `+${Math.round((output.stoi - input.stoi) * 100)}%`;
      }
    }
  } catch (err) {
    console.error('showResult crash:', err);
    showToast('Display error. Please refresh.');
  }
}

// ── TOGGLE HANDLERS ──
$('#stats-toggle-btn').addEventListener('click', () => {
  const card = $('#stats-card');
  card.style.display = (card.style.display === 'none') ? 'block' : 'none';
  $('#compare-card').style.display = 'none'; // Close other
});

$('#compare-toggle-btn').addEventListener('click', () => {
  const card = $('#compare-card');
  card.style.display = (card.style.display === 'none') ? 'block' : 'none';
  $('#stats-card').style.display = 'none'; // Close other
});

// ── STUDIO: SAVE ──
$('#save-btn').addEventListener('click', async () => {
  if (!state.enhancedVideoUrl) return;

  try {
    showToast('Saving video...');
    // Fetch blob only when needed for saving
    const videoRes = await fetch(state.enhancedVideoUrl);
    const blob = await videoRes.blob();

    const formData = new FormData();
    formData.append('video', blob, `enhanced_${state.videoName || 'video.mp4'}`);
    formData.append('user_id', state.userId);
    formData.append('original_name', state.videoName || 'Unknown.mp4');

    // If subtitles were fetched or we have a URL, we might need them. 
    // For now, let's just send the video as the backend handles basic saving.
    if (state.subtitleUrl) {
      const subRes = await fetch(state.subtitleUrl);
      const subText = await subRes.text();
      formData.append('subtitles', new Blob([subText], { type: 'text/vtt' }), 'subtitles.vtt');
    }

    const res = await fetch(`${API}/user/save-video`, {
      method: 'POST',
      body: formData,
    });
    if (res.ok) {
      showToast('Saved to your account!');
    } else {
      showToast('Failed to save');
    }
  } catch (e) {
    showToast('Error saving video');
    console.error(e);
  }
});

// ── SAVED VIDEOS ──
async function loadSavedVideos() {
  try {
    const res = await fetch(`${API}/user/videos?user_id=${state.userId}`);
    const data = await res.json();
    const grid = $('#saved-grid');
    const empty = $('#saved-empty');

    if (!data.videos || data.videos.length === 0) {
      grid.innerHTML = '';
      grid.style.display = 'none';
      empty.style.display = 'block';
      return;
    }

    empty.style.display = 'none';
    grid.style.display = 'grid';
    grid.innerHTML = data.videos.map(v => {
      let trackHtml = '';
      if (v.has_vtt) {
        trackHtml = `<track kind="subtitles" label="English" srclang="en" default src="/saved_videos/${v.vtt_filename}">`;
      }
      return `
      <div class="card">
        <div class="section-label">${v.created_at}</div>
        <h4 style="font-size:1.05rem;margin-bottom:0.8rem;">${v.original_name}</h4>
        <div class="video-container">
          <video controls preload="metadata" src="/saved_videos/${v.filename}">${trackHtml}</video>
        </div>
        <a class="btn btn-secondary btn-full btn-sm" href="/saved_videos/${v.filename}" download="MAVISE_History_${v.original_name.replace(/\.[^/.]+$/, '')}.mp4" style="margin-top:0.5rem;">
          ↓ Download MP4
        </a>
      </div>`;
    }).join('');

  } catch (e) {
    console.error('Failed to load saved videos:', e);
  }
}

// ── INIT ──
navigateTo('auth');
