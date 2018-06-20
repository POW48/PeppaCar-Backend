# 小車（jū）佩奇后端

## 简介

这是我们（[@chengluyu](https://github.com/chengluyu)、[@Talegqz](https://github.com/Talegqz) 和 [@jack-z](https://github.com/z-jack)）嵌入式系统设计课程的大实验。我们制作了一个树莓派小车，其可以完成如下任务：

- 循线避障：沿着车下的黑色线条行走，并且绕过黑色线条上的障碍物。
- 推球入门：识别场地中的球和球门，把球推入球门。

## 小车结构

构筑小车使用了以下组件：

- 马达（4 个）
- 轮胎（4 个）
- 超声波传感器（1 个）
- 红外线传感器（3 个）
- 轨道检测器（3 个）
- 树莓派 3B V1.2（1 个）
- 树莓派 NoIR 摄像头（1 个）
- 某不知名 7.5 V 1500 mAh 可充电锂电池（1 个）
- 某米移动电源 5000 mAh（1 个）
- 面包版（1 个）
- 杜邦线若干
- 3 mm 和 2mm 螺丝螺母若干
- 热熔胶

## 程序结构

- `ball_utils` 用于推球任务的若干函数
- `camera` 用于视频串流和物体识别的类
- `find_track_and_avoid` 循线避障任务的若干函数
- `local_camera`、`test_camera` 和 `threadhold_camera` 用于在电脑上测试摄像头物体识别的实验模块
- `scheduler` 一个用于定时规划任务的事件队列
- `server` 前端和后端的服务器
- `ultrasonic` 超声波传感器模块

## 问与答

<details>
<summary>为什么有这么多 commit？</summary>
我们的 git repo 除了有指向 GitHub 上的 remote 外，还有一个 remote 指向小车的树莓派上，我们开发时在本地做完修改直接 push 到树莓派上。因此每一个微小的修改（改时间、参数、距离、拼写错误、语法错误）都会构成一个 commit。
</details>

