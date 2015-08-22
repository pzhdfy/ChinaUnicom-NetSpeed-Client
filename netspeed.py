#!/usr/bin/python
# coding=utf8
import urllib2
import urllib
import cookielib
import json
import time
import sys
import os
import socket
from BeautifulSoup import BeautifulSoup
import random
import logging
import logging.handlers
import time
reload(sys)
sys.setdefaultencoding('utf-8')
#ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.22 (KHTML, like Gecko) Maxthon/4.0.4.1012 Chrome/25.0.1364.99 Safari/537.22"

class NetSpeed(object):
    def __init__(self):
        self.initSelf()
        self.get_info()

    def initSelf(self):
        self.account = '100000000000'
        self.cid = self.genCompID()
        self.mac = self.randomMAC()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.handlers.SysLogHandler("/dev/log"))


    def parse_info(self, html):
        def clean_html(html):
            soup = BeautifulSoup(html)
            result = soup.find(id="webcode").string

            # Remove unexcepted ";" under OS X.
            return result.replace(";", "")

        html = clean_html(html)
        html = html.split('&')
        info = {}
        for i in html:
            tag, value = i.split('=')
            info[tag] = value

        return info

    def speed_up(self):
        uri = 'http://bj.wokuan.cn/web/improvespeed.php?ContractNo='+self.account+'&up='+self.new_speed_id+'&old='+self.old_speed_id+'&round='+self.random
        request = urllib2.Request(uri)
        response = urllib2.urlopen(request)
        html = response.read()
        return "success&00000000" in html

    def speed_heartbeat(self):
        uri = 'http://bj.wokuan.cn/web/updateforfifteenmin.php?Mactxt='+self.cid+'&ADSLTxt='+self.account+'&Tick='+str(random.randint(7000000, 17000000))+'&OEM='
        request = urllib2.Request(uri)
        response = urllib2.urlopen(request)
        html = response.read()
        return html

    def speed_down(self):
        uri = 'http://bj.wokuan.cn/web/lowerspeed.php?ContractNo='+self.account+'&round='+self.random
        request = urllib2.Request(uri)
        response = urllib2.urlopen(request)
        html = response.read()
        return "success&00000000" in html

    def get_info(self):
        uri = 'http://bj.wokuan.cn/web/startenrequest.php?ComputerMac=' + self.mac +'&ADSLTxt=' + self.account +'&Type=2&reqsn='+ self.genReqSN() +'&oem=00&ComputerId=' + self.cid
        request = urllib2.Request(uri)
        response = urllib2.urlopen(request)
        html = response.read()

        info = self.parse_info(html)

        self.id = info['cn']
        self.status = int(info['stu'])
        self.old_speed = info['os']
        self.old_speed_id = info['old']
        self.new_speed = info['up']
        self.new_speed_id = info['gus']
        self.hours = float(info['glst'])
        self.random = info['random']
        self.account = info['cn']

        if self.old_speed == "512":
            self.old_speed_unit_name = "Kbps"
        else:
            self.old_speed_unit_name = "Mbps"
            assert self.new_speed != "512"

    def randomMAC(self):
        mac = [ 0x52, 0x54, 0x00,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def genReqSN(self):
        return "00TF"+time.strftime('%Y%m%d%H%M')+"009262"

    def genCompID(self):
        str = 'BFEBFBFF'
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        length = len(chars) - 1
        for i in range(18):
            str+=chars[random.randint(0, length)]
        return str

if len(sys.argv) < 2:
    print(
    """使用说明:
        info -- 显示宽带信息
         up  -- 提速
        down -- 恢复""")
else:
    my_netspeed = NetSpeed()
    if sys.argv[1] == "info":
        print("SpeedUp: %s\nNormal speed: %s %s\nSpeedup speed: %s Mbps\nLeft time: %sh"
              % (bool(my_netspeed.status), my_netspeed.old_speed, my_netspeed.old_speed_unit_name,
                 my_netspeed.new_speed, my_netspeed.hours))
    elif sys.argv[1] == "up":
        status = my_netspeed.speed_up()
        while status == False:
            print("提升失败,60秒后重试!")
            logging.info("提升失败,60秒后重试!")
            time.sleep(60 * 1)
            status = my_netspeed.speed_up()
        print("提升成功.")
        logging.info("提升成功.")
        open('fail.log','a').write(str(time.localtime())+'\n')
        count = 0
        while True:
            time.sleep(60 * 10)
            #my_netspeed.speed_heartbeat()
            count += 1
            my_netspeed.get_info()
            if(count>=3):
                print("加速状态间隔三次，续期一次")
                logging.info("加速状态间隔三次，续期一次")
                status = my_netspeed.speed_up()
                if(status):
                    count = 0
                    print("续期成功.")
                    logging.info("续期成功.")
                else:
                    print("续期失败,下次重试!")
                    logging.info("续期失败,下次重试!")
            elif(bool(my_netspeed.status)):
                print("加速状态有效，无需处理")
                logging.info("加速状态有效，无需处理")
            else:
                print("加速状态失效，重新获取")
                logging.info("加速状态失效，重新获取")
                open('fail.log','a').write(str(time.localtime())+'\n')
                status = my_netspeed.speed_up()
                if(status):
                    count = 0
                    print("提升成功.")
                    logging.info("提升成功.")
                else:
                    print("提升失败,下次重试!")
                    logging.info("提升失败,下次重试!")

    elif sys.argv[1] == "down":
        status = my_netspeed.speed_down()
        if status:
            print("恢复成功.")
            logging.info("恢复成功.")
        else:
            print("恢复失败!")
            logging.info("恢复成失败!")
            sys.exit(1)
