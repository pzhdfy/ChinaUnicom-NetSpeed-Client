中国联通带宽客户端
===========================
在某些情况下，只有使用联通沃宽客户端才可获得较高网速，但此客户端不跨平台。本程序是其跨平台的替代品。

版本
---------------------------
本程序是命令行版本。

依赖关系
---------------------------
### 命令行版本 ###
1. Python (2.7测试) 
2. BeautifulSoup
3. urllib2

用法
---------------------------
### 命令行版本 ###

1. `./netspeed.py info` 将显示网速信息。
2. `./netspeed.py up` 将会提速带宽,每10分钟发送心跳包。
3. `./netspeed.py down` 将会恢复原始带宽。

### 使用 ###
1. 直接用命令行 `./netspeed.py up & >/dev/null`
2. supervisor
```
[program:speed]
command=/app/speed/netspeed.py up
directory=.
autostart=true
autorestart=true
stdout_logfile = /var/log/supervisor/speed.log
```
