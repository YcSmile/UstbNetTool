# -*- coding: utf-8 -*-
# @Author: YcSmile
# @Date:   2017-09-19 14:46:11
# @Last Modified by:   YcSmile
# @Last Modified time: 2017-11-16 10:47:00
import os
import sys

import requests

import socket
import fcntl
import json
import re

class BeikeNet():
    # 配置 
    config = {
        'username':'xx',
        'userpass':'xx'
    }
    WebHeader = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        #'If-None-Match':'W/"e67178ec12bc19406c58d87f79587ef3"',
        #'host':'www.xicidaili.com',
        # 'Cookie':'myusername={0}; username={1}',
        'Host':'202.204.48.66',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }

    UstbUrls = {
        'login':        'http://202.204.48.66/',            # 登录地址
        'logout':       'http://202.204.48.66/F.html',      # 本机注销
        'ipv4_server':{
            'addr':'202.204.48.66',
            'port':80
        },
        'ipv6_head':'2001:da8',                              # ipv6头
        'ipv6_server':{                                     # 获取ipv6 地址
            'addr':'2001:da8:208:100::115',
            'port':80
        },
        'gg_server':{                                       # 测试链接 hk
            'addr':'2404:6800:4008:c00::c7',
            'port':443
        },
    }

    UstbRekey = {
        'key_login':r'<script language="JavaScript"><!--\s(.*?)\s--></script>',
    }

    def __init__(self,cfg_file):
        self.cfg_file = cfg_file
        if os.path.exists(cfg_file):
            self.load_config()
        else:
            self.creat_config()

    def load_config(self):
        self.config = {}
        with open(self.cfg_file,'r') as pf:
            text = pf.read()
            self.config = json.loads(text)
            # 校验参数

    def creat_config(self):
        print('creat config file')
        try:
            user_name = input('user name:')
            user_pass = input('user passwd:')
            self.config = {
                'username':user_name,
                'userpass':user_pass
            }
            if 0 == self.login():
                self.config = {}
            else:
                with open(self.cfg_file,'w') as pf:
                    pf.write(json.dumps(self.config))
        except Exception as e:
            pass
    def recreat_config(self):
        if os.path.exists(self.cfg_file):
            os.remove(self.cfg_file)
        self.creat_config()

    # ------------ mathod
    def get_info(self,html,key):
        match = re.search(key, html, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).replace(' ','').replace('\r\n','').replace(';',';\n') # 抓取
        else:
            return ""

    def get_value(self,text,key,default_value=''):
        match = re.search(key + r'=(.*?);', text, re.DOTALL)
        if match:
            result = match.group(1).replace('\'','')
            return(result)
        return default_value

    # ----------- 主操作 ----------------
    # 获取信息账户信息
    def print_infos(self,infos):
        # 输出信息
        BKNet_UID   = '当前用户:{0}'
        BKNet_TIME   = '使用时长:{0}时 {1}分'
        BKNet_UEDV4 = 'V4使用流量: {0}G {1}M'
        BKNet_UEDV6 = 'V6使用流量: {0}G {1}M'
        BKNet_MON = '剩余金额:{0}元'
        BKNet_V4IP = 'IPv4地址:{0}'
        BKNet_V6IP = 'IPv6地址:{0}'

        print(BKNet_UID.format(infos['uid']))
        print(BKNet_TIME.format(infos['time'] // 60 ,infos['time']%60 ))
        print(BKNet_MON.format( infos['fee'] / 10000))
        if infos['mode'] == '4' or infos['mode'] == '12': # v6模式
            print('上网模式: Ipv4 & v6 模式')
            print(BKNet_UEDV4.format(  infos['v4_flow']// 1024// 1024,infos['v4_flow'] // 1024 % 1024 ))
            print(BKNet_UEDV6.format(  infos['v6_flow']// 1024// 1024,infos['v6_flow'] // 1024 % 1024 ))
            print(BKNet_V4IP.format(infos['v4ip']))
            print(BKNet_V6IP.format(infos['v6ip']))
        else:
            print('上网模式: Ipv4  模式')
            print(BKNet_UEDV4.format(  infos['v4_flow']// 1024// 1024,infos['v4_flow'] // 1024 % 1024 ))
            print(BKNet_V4IP.format(infos['v4ip']))            

    def infos(self):
        
        self.WebHeader['Cookie'] = 'myusername={0}; username={0}'.format(self.config['username'])
        html = self.light_get(url=self.UstbUrls['login'],headers =   self.WebHeader)
        info = self.get_info(html,self.UstbRekey['key_login'])
        # 判断是否是已经登录
        user_info = {}
        if self.get_value(info,'uid','0') == self.config['username']:
            # 已经登录
            user_info['status']='已登录'

            user_info['uid'] = self.get_value(info,'uid')
            user_info['time'] = int(self.get_value(info,'time','0'))
            user_info['fee'] = int(self.get_value(info,'fee','0'))
            user_info['mode'] = self.get_value(info,'v46m','')

            user_info['v4_flow'] = int(self.get_value(info,'flow','0'))

            user_info['v6_flow'] = int(self.get_value(info,'v6af','0'))

            user_info['v4ip'] = self.get_value(info,'v4ip','')

            user_info['v6ip'] = self.get_value(info,'v6ip','')


            return  self.print_infos( user_info)
        else:
            print('登录状态:','未登录')

    # 校园网登录
    def login(self):
        ipv6_addr = self.get_ip(socket.AF_INET6,self.UstbUrls['ipv6_server'])
        # 检验ip地址
        # # 测试 ip v6 登录 登录成功
        if self.UstbUrls['ipv6_head'] not in ipv6_addr: # 未获取ipv6地址
            ipv6_addr = ''
        # 等咯提交数据
        login_data = {
            'DDDDD' : self.config['username'],
            'upass' : self.config['userpass'],
            # 'upass' : '123',
            'v6ip' : ipv6_addr,
            '0MKKey':'123456789'
        }

        self.WebHeader['Cookie'] = 'myusername={0}; username={0}'.format(self.config['username'])
        html = self.light_post(url = self.UstbUrls['login'],post_data=login_data,headers =   self.WebHeader)

        info = self.get_info(html,self.UstbRekey['key_login'])
        Gno = self.get_value(info,'Gno')
        if '15' == Gno:
            # 判断ipv6是否登录成功2
            if '' != ipv6_addr:
                if self.ipv6_conn_test(ipv6_addr):
                    print('登录状态:','登录成功')
                    self.infos()
                    return 1
            else:
                print('登录状态:','登录失败')
                return 0
                
        else:
            # 处理错误信息
            Msg = self.get_value(info,'Msg')
            msga = self.get_value(info,'msga')
            if Msg == '01':
                pass
            print('登录状态:','登录失败')
            return 0

    # 注销 - 直接请求地址为注销
    def logout(self):
        
        self.WebHeader['Cookie'] = 'myusername={0}; username={0}'.format(self.config['username'])
        html = self.light_get(url=self.UstbUrls['logout'],headers =   self.WebHeader)

        info = self.get_info(html,self.UstbRekey['key_login'])
        Msg = self.get_value(info,'Msg')
        if Msg == '14':
            print('登录状态:','已注销')
        else:
            print('登录状态:','未知错误')

    # 测试 ip v6 是不是联通
    def ipv6_conn_test(self,ipv6_addr):
        ipv6_addr_temp =  self.get_ip(socket.AF_INET6,self.UstbUrls['gg_server'])

        if ipv6_addr_temp == ipv6_addr:
            return True
        else:
            return False

    def get_ip(self,ip_type,server):
        ip = ''
        try:
            s = socket.socket(ip_type, socket.SOCK_DGRAM)
            s.connect((server['addr'], server['port']))    # google hk
            ip = s.getsockname()[0]
        except Exception as e:
            pass
        finally:
            s.close()
        return ip
    
    def light_get(self,url,headers=None,proxy=None):
        try:
            resp = requests.get(url,timeout=5,proxies=proxy)
            return resp.text
        except Exception as e:
            return ''

    def light_post(self,url,post_data=None,headers=None,proxy=None):
        try:
            resp = requests.post(url,data=post_data,timeout=5,proxies=proxy)
            return resp.text
        except Exception as e:
            return ''

def UstbNetTool_usage():
    print('------------ Usage -------------')
    print('[ 1:登录 ]')
    print('[ 2:查询 ]')
    print('[ 3:本机注销 ]')
    print('[ 4:重新生成配置文件 ]')
    print('默认:无')

def main():
    UBTool = BeikeNet('./config.cfg')

    UstbNetTool_usage()

    argv = input('输入:')
    if argv not in ('1','2','3','4'):
        print('# 参数错误')
        sys.exit(0)

    if argv in ['1']:
        UBTool.login()
    elif argv in ['2']:
        UBTool.infos()
    elif argv in ('3'):
        UBTool.logout()
    elif argv in ['4']:
        UBTool.recreat_config()

    print('执行结束')


if __name__ == '__main__':
    main()
    