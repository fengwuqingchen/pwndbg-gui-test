# pwndbg-gui

[![CodeQL](https://github.com/AlEscher/pwndbg-gui/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/AlEscher/pwndbg-gui/actions/workflows/github-code-scanning/codeql)

这是我从 [AlEscher/pwndbg-gui](https://github.com/AlEscher/pwndbg-gui) fork 的项目，目的是增加一些功能

## 待办

- [ ] 增加页码的功能，并且可以保留每个页面的记录，同时能够标记重点页面和进行注释
- [ ] 看一些能不能把 ida 结合起来，或者最好能结合使用多个反编译引擎，如果能有那种图形分支的界面或者反编译为c语言的调试能力就更好了
- [ ] 最重要的是能够和脚本一起进行调试
- [ ] 支持所有的gdb命令
- [ ] 如果可以的话看看能不能把模糊测试的工具也结合一下
- [ ] 对步进的系统调用进行记录
- [ ] 更方便的对内存进行操作，以及直接调用一些系统调用





如果已经有现成的方案的话就算了，比如ida的插件之类的
其次是现在还不确定一些方案的可行性

## 一些基础

暂时就是 README_zh.md 里面的东西，其他的暂时都不管



## 实现方式

该 GUI 使用 [Qt](https://doc.qt.io/qtforpython-6/) 框架进行 Python 编写。GDB 作为一个子进程在 [MI 模式](https://ftp.gnu.org/old-gnu/Manuals/gdb/html_chapter/gdb_22.html) 下运行，并通过 [pygdbmi](https://pypi.org/project/pygdbmi/) 与其交互。为了让 GUI 更加流畅，避免卡顿，应用程序是多线程的。主线程是 GUI 线程，其他线程负责与 GDB 的输入交互（`GdbHandler`）、收集 GDB 输出（`GdbReader`）和与子进程的交互（`InferiorHandler`）。

## 故障排除

- 如果在启动时遇到与 QT 插件未找到或加载有关的问题，请尝试为发生故障的用户设置 `QT_DEBUG_PLUGINS=1` 并重试。这将显示更多与 QT 相关的调试输出。很可能你缺少一些依赖项，可以通过你最喜欢的包管理器安装它们。在 Ubuntu/Debian 上，通常缺少的是 `libxcb-cursor0` 库。请参阅这个 [SO 帖子](https://stackoverflow.com/questions/68036484/qt6-qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-thou)。

## 外部依赖

- [Qt PySide6](https://www.qt.io/download-open-source) 作为 GUI 框架
- [Pygdbmi](https://github.com/cs01/pygdbmi) 用于与 GDB 的 MI 模式交互
- [psutil](https://pypi.org/project/psutil/) 用于跨平台访问进程信息

## 免责声明

该工具只是我个人对工具进行改进的尝试，请勿用于违法功能，造成的后果与本人无关，并且我想厉害的 pwner 应该也不会用我改烂的工具
