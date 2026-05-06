---
title: "Windows (WSL2) 快速开始"
description: "在 Windows 上使用 WSL2 运行 Hermes Agent — CLI 和工具消息网关的受支持路径"
sidebar_label: "Windows (WSL2)"
sidebar_position: 2
---

# Windows (WSL2) 快速开始

Hermes Agent 是在 **Linux** 和 **macOS** 上开发和测试的。在 Windows 上，受支持的设置是 **WSL2**（Windows Subsystem for Linux），而不是传统的原生 Windows shell。

:::info 完整中文指南
详细的检查清单（WSL2、`uv`、仓库克隆、消息网关提示）以 **简体中文** 维护。请使用右上角的 **语言** 菜单，选择 **简体中文**，然后重新打开此页面。
:::

## 最小化路径

1.  安装 [WSL2](https://learn.microsoft.com/windows/wsl/install) 和一个较新的 Ubuntu（或其他受支持的发行版）。
2.  打开你的 WSL 终端，并在该执行环境中按照 [安装指南](/getting-started/installation) 操作。
3.  从 WSL 运行 `hermes model` / `hermes tools`，以确保路径、进程隔离和工具消息网关符合上游的预期。

关于工具消息网关和图像工具行为，请参阅 [工具消息网关](/user-guide/features/tool-gateway) 和 [图像生成](/user-guide/features/image-generation)。