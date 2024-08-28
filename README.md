# Wise Browse

**Wise Browse** is a user-friendly desktop web browser designed to assist older adults in navigating the internet with ease. By integrating advanced artificial intelligence and a minimalist interface, Wise Browse provides step-by-step guidance tailored to user needs, making digital interactions more accessible and intuitive.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Technical Details: How the AI Works](#technical-details-how-the-ai-works)
- [Contributors](#contributors)
- [Licensing](#licensing)

## About

**Wise Browse** is developed to address the challenges faced by older adults when using the internet. With its built-in AI assistant, Wise Browse simplifies the web experience by providing real-time, step-by-step instructions to guide users through various online tasks. The project is a collaborative effort by Imperial College London students aimed at enhancing digital literacy and confidence.

## Features

- **AI-Powered Assistance**: The AI assistant, powered by OpenAI, reads and interprets the content of websites to provide contextual help. It delivers easy-to-follow, step-by-step instructions that adapt based on user actions and queries.
- **Minimalist Interface**: Designed with a clean and simple interface, Wise Browse reduces cognitive load and focuses on essential functionality. A side menu provides access to the AI assistant and other helpful features.
- **Community-Driven FAQs**: The browser includes a feature to display Frequently Asked Questions (FAQs) from other users regarding the current website. This creates a sense of community and helps users find answers to common issues.
- **Cross-Platform Compatibility**: Wise Browse is available for Windows, macOS, and Linux, ensuring broad accessibility across different operating systems.

## Installation

To install Wise Browse, follow these steps:

1. **Download the Installer**:
   - Go to the [Releases](https://github.com/AlexShem247/wise-browse/releases) page.
   - Download the appropriate `.exe` file for Windows, or the corresponding installer for macOS and Linux.

2. **Run the Installer**:
   - Execute the downloaded file to start the installation process.
   - Follow the on-screen instructions to complete the installation.

3. **Launch the Application**:
   - Once installed, open Wise Browse from your applications menu or desktop shortcut.

## Usage

To start using Wise Browse:

1. **Open the Application**: Launch Wise Browse from your applications menu or desktop shortcut.
2. **Interact with the AI Assistant**:
   - Type your questions or use voice commands to ask the AI assistant for help.
   - Follow the step-by-step instructions provided by the AI to complete tasks.
3. **Access FAQs**: Use the side menu to view FAQs related to the current website, helping you navigate common issues.

## Technical Details: How the AI Works

The AI component of Wise Browse is designed to enhance user navigation by providing contextual assistance and step-by-step guidance. Here’s an overview of how the AI system functions:

1. **User Interaction**:
   - The user interacts with the browser and asks questions or requests help through the AI menu.
   - User queries are captured and sent to the AI system for processing.

2. **Query Processor**:
   - The Query Processor receives the user's question and determines the nature of the request.
   - It categorises the query and prepares it for further processing by the AI.

3. **Request Web Page**:
   - If the query requires information from the current webpage, the Request Web Page component fetches the relevant content from the web.
   - The system retrieves and processes the page data to understand its structure and content.

4. **Response Processor**:
   - The Response Processor analyses the user's question in the context of the fetched webpage content.
   - It generates a response by combining natural language understanding with web page data to provide accurate, step-by-step instructions.

5. **AI Integration**:
   - The AI assistant, powered by OpenAI's models, interprets the question and the context provided by the webpage.
   - The AI uses advanced algorithms to generate responses that are relevant to the user's needs, adapting instructions based on the user’s interaction with the website.

6. **Database Interaction**:
   - The system interacts with a Supabase-hosted database to store and retrieve historical user data and preferences.
   - This data helps personalise the AI responses and improve accuracy over time by learning from previous interactions.

7. **Response Delivery**:
   - The final response, crafted by the Response Processor, is delivered to the user through the AI menu.
   - Users receive clear, actionable steps to complete their tasks, with the ability to follow instructions at their own pace.

8. **Feedback Loop**:
   - User interactions and feedback are continuously monitored to refine and enhance the AI’s capabilities.
   - The system uses this feedback to adjust its responses and improve overall user experience.

By integrating these components, Wise Browse ensures that users receive timely and relevant assistance tailored to their specific needs, making internet navigation simpler and more intuitive.

## Contributors

This project was a collaborative effort developed by a dedicated team of students from Imperial College London. Each member brought their unique skills and expertise to various aspects of the Wise Browse's development.

- [Alexander Shemaly](https://github.com/AlexShem247)
- [Andras Tremmel](https://github.com/AndrasTremmel)
- Vlad Marchis
- Alex Slater


## Licensing

Wise Browse is licensed under the [GPL v3 License](LICENSE). This open-source license allows you to freely modify and distribute the code, provided that any derivative works are also open-source under the same license.