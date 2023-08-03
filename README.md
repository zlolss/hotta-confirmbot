# hotta-confirmbot

“幻塔”回归团挂件专用脚本，需要配合支持调试模式的安卓模拟器.
只推荐使用安卓模拟器的平板模式以1280x720分辨率运行游戏。

注意：
- 目前只支持adb同时连接一个设备。
- 部分模拟器（如mumu12）需要手动连接adb

已实现以下功能：

- 自动同意组队邀请
- 自动同意匹配
- 打完自动退出副本
- 公会频道自动冒泡
- 待机3分钟自动退队

# 安装

## python>=3.8

https://www.python.org/

## 自备adb
https://developer.android.google.cn/studio/command-line/adb?hl=zh-cn

下载后解压到项目根目录，或将所在路径加入到path环境变量中

## 需要的包

```python
pip install -r requirement.txt
```

# 使用说明
- 使用模拟器运行幻塔

- 命令行路径到脚本目录

```python
python run.py
```

# 引用
本项目中包含部分来自其他项目的预编译文件。

minitouch & minicap: 
https://github.com/bbsvip/minicap_minitouch_prebuilt.git

minicap-android-32：
https://github.com/varundtsfi/Android-sdk-32-minicap.git
https://github.com/NakanoSanku/minidevice

# 演示

https://www.bilibili.com/video/BV1bm4y1j7Sy/