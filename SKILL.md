---
name: memory-sync
description: >
  WorkBuddy Memory cloud sync skill. Syncs AI memory files (.workbuddy/memory/) to a
  private GitHub repository, enabling cross-device context sharing.
  Supports push, pull, status check, and initial setup.
  WorkBuddy Memory 云同步技能。将 AI 的记忆文件（.workbuddy/memory/）同步到 GitHub 私有仓库，
  实现多设备之间的上下文记忆共享。支持推送记忆、拉取记忆、查看同步状态、初始化配置。
  触发词：同步记忆、上传记忆、下载记忆、memory同步、记忆同步、sync memory、
  push memory、pull memory、多设备同步、跨设备记忆、记忆备份、memory备份、
  同步记忆到github、拉取最新记忆、记忆云同步。
version: 1.2.0
author: SuperCrzy
license: MIT
repository: https://github.com/SuperCrzy/workbuddy-memory-sync
scripts_dir: scripts
---

# Memory Sync Skill

将 WorkBuddy 的所有工作区 Memory 文件同步到 GitHub 私有仓库，让你在多台设备之间共享 AI 的记忆上下文。  
Syncs all WorkBuddy workspace memory files to a private GitHub repo, so your AI's context follows you across devices.

**核心脚本 / Core script**：`scripts/memory_sync.py`  
**支持平台 / Platforms**：Windows / macOS / Linux  
**依赖 / Dependencies**：Python 3.8+、Git

---

## 触发词识别规则 / Trigger Rules

| 用户说的话 / User says | 执行操作 / Action |
|---|---|
| "同步记忆"、"推送记忆"、"上传记忆"、"备份记忆" / "sync memory", "push memory", "backup memory" | push |
| "拉取记忆"、"下载记忆"、"恢复记忆"、"同步到本地" / "pull memory", "download memory", "restore memory" | pull |
| "记忆同步状态"、"查看同步" / "memory sync status", "check sync" | status |
| "配置记忆同步"、"初始化同步" / "setup memory sync", "configure sync" | setup |

---

## 命令执行方式 / How to Run Commands

执行脚本前，先用以下方式确定 Python 命令：  
Determine the Python command before running scripts:

- **Windows**：`python` 或 / or `py`
- **macOS / Linux**：`python3`

### 推送记忆到 GitHub / Push memory to GitHub
```bash
# Windows
python %USERPROFILE%\.workbuddy\skills\memory-sync\scripts\memory_sync.py push

# macOS / Linux
python3 ~/.workbuddy/skills/memory-sync/scripts/memory_sync.py push
```

### 从 GitHub 拉取最新记忆 / Pull latest memory from GitHub
```bash
python scripts/memory_sync.py pull
```

### 查看同步状态 / Check sync status
```bash
python scripts/memory_sync.py status
```

### 初始化配置（首次使用）/ Initialize (first time)
```bash
python scripts/memory_sync.py setup --repo <repo-url> --token <token>
```

---

## 完整工作流程 / Full Workflow

### 当用户触发 push 时 / When user triggers push:
1. 检查配置文件 `~/.workbuddy/memory-sync-config.json` 是否存在  
   Check if config file `~/.workbuddy/memory-sync-config.json` exists
2. 若未配置，提示用户先运行 setup，并引导获取 GitHub Token  
   If not configured, prompt user to run setup and obtain a GitHub Token
3. 自动扫描所有工作区，执行推送，展示结果  
   Auto-scan all workspaces, push, and display results

### 当用户触发 pull 时 / When user triggers pull:
1. 从 GitHub 拉取最新文件  
   Pull latest files from GitHub
2. 只还原本机已存在的工作区记忆，展示更新了哪些文件  
   Only restore memory for workspaces that already exist locally; show what was updated

### 当用户触发 setup 时 / When user triggers setup:
1. 询问用户的 GitHub 仓库 URL / Ask for GitHub repo URL
2. 询问 GitHub Personal Access Token（需要 `repo` 权限）/ Ask for PAT with `repo` scope
3. 执行 setup 命令完成配置 / Run setup to complete configuration

---

## 注意事项 / Notes

- 配置文件 `~/.workbuddy/memory-sync-config.json` 包含 Token，已加入 `.gitignore`，不会被上传  
  Config file contains Token and is in `.gitignore` — never committed
- 冲突策略：以**最新修改时间**为准，更新的文件覆盖旧文件  
  Conflict strategy: **latest mtime** wins
- 建议使用 **GitHub 私有仓库** / Use a **private GitHub repository** — memory is personal
- 可通过环境变量 `WORKBUDDY_WORKSPACE_ROOT` 指定自定义工作区根目录  
  Use env var `WORKBUDDY_WORKSPACE_ROOT` to override workspace root
