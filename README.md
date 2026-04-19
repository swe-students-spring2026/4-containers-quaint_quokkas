![Web App](https://github.com/swe-students-spring2026/4-containers-quaint_quokkas/actions/workflows/web-app.yml/badge.svg)
![ML Client](https://github.com/swe-students-spring2026/4-containers-quaint_quokkas/actions/workflows/ml-client.yml/badge.svg)
![Lint](https://github.com/swe-students-spring2026/4-containers-quaint_quokkas/actions/workflows/lint.yml/badge.svg)

# Presently

### Project Description
Presently is a Flask web app designed to help you improve your speaking and presentation skills. Users can record video directly in the browser, and the app uses machine learning to analyze both the video feed and speech. By tracking metrics like eye contact and speech patterns, Presently calculates a "focus" score to give you actionable feedback. The app does not require user authentication as it only requires a local database to run.

### Main Features
* **Video & Audio Analysis:** Processes user-recorded video to evaluate presentation delivery.
* **Eye Contact Tracking:** Uses MediaPipe to determine how many frames you spend actually looking at the camera.
* **Filler Word Detection:** Transcribes your speech to find and count filler words (e.g., "um", "uh", "like").
* **Focus Scoring:** Aggregates video and audio metrics to give you an overall focus and performance score.
* **Progress Tracking:** Saves your results to our database so you can view your historical data and see how you improve.

### Team Members
* [Abid Al Qureshi](https://github.com/Abid2422)
* [Anish Susarla](https://github.com/anishs37)
* [Ethan Arnold](https://github.com/ethanarnold)
* [Sanjay Chunduru](https://github.com/Sanjayc0204)
* [Vincent Campanaro](https://github.com/vincentcamp)

[Task Board](https://github.com/orgs/swe-students-spring2026/projects/112/views/2)

### Setup Instructions

1. Clone the repository:
```bash
   git clone https://github.com/swe-students-spring2026/4-containers-quaint_quokkas.git
   cd 4-containers-quaint_quokkas
```

2. Create your environment file:
```bash
   cp env.example .env
```

3. Build and start all containers:
```bash
   docker-compose up --build
```

Note: It can take up to 10 minutes for all containers to build.

4. Access the application **(Please use Chrome instead of Safari or any other browser)**:
   - Web app: http://localhost:3000
   - ML client API: http://localhost:8000

5. To stop all containers:
```bash
   docker-compose down
```
*Note, it does take some time to analyze your speech and video*

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `MONGO_URI` | MongoDB connection string | `mongodb://mongodb:27017/mydb` |

### Database

MongoDB runs automatically via Docker Compose with persistent storage. No manual setup or seed data is required.



