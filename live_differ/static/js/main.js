// Utility function to format bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Socket.io connection and event handling
const socket = io();
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.querySelector('.status-text');

socket.on('connect', () => {
    console.log('Connected to server');  // Debug log
    statusIndicator.classList.remove('disconnected');
    statusIndicator.classList.add('connected');
    statusText.textContent = 'Connected';
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');  // Debug log
    statusIndicator.classList.remove('connected');
    statusIndicator.classList.add('disconnected');
    statusText.textContent = 'Disconnected';
});

socket.on('update_diff', (data) => {
    console.log('Received diff update');  // Debug log
    
    // Update file 1 info
    document.getElementById('file1-name').textContent = data.file1_info.name;
    document.getElementById('file1-path').textContent = data.file1_info.path;
    document.getElementById('file1-modified').textContent = data.file1_info.modified_time;
    document.getElementById('file1-size').textContent = formatBytes(data.file1_info.size);
    
    // Update file 2 info
    document.getElementById('file2-name').textContent = data.file2_info.name;
    document.getElementById('file2-path').textContent = data.file2_info.path;
    document.getElementById('file2-modified').textContent = data.file2_info.modified_time;
    document.getElementById('file2-size').textContent = formatBytes(data.file2_info.size);
    
    // Update diff content
    document.getElementById('diff-view').innerHTML = data.diff_html;
});

// Theme switching functionality
function initializeTheme() {
    const themeSwitch = document.getElementById('theme-switch');
    const themeIcon = document.getElementById('theme-icon');
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeIcon.className = savedTheme === 'dark' ? 'ri-lightbulb-line' : 'ri-lightbulb-fill';
    
    themeSwitch.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        themeIcon.className = newTheme === 'dark' ? 'ri-lightbulb-line' : 'ri-lightbulb-fill';
        localStorage.setItem('theme', newTheme);
    });
}

// Initialize theme switcher
document.addEventListener('DOMContentLoaded', initializeTheme);
