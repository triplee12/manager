# Project Challenge: TaskFlow – A Collaborative Task Management API

## Objective

Build a backend REST API for a collaborative task management system (like a lightweight Asana or Trello clone) using FastAPI and SQL (SQLite or PostgreSQL). The system should support users, teams, projects, tasks, and comments, with appropriate authentication, authorization, and relational design.

## 🗂️ Functional Requirements

### * User Management

* Register new users (with hashed passwords).
* JWT-based login.

* Role-based access control (admin, member).
* Team and Project Structure

* Users can create or join teams.

* Teams can have multiple projects.
* Only team members can access their projects.

### * Tasks

* Each project has multiple tasks with:

    Title, description, status (todo, in_progress, done), due date, priority.

* Assigned user(s) from the same team.
* Tasks can be filtered by status, assignee, due date range.

* Comments
* Users can comment on tasks.

* Comments are timestamped and ordered.

### * Activity Log

* Every significant action (create/update/delete task/comment) should be recorded in an activity log per project.

## 🧪 Technical Requirements

* Use FastAPI for the API layer.
* Use SQLAlchemy ORM with PostgreSQL (preferred) or SQLite.

* Secure endpoints using OAuth2 + JWT.
* Modular code structure using routers and dependency injection.

* Write at least 5 unit tests using pytest.

### * 🧠 Bonus Requirements (if time allows)

* Add WebSocket endpoint for real-time project activity feed.
* Add rate limiting per user using a FastAPI middleware.

* Deployable Dockerfile with docker-compose to run the app and DB locally.

## 📦 Deliverables

* Complete FastAPI project code in a GitHub repo (or zipped).
* API documentation using FastAPI’s OpenAPI auto-docs.

* Sample DB seeding script or test users/tasks for quick testing.
* (Optional) Postman collection or curl commands to demo endpoints.
