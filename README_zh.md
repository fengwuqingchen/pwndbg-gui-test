### pwndbg-gui

[![CodeQL](https://github.com/AlEscher/pwndbg-gui/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/AlEscher/pwndbg-gui/actions/workflows/github-code-scanning/codeql)

这是我从 [AlEscher/pwndbg-gui](https://github.com/AlEscher/pwndbg-gui) fork 的项目，目的是增加一些功能



## 安装设置

1. 安装并设置 [pwndbg](https://github.com/pwndbg/pwndbg#how)

2. 可选地在 `~/.gdbinit` 文件中添加所需的设置

3. 运行 

   ```
   python start.py
   ```

   - 这将创建一个虚拟环境并安装所需的依赖项
   - 在 Debian/Ubuntu 系统上，可能需要先安装 `python3-venv`
   - 如果你希望附加到正在运行的程序，GDB 需要使用 `sudo` 启动。为此，将 `~/.gdbinit` 复制到 `/root` 目录并运行 `python start.py --sudo`，在提示时输入你的 sudo 密码

## 特性

- 可调整大小和折叠的面板
- 堆上下文
  - 持续显示堆相关信息，如分配的内存块和已释放的内存块
  - 提供快速访问 `pwndbg` 的 `try_free` 命令
- 监视上下文
  - 向监视上下文添加多个地址，以十六进制格式持续监控数据
- 栈和寄存器上下文的上下文菜单，允许通过 `xinfo` 命令轻松查找
- 键盘快捷键
  - 支持 GDB 命令和 GUI 功能的快捷键
  - 快捷键要么显示在菜单中的动作旁边（例如 `Ctrl + N`），要么通过下划线字母显示（按下 `Alt + <字母>` 激活按钮/菜单）
- 输入字节文字
  - 当向子进程输入数据时（由主面板输入框旁的标签表示），你可以提供 Python `bytes` 字面量
  - 例如：输入 `b"Hello\x00World\n"` 将按字节文字解释输入并相应地进行评估
- 所有现有的 GDB / `pwndbg` 命令仍然可以通过主输入框执行

## 预览

![Overview Running](https://chatgpt.com/c/screenshots/OverviewRunning.png)

## 动机

`pwndbg` 是一个命令行工具，通过让用户更容易地查看数据并添加许多新命令，大大增强了 `gdb` 的功能。作为调试和攻击的主流工具，它们主要受制于终端应用的局限性。为了解决这个问题，我们希望利用现代 UI 框架将最重要的功能封装起来。这使得我们可以筛选、重新排序和自定义 GDB 输出，简化或突出显示重要信息。我们的 GUI 应用程序主要侧重于提高可用性，减少用户命令，整齐地显示信息，轻松复制数据，并提供控制流的快捷键。

## 实现方式

该 GUI 使用 [Qt](https://doc.qt.io/qtforpython-6/) 框架进行 Python 编写。GDB 作为一个子进程在 [MI 模式](https://ftp.gnu.org/old-gnu/Manuals/gdb/html_chapter/gdb_22.html) 下运行，并通过 [pygdbmi](https://pypi.org/project/pygdbmi/) 与其交互。为了让 GUI 更加流畅，避免卡顿，应用程序是多线程的。主线程是 GUI 线程，其他线程负责与 GDB 的输入交互（`GdbHandler`）、收集 GDB 输出（`GdbReader`）和与子进程的交互（`InferiorHandler`）。

## 故障排除

- 如果在启动时遇到与 QT 插件未找到或加载有关的问题，请尝试为发生故障的用户设置 `QT_DEBUG_PLUGINS=1` 并重试。这将显示更多与 QT 相关的调试输出。很可能你缺少一些依赖项，可以通过你最喜欢的包管理器安装它们。在 Ubuntu/Debian 上，通常缺少的是 `libxcb-cursor0` 库。请参阅这个 [SO 帖子](https://stackoverflow.com/questions/68036484/qt6-qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-thou)。

## 外部依赖

- [Qt PySide6](https://www.qt.io/download-open-source) 作为 GUI 框架
- [Pygdbmi](https://github.com/cs01/pygdbmi) 用于与 GDB 的 MI 模式交互
- [psutil](https://pypi.org/project/psutil/) 用于跨平台访问进程信息

## 免责声明

该工具是作为 TUM（慕尼黑工业大学）**二进制利用实操课程**的项目开发的。所有功能都针对该课程中的 pwning 挑战。如果你喜欢这个工具，但有当前不支持的使用案例，欢迎打开 PR 或提出问题。
