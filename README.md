![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

Project specs:
ML Client (2 people) — @ethan and @Geosoleus 🔮 
ML-1: Sensor data collection (e.g., OpenCV camera capture), pymongo storage logic
ML-2: ML analysis pipeline (e.g., pretrained model for image recognition/classification), processing results and writing them to DB

Both write their own tests and handle black/pylint for their code.

Web App (2 people) — @Abid and @Vincent 
Web-1: Flask backend — routes, pymongo queries, API endpoints serving ML results
Web-2: Frontend dashboard — templates, visualization of results, any user-facing interaction

Both write their own tests (pytest-flask) and handle black/pylint for their code.

Infrastructure (1 person) — @N1rvana 
Dockerfiles for both subsystems, docker-compose.yml, MongoDB container config, inter-container networking, .env / env.example
GitHub Actions workflows (build/test CI for both subsystems, lint workflow adjustments)
README documentation (setup instructions, badges, team links)

This person should start early since others need working containers to integration-test against, and should be available to unblock teammates on Docker/networking issues throughout. 
Next meetings: Friday 6 PM, Sunday 2 PM
