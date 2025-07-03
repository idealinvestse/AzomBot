# AzomBot System Workflows and Logic

This document provides a detailed explanation of the key architectural workflows and logic flows within the AzomBot application. It covers how settings are managed, how the different Large Language Model (LLM) backends operate, and how the specialized pipeline server functions.

---

## 1. High-Level System Architecture

The AzomBot system is composed of three primary components:

1.  **Frontend**: A React application built with Vite and TypeScript. It provides the user interface for interacting with the bot, managing knowledge base files, and configuring system settings.
2.  **Main Backend**: A FastAPI application that serves the frontend, handles general chat queries, manages the knowledge base, and exposes an API for system configuration.
3.  **Pipeline Server**: A separate FastAPI application dedicated to handling complex, multi-step tasks, such as generating vehicle-specific installation guides. It has its own set of services and logic tailored for these structured workflows.

---

## 2. Dynamic Configuration and Settings Flow

One of the core features of AzomBot is its ability to be reconfigured at runtime directly from the frontend settings page. This allows users to switch LLM backends, update API keys, and change models without restarting the server.

**The flow works as follows:**

1.  **User Interaction (Frontend)**:
    *   The user navigates to the `SettingsPage.tsx` in the frontend.
    *   They modify a setting, for example, changing the **LLM Backend** from `OpenWebUI` to `Groq`.
    *   Upon clicking "Save," the `saveSettings` function in `settingsService.ts` is triggered.

2.  **API Call (Frontend to Backend)**:
    *   The `settingsService.ts` first saves the settings to the browser's `localStorage` for UI persistence.
    *   It then immediately sends a `POST` request containing the updated settings object to the `/api/v1/settings` endpoint on the **Main Backend**.

3.  **Dynamic Update (Backend)**:
    *   The `/api/v1/settings` endpoint receives the new settings and validates them using the `FrontendSettings` Pydantic model.
    *   It then calls the `update_runtime_settings` function in `app/config.py`.
    *   This function updates a global, in-memory dictionary (`_current_settings`) with the new configuration values. This dictionary acts as the single source of truth for all runtime-configurable settings.

4.  **Dependency Injection in Action**:
    *   Subsequent API calls that rely on these settings (e.g., a new chat message) will now use the updated values. FastAPI's dependency injection system re-evaluates dependencies for each request, so the `get_llm_client` dependency will now receive the new configuration from `get_current_config()` and instantiate the correct client (e.g., `GroqClient` instead of `OpenWebUIClient`).

---

## 3. LLM Backend Switching: Groq vs. OpenWebUI

The system is designed to seamlessly switch between a local OpenWebUI instance and the cloud-based Groq API. This is achieved through a combination of a unified interface (Protocol) and a dynamic factory (Dependency).

**Key Components:**

*   **`LLMServiceProtocol` (`llm_client.py`)**: A protocol that defines a common interface that all LLM clients must adhere to. It mandates a `chat` method, ensuring that the `AIService` can interact with any client in the same way.

*   **`OpenWebUIClient` and `GroqClient` (`llm_client.py`)**: Two distinct classes, each implementing the `LLMServiceProtocol`. 
    *   The `OpenWebUIClient` is configured to make requests to a local OpenWebUI server URL.
    *   The `GroqClient` is configured to use the Groq API endpoint and requires a Groq API key.

*   **`get_llm_client` Factory (`llm_client.py`)**: This is the core of the dynamic switching logic. It is a FastAPI dependency function that:
    1.  Retrieves the current runtime configuration by calling `get_current_config()`.
    2.  Checks the value of the `LLM_BACKEND` setting.
    3.  If `LLM_BACKEND` is `'groq'`, it instantiates and returns a `GroqClient`.
    4.  Otherwise, it defaults to instantiating and returning an `OpenWebUIClient`.

**How it works in a request:**

1.  A request hits an endpoint like `/chat/azom`.
2.  FastAPI sees that the endpoint depends on `AIService` (via `get_ai_service`).
3.  To create `AIService`, FastAPI needs to resolve its dependency: an `LLMServiceProtocol` client (via `get_llm_client`).
4.  The `get_llm_client` function executes, reads the *current* runtime settings, and returns the appropriate client instance.
5.  The `AIService` receives this client and uses it to process the request, completely unaware of which specific implementation it is using.

---

## 4. Pipeline Server Workflow

The **Pipeline Server** is designed for a specific, structured task: generating installation guides for Azom products based on a user's vehicle.

**The flow for the `/pipeline/install` endpoint is as follows:**

1.  **Request Initiation**: A client (e.g., the main application or a testing tool) sends a `POST` request to `/pipeline/install`. The payload includes the user's query, their car model, and optionally their experience level.

2.  **Input Validation**: The endpoint first validates the input to ensure that the car model and user query are present.

3.  **Orchestration Service**: The request is handed off to the `OrchestrationService`. This service acts as the main controller for the pipeline.

4.  **Product Recommendation**: The `OrchestrationService` calls the `ProductService` with the user's car model. The `ProductService` queries its internal data (from `products.json`) to find a compatible Azom product (e.g., "AZOM DLR" for a "Honda CR-V").

5.  **Knowledge Retrieval (Vector Store)**: The `OrchestrationService` then uses the recommended product name and the user's query to search for relevant information in the **Vector Store**. The `VectorStoreService` finds the most relevant chunks of text from the knowledge base related to installing that specific product.

6.  **Prompt Composition**: The retrieved knowledge chunks, the recommended product, the car model, and the user's original query are all compiled into a detailed, structured prompt.

7.  **LLM Invocation**: This final prompt is sent to an LLM (configured within the pipeline server itself) to generate a set of clear, step-by-step installation instructions tailored to the user's context.

8.  **Response Generation**: The generated steps, along with the recommended product information, are packaged into a JSON response and sent back to the client.

This pipeline ensures that the user receives a highly relevant and context-specific installation guide, rather than a generic answer.
