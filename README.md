# E-commerce Recommendation Engine

## Team Members

*   [Xingjian Zhang](https://github.com/ScottZXJ123)
*   [Yukun Dong](https://github.com/abccdyk)

## Subsystems

*   **MongoDB:** Database for products, users, and interactions.
*   **Recommender (Python):** Generates product recommendations.
*   **API (Python/FastAPI):** Serves recommendations via a RESTful API.
*   **Frontend (HTML/JS/Nginx):** Simple web interface to display recommendations.

## Docker Hub Images

*   MongoDB: `docker pull scottz1234/ecommerce-mongodb:latest`
*   Recommender: `docker pull scottz1234/ecommerce-recommender:latest`
*   API: `docker pull scottz1234/ecommerce-api:latest`
*   Frontend: `docker pull scottz1234/ecommerce-frontend:latest`

## Setup and Running

**Detailed instructions are required here!** Include:

1.  **Prerequisites:** (e.g., Docker, Docker Compose)
2.  **Configuration:**
    *   How to create the `.env` file from `.env.example`.
    *   Explanation of each environment variable in `.env.example`.
3.  **Running the application:** (e.g., using Docker Compose)
    ```bash
    # Example docker-compose setup (You need to create docker-compose.yml)
    cp .env.example .env
    # Edit .env with your actual secrets/configuration
    docker-compose up --build -d
    ```
4.  **Accessing the application:**
    *   Frontend: `http://localhost:<FRONTEND_PORT>`
    *   API: `http://localhost:<API_PORT>` (e.g., `http://localhost:8000/docs` for API docs)
5.  **Importing Data:** Explain that data is imported automatically via `mongodb/init.sh` when the MongoDB container starts.

## Environment Variables

See `.env.example` for required environment variables. Create a `.env` file based on the example and populate it with your configuration and secrets.

*(Ensure this section provides clear instructions as per instructions.md)*
