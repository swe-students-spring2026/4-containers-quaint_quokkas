![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

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