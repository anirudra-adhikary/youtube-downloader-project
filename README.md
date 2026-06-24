# 🎥 YouTube Downloader Project

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/anirudra-adhikary/youtube-downloader-project/graphs/commit-activity)

A robust, web-based YouTube video downloading application built primarily in Python. This project was conceptualized and built for educational purposes, specifically to explore and learn the system design principles behind complex media-processing systems.

## 📖 Table of Contents
- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [System Design Learnings](#system-design-learnings)
- [Contributing](#contributing)
- [License](#license)

## 🧐 About the Project
Downloading and processing video files from external sources at scale requires careful consideration of networking, file I/O, storage, and processing overhead. This project serves as a sandbox to understand how these components interact. It includes a web interface for user interaction and backend scripts capable of downloading and manipulating media files.

## ✨ Key Features
- **Web Interface:** Clean and intuitive UI to accept YouTube URLs.
- **Video Downloading:** Core backend functionality to fetch video streams from YouTube.
- **Media Processing:** Includes logic (`crop.py`) for post-processing and cropping downloaded media files.
- **Extensible Architecture:** Designed with system design concepts in mind, making it easy to scale or add queue-based processing in the future.

## 🛠 Tech Stack
- **Backend:** Python (93.2%)
- **Frontend:** HTML (3.2%), CSS (3.6%)
- **Dependencies:** Managed via `requirements.txt`.

## 📁 Project Structure
```text
youtube-downloader-project/
├── static/              # CSS, JavaScript, and other static web assets
├── templates/           # HTML templates for the web interface
├── crop.py              # Script for processing and cropping media  
├── gui.py               # GUI Application entry point / flet app
├── main.py              # Application entry point / core execution logic
├── web.py               # Web server and routing logic
├── requirements.txt     # Python dependencies (minimal)
├── requirements-fletapp.txt  # Python dependencies for flet GUI app development
└── .gitignore           # Ignored files and directories

```

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Make sure you have Python installed on your system.

* Python 3.8 or higher
* `pip` (Python package installer)

### Installation

1. Clone the repository:

```bash
   git clone [https://github.com/anirudra-adhikary/youtube-downloader-project.git](https://github.com/anirudra-adhikary/youtube-downloader-project.git)
   cd youtube-downloader-project

```

2. Create a virtual environment (Recommended):

```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

3. Install the dependencies:

```bash
   pip install -r requirements.txt
   # use `requirements-fletapp.txt` for flet app
```

## 💻 Usage

1. Start the web server:

```bash
   python main.py 

```

2. Open your web browser and navigate to the localhost port specified in the console (usually `http://127.0.0.1:5000` or `http://127.0.0.1:8000`).
3. Enter a valid YouTube URL into the interface and initiate the download.

### Run as Flet app (GUI)

Run as a desktop app:

```bash
flet run gui.py
```

Run as a web app:

```bash
flet run --web gui.py
```

For more details on running the **Flet app**, refer to the [Getting Started Guide](https://flet.dev/docs/).

### Build the flet app

Build as Android apk

```bash
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

Build as iOS app

```bash
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

Build as macOS app

```bash
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

Build as Linux app

```bash
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

Build as Windows app

```bash
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).

Build as Web app

```bash
flet build web -v
```

For more details on building Web app, refer to the [Web Packaging Guide](https://flet.dev/docs/publish/web/).

## 🧠 System Design Learnings

Because this project focuses on system design, here are some concepts that can be explored or mapped out using this codebase:

* **Client-Server Architecture:** Handling web requests and asynchronous video downloads.
* **Storage Optimization:** Managing temporary files and cleanup after media processing (`crop.py`).
* **Future Scalability:** Identifying bottlenecks (e.g., synchronous downloads) to eventually introduce Message Queues and background workers.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Since this is an educational project, PRs that improve the architecture, add caching, or introduce containerization (Docker) are highly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

```

```
