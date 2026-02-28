# ClawMini 🤖

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Read this in other languages: [English](README.md), [简体中文](README_zh.md).*

**ClawMini** is a lightweight, highly extensible, and privacy-first autonomous AI Agent framework built on LangChain and LangGraph. It is designed to act as your personalized digital assistant, capable of dynamically loading skills, managing long-term memory via RAG, and interacting with your local operating system safely.

## 📑 Table of Contents
- [🌟 Key Features](#-key-features)
- [🚀 Quick Start](#-quick-start)
- [📁 Structure Overview](#-structure-overview)
- [📄 License](#-license)

## 🌟 Key Features

- **Multi-LLM Support**: Seamlessly switch between local models (Ollama) and cloud providers (DeepSeek, OpenAI, DashScope, Google Gemini) via `.env` configuration.
- **Hot-Pluggable Skills**: A dynamic plugin system. Add or modify skills folders in the `backend/skills` directory, and the agent will instantly recognize and utilize new capabilities without needing a restart.
- **Long-Term Memory & Identity**: Features a robust, self-managing RAG (Retrieval-Augmented Generation) memory system using FAISS. The agent automatically maintains `MEMORY.md` to remember your preferences and context across sessions while isolating your sensitive data.
- **Sandboxed Execution**: Equipped with core tools (Terminal, Python REPL, Web Fetcher) that operate under strict user-defined boundaries and safety checks.

## 🚀 Quick Start

1. **Clone & Setup Environment**
   ```bash
   git clone git@github.com:Leo-434/claw-mini.git
   cd claw-mini
   # Using uv to manage the virtual environment
   uv sync
   ```

2. **Configuration**
   Copy the example environment file and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   *For memory and user profile initialization, copy the templates in `backend/` as well:*
   ```bash
   cp backend/workspace/USER.example.md backend/workspace/USER.md
   cp backend/memory/MEMORY.example.md backend/memory/MEMORY.md
   ```

3. **Run the Agent CLI**
   ```bash
   uv run main.py
   ```

## 📁 Structure Overview
- `backend/graph/`: Contains the LangGraph agent logic.
- `backend/memory/`: RAG indexing, FAISS storage, and long-term memory logic.
- `backend/skills/`: Drop-in directory for new Agent skills (e.g., `get_weather`, `pdf_to_md`).
- `backend/tools/`: Core fundamental tools (`terminal`, `python_repl`).
- `backend/workspace/`: Agent personality (`SOUL.md`), operation protocols (`AGENTS.md`), and your personal profile.

## � License
This project is licensed under the MIT License - see the LICENSE file for details.

---
