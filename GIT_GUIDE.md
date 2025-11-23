# Git 推送指南

## 1. 创建远程仓库

首先，在 GitHub、Gitee 或其他 Git 托管平台上创建一个新的空仓库。

## 2. 添加远程仓库

将以下命令中的 URL 替换为你的实际仓库地址：

```bash
# 对于 GitHub
git remote add origin https://github.com/你的用户名/仓库名.git

# 对于 Gitee
git remote add origin https://gitee.com/你的用户名/仓库名.git

# 或者使用 SSH（推荐）
git remote add origin git@github.com:你的用户名/仓库名.git
```

## 3. 推送到远程仓库

```bash
# 首次推送，设置上游分支
git push -u origin main

# 后续推送
git push
```

## 4. 配置本地环境

克隆仓库后，其他开发者需要：

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入实际的 API 密钥和配置

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 5. 安全注意事项

- **切勿**将 `.env` 文件提交到版本控制系统
- **切勿**在代码中硬编码 API 密钥
- 定期轮换 API 密钥
- 使用最小权限原则配置 API 密钥

## 6. 分支管理建议

```bash
# 创建新功能分支
git checkout -b feature/新功能名称

# 完成开发后，合并回主分支
git checkout main
git merge feature/新功能名称

# 删除已合并的分支
git branch -d feature/新功能名称
```