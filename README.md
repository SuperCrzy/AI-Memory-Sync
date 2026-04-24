# WorkBuddy Memory Sync

> 跨设备同步 WorkBuddy AI 记忆的 Skill —— 换台电脑，AI 依然记得你们聊过什么。  
> A WorkBuddy Skill to sync AI memory across devices — switch computers, AI still remembers everything.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-green)]()
[![Version](https://img.shields.io/badge/version-1.2.0-brightgreen)]()

---

## 为什么需要这个 Skill？ / Why?

**中文**

WorkBuddy 默认将 AI 的记忆（`.workbuddy/memory/`）存储在本地。当你在家里和 AI 聊了很多、建立了上下文之后，换到公司电脑，AI 对之前的一切一无所知。

这个 Skill 通过 GitHub 私有仓库，将所有工作区的记忆文件自动同步到云端，让你在任何设备上都能让 AI 延续之前的上下文。

**English**

WorkBuddy stores AI memory (`.workbuddy/memory/`) locally by default. When you've been working with AI at home and then switch to your office computer, the AI remembers nothing about your previous context.

This Skill syncs all workspace memory files to a private GitHub repository, so the AI can pick up right where you left off on any device.

```
Home Computer                    GitHub Private Repo              Office Computer
─────────────────                ─────────────────────            ─────────────────
.workbuddy/memory/    →  push →  memory/MEMORY.md      →  pull →  .workbuddy/memory/
WorkBuddy/<ws1>/...              workspaces/<ws1>/...             WorkBuddy/<ws1>/...
WorkBuddy/<ws2>/...              workspaces/<ws2>/...             WorkBuddy/<ws2>/...
```

---

## 功能特性 / Features

| 功能 / Feature | 说明 / Description |
|---|---|
| ✅ 一句话触发 / One-phrase trigger | 对 AI 说"同步记忆"即可 / Just say "sync memory" |
| ✅ 全量工作区扫描 / Full workspace scan | 自动扫描所有工作区，一次同步 / Auto-scans all workspaces in one shot |
| ✅ 跨平台 / Cross-platform | Windows / macOS / Linux |
| ✅ 冲突处理 / Conflict handling | 按最新修改时间合并 / Merge by latest mtime, never overwrites newer files |
| ✅ 版本历史 / Version history | 每次同步生成 Git commit，可随时回溯 / Every sync creates a Git commit |
| ✅ 隐私安全 / Privacy | 使用私有仓库，Token 仅存本地 / Private repo, Token stored locally only |
| ✅ 零依赖 / Zero dependencies | 只需 Python 3.8+ 和 Git / Only Python 3.8+ and Git required |

---

## 快速开始 / Quick Start

### 第一步 / Step 1：准备 GitHub 私有仓库 / Create a Private GitHub Repo

**中文**
1. 访问 [github.com/new](https://github.com/new)
2. 创建一个**私有（Private）仓库**，名称建议：`workbuddy-memory`
3. 勾选 **Add a README file**（仓库不能为空）

**English**
1. Go to [github.com/new](https://github.com/new)
2. Create a **Private** repository, recommended name: `workbuddy-memory`
3. Check **Add a README file** (the repo must not be empty)

---

### 第二步 / Step 2：获取 Personal Access Token / Get a Personal Access Token

**中文**
1. 访问 [GitHub Token 设置页](https://github.com/settings/tokens/new)
2. Note 填写：`workbuddy-memory-sync`
3. 权限勾选：`repo`（完整仓库读写权限）
4. 点击 **Generate token**，**立即复制**（只显示一次！）

**English**
1. Go to [GitHub Token settings](https://github.com/settings/tokens/new)
2. Note: `workbuddy-memory-sync`
3. Scope: check `repo` (full repository access)
4. Click **Generate token** and **copy immediately** (shown only once!)

---

### 第三步 / Step 3：安装 Skill / Install the Skill

**Windows：**
```powershell
git clone https://github.com/SuperCrzy/workbuddy-memory-sync "$env:USERPROFILE\.workbuddy\skills\memory-sync"
```

**macOS / Linux：**
```bash
git clone https://github.com/SuperCrzy/workbuddy-memory-sync ~/.workbuddy/skills/memory-sync
```

---

### 第四步 / Step 4：初始化配置 / Initialize Configuration

**对 AI 说 / Tell your AI:**

> 中文：「配置记忆同步，仓库是 `https://github.com/你的用户名/workbuddy-memory`，Token 是 `ghp_xxxxx`」  
> English: "Set up memory sync, repo is `https://github.com/yourname/workbuddy-memory`, token is `ghp_xxxxx`"

**或直接运行命令 / Or run directly:**

```bash
# Windows
python %USERPROFILE%\.workbuddy\skills\memory-sync\scripts\memory_sync.py setup --repo https://github.com/yourname/workbuddy-memory --token ghp_xxxxx

# macOS / Linux
python3 ~/.workbuddy/skills/memory-sync/scripts/memory_sync.py setup --repo https://github.com/yourname/workbuddy-memory --token ghp_xxxxx
```

---

## 使用方法 / Usage

### 对 AI 说话（推荐）/ Talk to AI (Recommended)

| 你说的话 / What you say | AI 执行的操作 / What AI does |
|---|---|
| 同步记忆 / 推送记忆 / sync memory / push memory | 将所有工作区 memory 推送到 GitHub |
| 拉取记忆 / 下载记忆 / pull memory / download memory | 从 GitHub 拉取最新 memory |
| 记忆同步状态 / memory sync status | 查看仓库和本地文件信息 |
| 配置记忆同步 / setup memory sync | 初始化配置 |

### 直接运行命令 / Run Commands Directly

```bash
# 推送记忆 / Push memory
python scripts/memory_sync.py push

# 拉取记忆 / Pull memory
python scripts/memory_sync.py pull

# 查看状态 / Check status
python scripts/memory_sync.py status

# 初始化配置 / Setup
python scripts/memory_sync.py setup
```

---

## 多设备同步工作流 / Multi-Device Workflow

```
第一台电脑（如家里）/ Device A (e.g. Home)      第二台电脑（如公司）/ Device B (e.g. Office)
──────────────────────────────────────          ──────────────────────────────────────
1. 安装 Skill / Install Skill                  1. 安装 Skill / Install Skill
2. 运行 setup，配置同一仓库 / Run setup         2. 运行 setup，配置同一仓库 / Run setup
3. 工作完成后说"同步记忆"       ─────────→      3. 开始工作前说"拉取记忆"
   (push to GitHub)                                (pull latest memory)
                                               4. AI 自动读取记忆，上下文恢复
                                                  AI resumes context seamlessly
```

---

## GitHub 仓库结构 / Repository Structure

同步后，你的 GitHub 私有仓库会按如下结构存储：  
After sync, your private GitHub repo stores files as:

```
workbuddy-memory/          (你的私有仓库 / your private repo)
├── memory/                ← 用户级记忆 / User-level memory (~/.workbuddy/memory/)
│   ├── MEMORY.md
│   └── 2026-04-24.md
└── workspaces/
    ├── workspace-id-1/    ← 工作区 1 记忆 / Workspace 1 memory
    │   ├── MEMORY.md
    │   └── 2026-04-24.md
    └── workspace-id-2/    ← 工作区 2 记忆 / Workspace 2 memory
        └── ...
```

---

## 文件结构 / Project Structure

```
memory-sync/
├── SKILL.md              # WorkBuddy Skill 描述 / Skill descriptor
├── README.md             # 本文档 / This document
├── LICENSE               # MIT License
├── .gitignore            # 排除配置文件（含 Token）/ Exclude config file (with Token)
└── scripts/
    └── memory_sync.py    # 核心同步脚本 / Core sync script
```

> 配置文件 `~/.workbuddy/memory-sync-config.json` 存储在用户目录，不包含在本仓库中。  
> Config file `~/.workbuddy/memory-sync-config.json` is stored in your home directory and never committed.

---

## 环境变量 / Environment Variables

| 变量 / Variable | 说明 / Description | 默认值 / Default |
|---|---|---|
| `WORKBUDDY_WORKSPACE_ROOT` | WorkBuddy 工作区根目录 / Workspace root | `~/WorkBuddy` |

---

## 冲突处理策略 / Conflict Resolution

**中文**：当两台设备都修改了同一个 memory 文件时，以**最新修改时间（mtime）**为准，更新的版本覆盖较旧的版本。每次推送都会产生一条 Git commit，可通过 `git log` 查看历史，随时回滚。

**English**: When the same memory file is modified on two devices, the version with the **newer modification time (mtime)** wins. Every push creates a Git commit, so you can always roll back via `git log`.

---

## 常见问题 / FAQ

**Q: 推送失败，提示 authentication failed？ / Push failed with "authentication failed"?**  
A（中）: Token 可能已过期，重新运行 `setup` 命令更新 Token。  
A（EN）: Your token may have expired. Re-run `setup` to update it.

**Q: 拉取后 AI 还是不记得之前的事？ / AI still doesn't remember after pull?**  
A（中）: 确认文件已拉取成功（运行 `status` 查看），然后**开启新的对话**，AI 会在会话开始时读取 memory。  
A（EN）: Confirm the files were pulled (run `status`), then **start a new conversation** — the AI reads memory at session start.

**Q: 能同步多少个工作区？ / How many workspaces can be synced?**  
A（中）: 没有限制，脚本会自动扫描 `~/WorkBuddy/` 下所有含 `.workbuddy/memory/` 目录的工作区，全部同步。  
A（EN）: No limit. The script auto-scans all workspaces under `~/WorkBuddy/` that contain a `.workbuddy/memory/` directory.

**Q: Token 安全吗？ / Is the Token safe?**  
A（中）: Token 仅存储在本地 `~/.workbuddy/memory-sync-config.json`，已加入 `.gitignore`，不会被上传到任何仓库。建议使用最小权限（仅 `repo`）并定期更换。  
A（EN）: The Token is only stored locally at `~/.workbuddy/memory-sync-config.json`, which is in `.gitignore` and never pushed. Use minimal scope (`repo` only) and rotate periodically.

**Q: 支持 Fine-grained Personal Access Token 吗？ / Fine-grained tokens supported?**  
A（中）: 支持。权限选择 `Contents: Read and write` 即可。  
A（EN）: Yes. Grant `Contents: Read and write` permission.

---

## 贡献 / Contributing

欢迎提 Issue 和 PR！  
Issues and PRs are welcome!

- 报告 Bug / Report bugs → [Issues](https://github.com/SuperCrzy/workbuddy-memory-sync/issues)
- 功能建议 / Feature requests → [Issues](https://github.com/SuperCrzy/workbuddy-memory-sync/issues)

---

## License

MIT © [SuperCrzy](https://github.com/SuperCrzy)
