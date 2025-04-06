from flask import Flask, request, redirect, jsonify, redirect, render_template_string
import string
import random
import redis
import os

app = Flask(__name__)

# In-memory store for URL mappings
# url_database = {}

# Apply Redis for URL storage
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Shortener</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .form-container {
                background-color: #f0f0f0;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            input[type="text"] {
                width: 70%;
                padding: 8px;
                margin-right: 10px;
            }
            button {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .url-list {
                border-top: 1px solid #ddd;
                margin-top: 20px;
            }
            .url-item {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #ddd;
            }
            .url-item a {
                color: #0066cc;
                text-decoration: none;
            }
            .url-item a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>URL Shortener</h1>
        
        <div class="form-container">
            <h2>Shorten a URL</h2>
            <input type="text" id="urlInput" placeholder="https://example.com">
            <button onclick="shortenUrl()">Shorten</button>
            <p id="result"></p>
        </div>
        
        <h2>Your Shortened URLs</h2>
        <div id="urlList" class="url-list">
            <p>No URLs shortened yet.</p>
        </div>
        
        <script>
            // Function to shorten a URL
            async function shortenUrl() {
                const urlInput = document.getElementById('urlInput');
                const result = document.getElementById('result');
                
                try {
                    const response = await fetch('/api/shorten', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ url: urlInput.value })
                    });
                    
                    const data = await response.json();
                    result.innerHTML = `Success! Short URL: <a href="${data.short_url}" target="_blank">${data.short_url}</a>`;
                    urlInput.value = '';
                    
                    // Refresh the URL list
                    loadUrls();
                } catch (error) {
                    result.innerHTML = `Error: ${error.message}`;
                }
            }
            
            // Function to load all URLs
            async function loadUrls() {
                try {
                    const response = await fetch('/api/urls');
                    const data = await response.json();
                    
                    const urlList = document.getElementById('urlList');
                    
                    if (data.urls.length === 0) {
                        urlList.innerHTML = '<p>No URLs shortened yet.</p>';
                        return;
                    }
                    
                    let html = '';
                    data.urls.forEach(item => {
                        html += `
                            <div class="url-item">
                                <div>
                                    <div><strong>Short URL:</strong> <a href="${item.short_url}" target="_blank">${item.short_url}</a></div>
                                    <div><strong>Original:</strong> <a href="${item.long_url}" target="_blank">${item.long_url}</a></div>
                                </div>
                            </div>
                        `;
                    });
                    
                    urlList.innerHTML = html;
                } catch (error) {
                    console.error('Error loading URLs:', error);
                }
            }
            
            // Load URLs when the page loads
            window.onload = loadUrls;
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

# Add this new API endpoint to get all URLs
@app.route('/api/urls', methods=['GET'])
def get_all_urls():
    urls = []
    host_url = request.host_url
    
    # for code, long_url in url_database.items():
    #     urls.append({
    #         "short_url": host_url + code,
    #         "long_url": long_url
    #     })

    # Use Redis to get all URLs both short and long form
    codes = r.smembers("shorturl:index")
    for code in codes:
        long_url = r.get(f"shorturl:{code}")
        urls.append({
            "short_url": host_url + code,
            "long_url": long_url
        })
    
    return jsonify({"urls": urls})


# Function to generate a random short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    long_url = data.get('url')
    
    if not long_url:
        return jsonify({"error": "URL is required"}), 400
    
    # Add http:// prefix if missing
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'http://' + long_url
    
    # Generate a new short code
    code = generate_short_code()
    # while code in url_database:
    #     code = generate_short_code()
    
    # # Store the mapping
    # url_database[code] = long_url
    # print(url_database)

    while True:
        code = generate_short_code()
        success = r.set(f"shorturl:{code}", long_url, nx=True)
        if success:
            r.sadd("shorturl:index", code)
            break
    
    # Return the short URL
    short_url = request.host_url + code
    return jsonify({"short_url": short_url, "long_url": long_url})

@app.route('/<short_code>')
def redirect_to_url(short_code):
    # long_url = url_database.get(short_code)
    long_url = r.get(f"shorturl:{short_code}")
    if long_url:
        return redirect(long_url)
    else:
        return "URL not found", 404

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)