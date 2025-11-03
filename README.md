# ⚡️ EchoSeek

**Search your style — discover trends, outfits, and more.**

---

## 🌟 Overview

EchoSeek is your personalized style discovery tool. Easily search and explore the latest **trends**, discover new **outfits**, and find **inspiration** to elevate your look.

---

## 💻 Local Deployment 

**Sorry, this is a local deployment!** This application requires external services and **will not function without them**.

It consists of a local **Frontend** and **Backend** application that interacts with two crucial **AWS SageMaker Endpoints** for its core functionality:

* **Generative Model:** The `llama-3 1-nemotron-nano-8B-v1` model is deployed on a dedicated SageMaker Endpoint for content generation (e.g., style advice, trend analysis).
* **Embedding Model:** The `llama-3.2-nv-embedqa-1b-v2` model is deployed on a dedicated SageMaker Endpoint for text embedding (e.g., searching, context matching).

---
## 📚 Resources

| Resource | Description | Link |
| :--- | :--- | :--- |
| **Project Documentation** | Detailed guides on architecture, setup, and features. | [Insert Docs Link Here] |
| **Demo Video** | A quick walkthrough of the application's core functionality. | [Insert Video Link Here] |

---

## 🏗️ Repository Structure

This project is split into two main branches to separate the application logic:

* **`main` branch**: Contains all the **Frontend** code (user interface, styling, and client-side logic).
* **`backend` branch**: Contains all the **Backend** code (API, database interactions, and server-side logic).

---

## 🚀 Getting Started

Follow these steps to get the **Frontend** and **Backend** running locally.

### 1. Backend Setup

The complete installation and running guide for the backend server, database, and API is located in the dedicated documentation.

➡️ **[Go to Backend Installation Guide](https://github.com/pratim4dasude/echoseek/tree/backend)**


### 2. Frontend Installation (Main Branch - Next.js)

Use the instructions below to set up and run the client-side application built with **Next.js**.

1.  **Clone the Repository:**
    ```bash
    git clone <Your-Repo-URL>
    cd EchoSeek
    ```
2.  **Install Core Dependencies:**
    Next.js requires the core packages: `next`, `react`, and `react-dom`.
    ```bash
    npm install next@latest react@latest react-dom@latest
    # OR
    yarn add next@latest react@latest react-dom@latest
    ```
3.  **Install Remaining Dependencies:**
    Install any other required packages listed in the `package.json` file.
    ```bash
    npm install 
    # OR
    yarn install
    ```
4.  **Configure API Endpoint:**
    * Ensure your backend server is running (see **Backend Installation Guide** above).
    * Update the API endpoint configuration in the relevant file (e.g., `.env` or `config.js`) to point to your local backend (usually `http://localhost:<BACKEND_PORT>`).
5.  **Run the Development Server:**
    Start the Next.js development server.
    ```bash
    npm run dev
    # OR
    yarn dev
    ```
    The frontend should open automatically in your browser (typically at `http://localhost:3000`).
