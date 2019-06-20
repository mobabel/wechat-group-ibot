# wechat Group iBot

## Feature

* Scheduled to check member's nickname in group, if it is invalid, send message to them.
* Export chat history in group and save into database.
* Analyse group members' branches,  developing languages and chat statistic as well
* Generate statistic report

## 1 Environment and Dependency

Script is compatible with Python 3.

> Install libraries

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
    
> Install wkhtmltopdf
  
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
    
> Configure IDEA/PyCharm Output Encoding 

    On the Help menu, click Edit Custom VM Options.
 
    Add -Dconsole.encoding=UTF-8
 
    Restart IDEA or PyCharm.

> Add the watched groups as Group Chat Contact in WeChat App
    
    This will help bot to find the group depends on its name quickly
    
### Prepare database

Only mysql is supported currently, and the sql script locates in ./sql/db_mysql.sql

> Please change database, username, password as yours


## 2 Possible problems

> Can not scan the generated barcode to login

* If the barcode has been transformed, try to use console_qr=1, 2 or other int to adjust barcode
* If the background color of console is white, please change console_qr to minus value.

~~~~
bot = Bot(cache_path=True, console_qr=True)
->
bot = Bot(cache_path=True, console_qr=-2)
~~~~


## 3 How to develop

- ibot_gp_mb_vali.py

    - validate the nick names of member following the Group Naming Specification:
        `nickname|branch&direction|language&framework`
    - Start scheduler to kick out member after noticing > N times
    
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_welcome.jpg "Welcome member notification")
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_validate.jpg "Validate member notification")



- ibot_gp_helper.py

    - group message listener
    - scheduler for group chat analyzing and generating charts
    
> Charts

* Chat history Wordcloud
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_word_cloud.png "Chat history Wordcloud")
* Member branch&skill Wordcloud
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_branch_skill_gender.png "Member branch&skill Wordcloud")
* Member gender pie chart
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/member_gender_pie.png "Member gender pie chart")
* Member week activity heatmap
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/activity_heatmap.png "Member week activity heatmap")
* Chat frequency dialy bar plot
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_freq_day_bar.jpg "Chat frequency dialy bar plot")
* Chat count dialy bar plot
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_count_day_spot.png "Chat count dialy bar plot")
* Chat message type monthly
![Demo 1](https://raw.githubusercontent.com/mobabel/wechat-group-ibot/master/wiki/chat_msg_type_bar.jpg "Chat message type monthly")

    
    

> Configuration

Edit wechat.conf and modify variables.


> Make directory and grant permission for path_tmp, for example:

    mkdir /opt/tmp/ && chmod 700 /opt/tmp/


### Debug

> Enable debug in each script to avoid disturbing group chat

    debug = True
    
    
### Tuling robot

> Tuling chat robot is deactivated currently, but you can activate it and implement more features.

    view tulingreply.py
    
    # wechat.conf
    tuling_api_key is required

    
## 4 How to use


### Run executable py directly

> Run directly

    python3 ibot_gp_mb_vali.py
    python3 ibot_gp_helper.py

> If you cannot login after barcode scan, try to delete the two files and try again.

    rm -rf wxpy.pkl    
    rm -rf wxpy_puid.pkl    

### Run script in background

Run the script with nohup which ignores the hangup signal. 
This means that you can close the terminal without stopping the execution. 
Also, don’t forget to add & so the script runs in the background:

    chmod +x ibot_gp_mb_vali.py
    chmod +x ibot_gp_helper.py
    
    nohup python3 ibot_gp_mb_vali.py &
    nohup python3 ibot_gp_helper.py &

The output will be saved in the nohup.out file, unless you specify the log file like here:

    nohup python3 ibot_gp_mb_vali.py > log_vali.log &
    nohup python3 ibot_gp_helper.py > log_helper.log &

> Where is barcode?

Logs will be outputed into log_vali.log, log_helper.log or nohup.out, as demand.


> Terminate ibot.py in thread
    
    ps ax | grep ibot
    kill -7 process_id   



## 5 TODOs

* Support MongoDB
* Analysis for members group names
* More analysis charts for chat

    
## Links

[wxpy Github](https://github.com/youfou/wxpy)

[wxpy Doc](https://wxpy.readthedocs.io/zh/latest/)

[Running a Python Script in the Background](https://janakiev.com/til/python-background/)