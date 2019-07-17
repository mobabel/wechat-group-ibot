# wechat Group iBot

## 功能

* 定时检查群员昵称，如果不符标准，发送提醒信息
* 存储群聊天记录并且录入数据库
* 分析群成员昵称和历史聊天记录，制作各类图表
* 生成数据分析报告

## 1 环境和依赖

脚本兼容于Python 3

> 安装各类库

    pip3 install wxpy
    pip3 install apscheduler
    pip3 install pymysql
    pip3 install DBUtils
    
    pip3 install pandas
    pip3 install matplotlib
    pip3 install jieba
    pip3 install wordcloud
    pip3 install seaborn
    pip3 install palettable
    pip3 install pdfkit
    
> 安装 wkhtmltopdf
  
- Debian/Ubuntu:
~~~~
sudo apt-get install wkhtmltopdf
~~~~

- Redhat/CentOS
~~~~
sudo yum install wkhtmltopdf
~~~~

- MacOS
~~~~
brew install Caskroom/cask/wkhtmltopdf
~~~~
    
> 设置IDEA/PyCharm日志输出编码

    打开 Help 菜单, 点击 Edit Custom VM Options.
 
    添加 -Dconsole.encoding=UTF-8
 
    重启 IDEA 或 PyCharm.

> 在微信App里将所管理的群添加为群聊联系人
    
    这会加速群助手根据群名快速找到群
    
### 数据库准备

目前只支持mysql， sql脚本位于 ./sql/db_mysql.sql

> 请在脚本中修改你自己的database, username, password


## 2 可能遇到的问题

> 无法在命令行工具里扫描二维码登录

* 如果二维码变形, 请用 console_qr=1, 2 或其他值调整二维码
* 如果命令行工具是白色背景，请将console_qr设为负值

~~~~
bot = Bot(cache_path=True, console_qr=True)
->
bot = Bot(cache_path=True, console_qr=-2)
~~~~


## 3 如何开发

- ibot_gp_mb_vali.py

    - 按如下标准验证群友昵称:
        `nickname|branch&direction|language&framework`
    - 启动定时器，踢掉N次提醒后还坚持不改昵称的群友
    
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_welcome.jpg "Welcome member notification")
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_validate.jpg "Validate member notification")



- ibot_gp_helper.py

    - 监听群聊消息
    - 启动定时器，生成数据分析图表
    
> Charts

* 群聊记录云图
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_word_cloud.png "Chat history Wordcloud")
* 群员专业技术云图
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_branch_skill_gender.png "Member branch&skill Wordcloud")
* 群员性别构成饼图
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_gender_pie.png "Member gender pie chart")
* 群员活跃热力图
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/activity_heatmap.png "Member week activity heatmap")
* 群聊频率分析
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_freq_day_bar.jpg "Chat frequency dialy bar plot")
* 群聊日均分析
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_count_day_spot.png "Chat count dialy bar plot")
* 消息种类分析
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_msg_type_bar.jpg "Chat message type monthly")

    
    

> 设置

修改 wechat.conf 中的参数.


> 创建临时缓存文件夹并给予读写权限:

    mkdir /opt/tmp/ && chmod 700 /opt/tmp/


### 调试

> 在每个脚本里启动debug模式，避免打扰群

    debug = True
    
    
### 图灵机器人

> 图灵聊天机器人默认关闭，你可以启动并开发更多功能

    查看 tulingreply.py
    
    # wechat.conf
    tuling_api_key 需要填写

    
## 4 如何使用


### 直接运行脚本

> 直接运行

    python3 ibot_gp_mb_vali.py
    python3 ibot_gp_helper.py

> 如果扫码后无法登陆，请删除下面两个文件后再次尝试.

    rm -rf wxpy.pkl    
    rm -rf wxpy_puid.pkl    

### 在后台运行脚本

使用nohub启动脚本，就算关闭终端，也可以保持脚本在后台持续运行，
首先给予权限:

    chmod +x ibot_gp_mb_vali.py
    chmod +x ibot_gp_helper.py
    
    nohup python3 ibot_gp_mb_vali.py &
    nohup python3 ibot_gp_helper.py &

日志将存在 nohup.out里, 也可以存在其它路径:

    nohup python3 ibot_gp_mb_vali.py > log_vali.log &
    nohup python3 ibot_gp_helper.py > log_helper.log &

> Where is barcode?

本项目日志将存于 log_vali.log, log_helper.log 或 nohup.out


> 查找并且关闭后台ibot进程
    
    ps ax | grep ibot
    kill -7 process_id   



## 5 TODOs

* Support MongoDB
* More analysis charts for chat

    
## 链接

[wxpy Github](https://github.com/youfou/wxpy)

[wxpy Doc](https://wxpy.readthedocs.io/zh/latest/)

[Running a Python Script in the Background](https://janakiev.com/til/python-background/)