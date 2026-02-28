# ClawMini 🤖

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*其他语言阅读：[English](README.md), [简体中文](README_zh.md).*

**ClawMini** 是一个基于 LangChain 和 LangGraph 构建的轻量级、高扩展性且**隐私优先**的本地自主 AI Agent 框架。它的目标是成为你专属的数字副手，具备技能热插拔、通过 RAG 管理长期记忆以及安全操作本地环境的能力。

## 📑 目录
- [🌟 核心特性](#-核心特性)
- [🚀 快速开始](#-快速开始)
- [📁 核心目录结构](#-核心目录结构)
- [📄 开源协议](#-开源协议)

## 🌟 核心特性

- **多模型无缝切换**：通过修改 `.env` 文件，可一键切换使用本地模型（Ollama）或云端大模型（DeepSeek、OpenAI、DashScope 阿里云、Google Gemini）。
- **技能热插拔 (Hot-Pluggable Skills)**：动态插件系统。只需在 `backend/skills` 目录下添加或修改skills文件夹，Agent 即可在下一秒的对话中瞬间掌握新技能，**无需重启应用**。
- **长期记忆与专属人设**：内置基于 FAISS 的智能 RAG（检索增强生成）长期记忆系统。代理不仅能通过 `USER.md` 认识你，还会自动将重要偏好和设定用专属安全工具写入 `MEMORY.md`，实现跨会话的记忆连贯。
- **沙盒化核心工具**：自带底层能力（如受限的 Terminal 终端执行、Python REPL 环境、网页信息抓取过滤），并在核心操作前有严格的安全审核机制。

## 🚀 快速开始

1. **克隆项目与配置环境**
   ```bash
   git clone git@github.com:Leo-434/claw-mini.git
   cd claw-mini
   # 推荐使用 uv 管理虚拟环境
   uv sync
   ```

2. **环境变量与隐私模板配置**
   复制示例环境变量文件并填入你的 API Key：
   ```bash
   cp .env.example .env
   ```
   *同时，为防止隐私泄漏，项目自带了模板文件。请在本地初始化你的专属记录：*
   ```bash
   cp backend/workspace/USER.example.md backend/workspace/USER.md
   cp backend/memory/MEMORY.example.md backend/memory/MEMORY.md
   ```

3. **运行交互式终端**
   ```bash
   uv run main.py
   ```

## 📁 核心目录结构
- `backend/graph/`：Agent 的运行逻辑与 LangGraph 路由定义。
- `backend/memory/`：基于 FAISS 的本地向量检索库及长短期记忆管理模块。
- `backend/skills/`：扩展技能库目录（如 `get_weather`天气查询、`pdf` 文件处理等）。
- `backend/tools/`：支持 Agent 运作的系统级核心工具 (`terminal`, `python_repl` 等)。
- `backend/workspace/`：存储智能体的核心性格约束 (`SOUL.md`)、运行协议 (`AGENTS.md`) 和你的用户画像。


## 📄 开源协议
本项目采用 MIT 开源许可协议 - 详情请参阅 LICENSE 文件。

---