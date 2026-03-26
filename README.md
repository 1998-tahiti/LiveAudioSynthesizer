# Live Audio Synthesizer

This project is a real-time audio synthesis and processing system built using Flask and WebSocket communication. It combines backend systems design with digital signal processing to deliver low-latency, interactive audio generation directly from a web interface.

The system demonstrates practical experience in real-time streaming, concurrent processing, and signal-level manipulation, bridging backend engineering with applied DSP.

## **Features**

- Real-time bidirectional communication using WebSocket (SocketIO)
- Low-latency audio streaming and processing pipeline
- Plucked-string synthesis using Karplus–Strong algorithm
- Dynamic vibrato modulation with configurable parameters
- Continuous audio buffering and block-based processing
- Event-driven architecture for real-time user interaction
- Integrated DSP pipeline within a web application
- Lightweight UI for interactive control

## **Tech Stack**
### Backend:

Python

Flask

Flask-SocketIO

PyAudio

NumPy

Multithreading

### Frontend:

HTML

CSS

JavaScript

## Core Concepts:

- Real-time systems
- Digital Signal Processing (DSP)
- Karplus–Strong synthesis
- WebSocket communication
- Low-latency streaming

## Architecture Overview

- The application is designed around a real-time streaming architecture:

- Flask handles HTTP requests and serves the frontend.

- SocketIO enables persistent, low-latency communication between client and server.

- Audio is generated and processed in real time using DSP modules.

- Karplus–Strong algorithm simulates plucked-string behavior, while vibrato adds time-based modulation.

- PyAudio streams audio output using small buffer chunks to minimize latency.

- Concurrency is managed using threading to ensure uninterrupted audio playback and responsiveness.

## **How It Works**

→ Client connects to the server via WebSocket.

→ User interaction triggers audio synthesis events.

→ The Karplus–Strong algorithm generates raw audio signals.

→ Vibrato modulation is applied dynamically.

→ Audio is processed in real-time buffers.

→ Processed audio is streamed continuously with low latency.

→ System maintains responsiveness through concurrent execution.

## Screenshots

### Main Interface
(Audio control and interaction panel)

### Real-Time Processing
(Live audio synthesis and playback)

## Running the Project Locally

Clone the repository:

git clone https://github.com/yourusername/LiveAudioSynthesizer.git

Navigate into the project:

cd your-repo-name

Create virtual environment:

python -m venv .venv

Activate virtual environment:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open browser:

http://localhost:5000
## Author

Tasnia Jasim Tahiti  
Master’s Student in Computer Engineering  
Spring Boot • Real-time Systems • Backend Development  
