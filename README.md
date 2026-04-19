![Build and Test](https://github.com/swe-students-spring2026/4-containers-quaint_quokkas/actions/workflows/full-stack.yml/badge.svg)                
![Lint](https://github.com/swe-students-spring2026/4-containers-quaint_quokkas/actions/workflows/lint.yml/badge.svg)

# Presently

### Project Description
Presently is a Flask web app designed to help you improve your speaking and presentation skills. Users can record video directly in the browser, and the app uses machine learning to analyze both the video feed and speech. By tracking metrics like eye contact and speech patterns, Presently calculates a "focus" score to give you actionable feedback. The app includes user authentication and saves your session data to our database so you can track your progress and improvement over time. 

### Main Features
* **Video & Audio Analysis:** Processes user-recorded video to evaluate presentation delivery.
* **Eye Contact Tracking:** Uses MediaPipe to determine how many frames you spend actually looking at the camera.
* **Filler Word Detection:** Transcribes your speech to find and count filler words (e.g., "um", "uh", "like").
* **Focus Scoring:** Aggregates video and audio metrics to give you an overall focus and performance score.
* **Progress Tracking:** Saves your results to our database so you can view your historical data and see how you improve.
* **User Authentication:** Secure login and registration so your video analysis and history remain private.

### Team Members
* [Abid Al Qureshi](https://github.com/swe-students-spring2026/Abid2422)
* [Anish Susarla](https://github.com/swe-students-spring2026/anishs37)
* [Ethan Arnold](https://github.com/ethanarnold)
* [Sanjay Chunduru](https://github.com/Sanjayc0204)
* [Vincent Campanaro](https://github.com/vincentcamp)

[Task Board](https://github.com/orgs/swe-students-spring2026/projects/112/views/2)

### Setup Instructions

1. Clone the repository:
```bash
   git clone https://github.com/YOUR_ORG/YOUR_REPO.git
   cd YOUR_REPO
```

2. Create your environment file:
```bash
   cp env.example .env
```

3. Build and start all containers:
```bash
   docker-compose up --build
```

4. Access the application:
   - Web app: http://localhost:3000
   - ML client API: http://localhost:8000

5. To stop all containers:
```bash
   docker-compose down
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `MONGO_URI` | MongoDB connection string | `mongodb://mongodb:27017/mydb` |

### Database

MongoDB runs automatically via Docker Compose with persistent storage. No manual setup or seed data is required.



