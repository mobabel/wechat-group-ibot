# encoding: utf-8

import re
import collections
import operator
import random
import numpy as np
from PIL import Image
from pathlib import Path
import csv
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from palettable.colorbrewer.sequential import *
import pdfkit

# local python lib
import wechat_const
from ibot_utils import *


class BotAnalyze(object):
    """
    Bot Analyse object::

        from ibot_chat_analyse import *
        ba = BotAnalyze(bot, bot_group)
        ba.start_analysis_tasks()


    """

    def __init__(self, bot_db, bot, bot_group):
        # read configuration
        self.debug = False
        self.fl_days = get_first_last_days()

        # init file handler
        self.path_analyse = get_path_custom('analyse')

        self.bot_db = bot_db
        self.bot = bot
        self.bot_group = bot_group

        try:
            self.group_id = bot_group.ext_attr.group_id
            self.group_name = bot_group.ext_attr.group_name
        except AttributeError:
            self.group_id = 1
            pass

    def load_chat_history(self, group_id, date_begin, date_end):
        return self.bot_db.select("SELECT `id`,`msg_type`,`wx_puid`,`sender_name`,`msg`,`create_time` "
                                  "FROM wx_chat_history WHERE `group_id` = %s"
                                  " AND `create_time` >= %s AND `create_time` <= %s ",
                                  (group_id, date_begin, date_end))

    @staticmethod
    def format_message(msg):
        msg = msg.replace('\n', ' ')
        if msg.find('昵称未设置或不符合标准') >= 0:
            msg = ''
        if msg.find('下次将无警告直接踢出群') >= 0:
            msg = ''
        return msg

    @staticmethod
    # r'(@([\u4e00-\u9fa5]|[ -~]|[\s\S])%s)|(@([\u4e00-\u9fa5]|[ -~]|[\s\S]))'
    def filter_message(msg):
        # get @nickname, if it locates at the end, there is not space char
        try:
            nickname = re.search(r'@(.+?)%s|@(.+?)+' % wechat_const.space_after_chat_at, msg).group(0)
            msg = msg.replace(nickname, '')
        except AttributeError:
            pass

        # TODO no so pretty here, should filter with nickname list
        msg = msg.replace('@野生小新|IoT|全栈构架', ' ')
        msg = msg.replace('哈哈', '')

        return msg

    def save_chat_in_current_month(self, group_id):
        results = self.load_chat_history(group_id, self.fl_days[0], self.fl_days[1])
        path_csv_file = os.path.join(self.path_analyse,
                                     '%s_chat_%s_%s.csv' % (self.group_id, self.fl_days[0], self.fl_days[1]))

        with open(path_csv_file, mode='w', encoding='utf-8') as csv_file:
            fieldnames = ['id', 'create_time', 'msg_type', 'wx_puid', 'sender_name', 'msg']
            csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            csv_writer.writerow(fieldnames)
            for row in results:
                row_id = row[0]
                msg_type = row[1]
                wx_puid = row[2]
                sender_name = row[3]
                msg = row[4]
                create_time = row[5]

                msg = self.format_message(msg)

                csv_writer.writerow([row_id, create_time, msg_type, wx_puid, sender_name, msg])

        csv_file.close()

        return path_csv_file

    @staticmethod
    def load_stopwords():
        filepath = os.path.join('./assets', r'stopwords_cn.txt')
        stopwords = [line.strip() for line in open(filepath, encoding='utf-8').readlines()]
        # print(stopwords) # ok
        return stopwords

    @staticmethod
    def load_stopwords_it(column='all'):
        if column == 'all':
            filepath_branch = os.path.join('./assets', r'stopwords_it_branch.txt')
            stopwords_branch = [line.strip() for line in open(filepath_branch, encoding='utf-8').readlines()]
            filepath_language = os.path.join('./assets', r'stopwords_it_language.txt')
            stopwords_language = [line.strip() for line in open(filepath_language, encoding='utf-8').readlines()]
            stopwords = set()
            stopwords.append(stopwords_branch)
            stopwords.append(stopwords_language)
        else:
            filepath = os.path.join('./assets', r'stopwords_it_%s.txt' % column)
            stopwords = [line.strip() for line in open(filepath, encoding='utf-8').readlines()]

        return stopwords

    def gen_wordcloud_chat_history(self, csv_file):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')
        # print(len(df))
        # print(df.head())

        stopwords = set(STOPWORDS)
        stopwords.update(self.load_stopwords())
        message = df['msg']
        word_count = ""
        for msg in message:
            if msg is not np.NaN:
                msg = self.filter_message(msg)
                seg_list = jieba.cut(msg, cut_all=True, HMM=True)
                for word in seg_list:
                    word_count = word_count + word + " "

        shape_file = './assets/chat_history_shape.png'
        shape = np.array(Image.open(shape_file))
        font = r'./assets/heiti.ttf'

        word_cloud = WordCloud(
                        margin=2,
                        mask=shape,
                        font_path=font,
                        scale=1,
                        # max_words=200,
                        # min_font_size=4,
                        # max_font_size=150,
                        stopwords=stopwords,
                        random_state=42,
                        background_color='white',
                        width=1080,
                        height=720).generate(word_count)

        path_image = os.path.join(self.path_analyse,
                                  '%s_chat_word_cloud_%s_%s.png' % (self.group_id, self.fl_days[0], self.fl_days[1]))
        word_cloud.to_file(path_image)
        return path_image

    @staticmethod
    def cal_time_list_chat_freq_day(df):
        time_list = {}

        # 2019-05-29 09:41:25
        create_times = df['create_time']
        for create_time in create_times:
            dt_stamp = mk_datetime(create_time)
            hour_in_24 = dt_stamp.hour
            if hour_in_24 in time_list:
                time_list[hour_in_24] = time_list[hour_in_24] + 1
            else:
                time_list[hour_in_24] = 1

        # fulfill the time list
        for i in range(0, 24):
            if i not in time_list:
                time_list[i] = 0

        time_list = collections.OrderedDict(sorted(time_list.items()))
        return time_list

    def gen_bar_plot_msg_type(self, csv_file):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')

        df['msg_type'].value_counts().plot(kind='bar')

        plt.subplots_adjust(bottom=0.2)
        plt.title('Message Type [%s - %s]' % (self.fl_days[0], self.fl_days[1]))
        path_image = os.path.join(self.path_analyse,
                                  '%s_chat_msg_type_bar_%s_%s.png' % (self.group_id, self.fl_days[0], self.fl_days[1]))
        plt.savefig(path_image)
        plt.close()

        return path_image

    def gen_bar_plot_chat_freq_day(self, csv_file):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')
        msg_count = len(df)

        time_list = self.cal_time_list_chat_freq_day(df)

        plt.figure(figsize=(18, 9))
        plt.bar(time_list.keys(), time_list.values(), width=.8, facecolor='lightskyblue', edgecolor='white')
        plt.xticks(range(len(time_list)), time_list.keys())
        for x_axies in time_list:
            y_axies = time_list[x_axies]
            label = '{}%'.format(round(y_axies*1.0/msg_count*100, 2))
            plt.text(x_axies, y_axies+0.05, label, ha='center', va='bottom')
        plt.title('Chat frequency in 24 hours [%s - %s]' % (self.fl_days[0], self.fl_days[1]))
        path_image = os.path.join(self.path_analyse,
                                  '%s_chat_freq_day_bar_%s_%s.png' % (self.group_id, self.fl_days[0], self.fl_days[1]))
        plt.savefig(path_image)
        plt.close()

        return path_image

    def gen_spot_plot_chat_count_day(self, csv_file):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')

        time_list = self.cal_time_list_chat_freq_day(df)
        max_freq = max(time_list.items(), key=operator.itemgetter(1))[0]

        x = []
        y = []
        for i in range(0, 24):
            x.append(str(i)+':00-'+str(i+1)+':00')
            y.append(time_list[i])
        x_array = np.array(x)
        y_array = np.array(y)
        # plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.figure(figsize=(16, 9))
        plt.subplots_adjust(bottom=0.2)
        plt.scatter(x_array, y_array, color="blue", label="times")
        plt.xlabel('Time 00:00—24:00')
        plt.ylabel('Chat Frequency [%s - %s]' % (self.fl_days[0], self.fl_days[1]))
        plt.xticks(range(0, 24), rotation=75, fontsize=10)
        plt.yticks(range(0, max_freq + 200, 20))
        # plt.legend(loc='lower right')
        # plt.show()
        path_image = os.path.join(self.path_analyse,
                                  '%s_chat_count_day_spot_%s_%s.png'
                                  % (self.group_id, self.fl_days[0], self.fl_days[1]))
        plt.savefig(path_image, format='png')
        plt.close()

        return path_image

    '''
    member activity heat map
    :param csv_file: csv file dir
    '''
    def gen_heatmap_member_activity(self, csv_file):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')
        create_times = df['create_time']

        week_online = [[0 for j in range(24)] for i in range(7)]
        for li in create_times:
            week_online[int(mk_datetime(li, "%Y-%m-%d %H:%M:%S").weekday())][int(li[11:13])] += 1

        week_online = np.array([li for li in week_online])
        columns = [str(i) + '-' + str(i + 1) for i in range(0, 24)]
        index = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']

        week_online = pd.DataFrame(week_online, index=index, columns=columns)
        plt.figure(figsize=(18.5, 9))
        plt.rcParams['font.sans-serif'] = ['SimHei']
        sns.set()

        # Draw a heatmap with the numeric values in each cell
        sns.heatmap(week_online, annot=True, fmt="d", cmap="YlGnBu")
        path_image = os.path.join(self.path_analyse,
                                  '%s_activity_heatmap_%s_%s.png' % (self.group_id, self.fl_days[0], self.fl_days[1]))
        plt.savefig(path_image, format='png', dpi=300)
        plt.close()

        return path_image

    @staticmethod
    def get_info_from_nickname(nickname):
        nickname = str.strip(nickname)
        nickname = nickname.replace('  ', ' ')

        nickname = nickname.replace('｜', '|')

        nickname = nickname.replace(' | ', '|')
        nickname = nickname.replace('| ', '|')
        nickname = nickname.replace(' |', '|')

        nickname = nickname.replace('&amp;', '&')

        branch = ''
        language = ''
        reg = r'([\u4e00-\u9fa5]|[ -~]|[\s\S])+\|([\u4e00-\u9fa5]|[ -~])+\|([\u4e00-\u9fa5]|[ -~])+'
        if re.match(reg, nickname):
            try:
                parsed = re.split(r'\|', nickname)
                branch = parsed[1]
                language = parsed[2]
            except AttributeError:
                pass

        return [branch, language]

    @staticmethod
    def format_readable_nickname(text):
        text = text.replace('&amp;', '&')
        return text

    @staticmethod
    def convert_it_term(text, word_count):
        if re.search(r'c\+\+', text, re.IGNORECASE):
            word_count = word_count + 'Cpp' + " "
        if re.search(r'\s.*?\s', text, re.IGNORECASE):
            word_count = word_count + 'C语言' + " "
        return word_count

    def save_member_detail_list(self):
        # include region, gender, signature
        self.bot_group.update_group(members_details=True)

        path_csv_file = get_path_custom('group_member') + '/%s_member_detail.csv' % self.group_id

        with open(path_csv_file, mode='w', encoding='utf-8') as csv_file:
            fieldnames = ['puid', 'nickname', 'gender', 'branch', 'language']
            csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            csv_writer.writerow(fieldnames)
            for member in self.bot_group:
                nickname = member.name  # display_name
                wx_puid = member.puid
                nickname = self.format_readable_nickname(nickname)
                gender = member.sex
                result = self.get_info_from_nickname(nickname)

                csv_writer.writerow([wx_puid, nickname, gender, result[0], result[1]])

        csv_file.close()

        return path_csv_file

    @staticmethod
    def color_func_gray(word, font_size, position, orientation, random_state=None, **kwargs):
        return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

    @staticmethod
    def color_func_red(word, font_size, position, orientation, random_state=None, **kwargs):
        # https://jiffyclub.github.io/palettable/colorbrewer/sequential
        return tuple(Reds_9.colors[random.randint(2, 8)])

    @staticmethod
    def color_func_blue(word, font_size, position, orientation, random_state=None, **kwargs):
        return tuple(Blues_9.colors[random.randint(2, 8)])

    @staticmethod
    def color_func_YlGn_9(word, font_size, position, orientation, random_state=None, **kwargs):
        return tuple(YlGn_9.colors[random.randint(2, 8)])

    @staticmethod
    def color_func_PuBu_9(word, font_size, position, orientation, random_state=None, **kwargs):
        return tuple(PuBu_9.colors[random.randint(2, 8)])

    '''
    wordcloud for branches & languages information of members' nickname
    :param csv_file: csv file dir
    :param column: column name: branch, language
    :param gender: all:all, male:male+unknown, female:female
    '''
    def gen_wordcloud_info_nicknames(self, csv_file, column='branch', gender='all'):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')

        if column == 'branch':
            # label_column = 'Branches which members[%s] are working in' % gender
            stopwords = set(STOPWORDS)
            stopwords.update(self.load_stopwords())
            stopwords.update(self.load_stopwords_it('branch'))
        elif column == 'language':
            # label_column = 'Languages&Framework which members[%s] are working with' % gender
            stopwords = set()
            stopwords.update(self.load_stopwords())
            stopwords.update(self.load_stopwords_it('language'))

        jieba.load_userdict("./assets/jieba_userdict.txt")

        if gender == 'male':
            df_male = df[df.gender == 1]
            col = df_male[column]
            shape_file = './assets/member_%s_%s_shape.png' % (column, gender)
            shape_alpha_file = './assets/member_%s_%s_shape_alpha.png' % (column, gender)
        elif gender == 'female':
            df_male = df[df.gender == 2]
            col = df_male[column]
            shape_file = './assets/member_%s_%s_shape.png' % (column, gender)
            shape_alpha_file = './assets/member_%s_%s_shape_alpha.png' % (column, gender)
        else:
            col = df[column]
            shape_file = './assets/member_info_shape.png'
            shape_alpha_file = './assets/member_info_shape_alpha.png'
            # shape_file = './assets/member_%s_%s_shape.png' % (column, gender)
            # shape_alpha_file = './assets/member_%s_%s_shape_alpha.png' % (column, gender)

        word_count = ""
        for c in col:
            if c is not np.NaN:
                seg_list = jieba.cut(c, cut_all=False, HMM=True)
                for word in seg_list:
                    word_count = word_count + word + " "
                word_count = self.convert_it_term(c, word_count)

        mask = np.array(Image.open(shape_file))
        font = r'./assets/heiti.ttf'
        # image_colors = ImageColorGenerator(mask)

        word_cloud = WordCloud(
            margin=0,
            mask=mask,
            font_path=font,
            scale=1,
            # max_words=200,
            # min_font_size=4,
            # max_font_size=150,
            stopwords=stopwords,
            random_state=42,
            background_color='white'
        ).generate(word_count)

        path_image = os.path.join(self.path_analyse,
                                  '%s_member_word_cloud_%s_%s.png' % (self.group_id, column, gender))

        if gender == 'male':
            word_cloud.recolor(color_func=self.color_func_blue, random_state=3)
        elif gender == 'female':
            word_cloud.recolor(color_func=self.color_func_red, random_state=3)

        word_cloud.to_file(path_image)

        # overlap shape alpha image
        background = Image.open(path_image)
        foreground = Image.open(shape_alpha_file)
        background.paste(foreground, (0, 0), foreground)
        # background.show()
        background.save(path_image)

        # path_pilot = os.path.join(self.path_analyse,
        #                           '%s_member_word_cloud_pilot_%s_%s.png' % (self.group_id, column, gender))
        # plt.figure(figsize=(16, 9))
        # # store default colored image
        # default_colors = word_cloud.to_array()
        #
        # if gender == 'male':
        #     plt.figure()
        #     plt.title(label_column)
        #     plt.imshow(word_cloud.recolor(color_func=self.color_func_blue, random_state=3), interpolation="bilinear")
        #     # word_cloud.to_file(path_image)
        #     plt.axis("off")
        # elif gender == 'female':
        #     plt.figure()
        #     plt.title(label_column)
        #     plt.imshow(word_cloud.recolor(color_func=self.color_func_red, random_state=3), interpolation="bilinear")
        #     # word_cloud.to_file(path_image)
        #     plt.axis("off")
        # else:
        #     plt.figure()
        #     plt.title(label_column)
        #     plt.imshow(default_colors, interpolation="bilinear")
        #     word_cloud.to_file(path_image)
        #     plt.axis("off")
        #
        # plt.savefig(path_pilot, format='png', dpi=300)
        # plt.close()

        return path_image

    '''
    wordcloud for branches & languages information of members' nickname
    :param csv_file: csv file dir
    :param column: column name: branch, language
    :param occupation: employee:employee, student:student
    '''
    def gen_wordcloud_info_occupation_nicknames(self, csv_file, column='language', occupation='employee'):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')

        if column == 'branch':
            stopwords = set(STOPWORDS)
            stopwords.update(self.load_stopwords())
            stopwords.update(self.load_stopwords_it('branch'))
        elif column == 'language':
            stopwords = set()
            stopwords.update(self.load_stopwords())
            stopwords.update(self.load_stopwords_it('language'))

        jieba.load_userdict("./assets/jieba_userdict.txt")

        df['is_student'] = df['branch'].apply(self.is_student)
        if occupation == 'employee':
            df_male = df[df.is_student == False]
            col = df_male[column]
            shape_file = './assets/member_%s_%s_shape.png' % (column, occupation)
            shape_alpha_file = './assets/member_%s_%s_shape_alpha.png' % (column, occupation)
        else:
            df_male = df[df.is_student == True]
            col = df_male[column]
            shape_file = './assets/member_%s_%s_shape.png' % (column, occupation)
            shape_alpha_file = './assets/member_%s_%s_shape_alpha.png' % (column, occupation)

        word_count = ""
        for c in col:
            if c is not np.NaN:
                seg_list = jieba.cut(c, cut_all=False, HMM=True)
                for word in seg_list:
                    word_count = word_count + word + " "
                word_count = self.convert_it_term(c, word_count)

        mask = np.array(Image.open(shape_file))
        font = r'./assets/heiti.ttf'
        # image_colors = ImageColorGenerator(mask)

        word_cloud = WordCloud(
            margin=0,
            mask=mask,
            font_path=font,
            scale=1,
            # max_words=200,
            # min_font_size=4,
            # max_font_size=150,
            stopwords=stopwords,
            random_state=42,
            background_color='white'
        ).generate(word_count)

        path_image = os.path.join(self.path_analyse,
                                  '%s_member_word_cloud_%s_%s.png' % (self.group_id, column, occupation))

        if occupation == 'employee':
            word_cloud.recolor(color_func=self.color_func_PuBu_9, random_state=3)
        else:
            word_cloud.recolor(color_func=self.color_func_YlGn_9, random_state=3)

        word_cloud.to_file(path_image)

        # overlap shape alpha image
        background = Image.open(path_image)
        foreground = Image.open(shape_alpha_file)
        background.paste(foreground, (0, 0), foreground)
        background.save(path_image)

        return path_image

    '''
    pie chart for gender of members
    :param csv_file: csv file dir
    '''
    def gen_pie_member_gender(self, csv_file):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')

        genders = df['gender']
        col = [0, 0, 0]
        for g in genders:
            if g == 1:
                col[0] = col[0] + 1
            elif g == 2:
                col[1] = col[1] + 1
            else:
                col[2] = col[2] + 1

        perccent_male = '{0:.2f}%'.format((col[0]/len(genders) * 100))
        perccent_female = '{0:.2f}%'.format((col[1]/len(genders) * 100))
        perccent_unknown = '{0:.2f}%'.format((col[2]/len(genders) * 100))

        labels = [r'Male %s' % perccent_male,
                  r'Female %s' % perccent_female,
                  r'Unknown %s' % perccent_unknown]
        colors = ['lightskyblue', 'pink', 'gold']

        plt.figure(figsize=(8, 6))
        patches, texts = plt.pie(col, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.title('Gender of Member')
        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
        plt.tight_layout()

        path_image = os.path.join(self.path_analyse,
                                  '%s_member_gender_pie.png' % self.group_id)

        plt.savefig(path_image, format='png', dpi=100)
        plt.close()
        return path_image

    @staticmethod
    def is_student(info):
        return info is not np.NaN and \
               (info.find('学生') >= 0
                or info.find('研究生') >= 0
                or info.find('实习') >= 0
                or info.find('博士') >= 0
                or info.find('待业') >= 0
                or info.find('求职') >= 0
                or info.find('毕业') >= 0
                or info.find('找工作') >= 0)

    def gen_pie_member_occupation(self, csv_file):
        df = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')

        branches = df['branch']
        col = [0, 0]
        for b in branches:
            if self.is_student(b):
                col[0] = col[0] + 1
            else:
                col[1] = col[1] + 1

        perccent_student = '{0:.2f}%'.format((col[0] / len(branches) * 100))
        perccent_emploee = '{0:.2f}%'.format((col[1] / len(branches) * 100))

        labels = [r'Unemployee %s' % perccent_student,
                  r'Emploee %s' % perccent_emploee]
        colors = ['forestgreen', 'royalblue']

        plt.figure(figsize=(8, 6))
        patches, texts = plt.pie(col, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.title('Occupation of Member')
        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
        plt.tight_layout()

        path_image = os.path.join(self.path_analyse,
                                  '%s_member_occupation_pie.png' % self.group_id)

        plt.savefig(path_image, format='png', dpi=100)
        plt.close()

        return path_image

    def send_image(self, path):
        try:
            if not self.debug:
                self.bot.file_helper.send_image(path)
                self.bot_group.send_image(path)
            else:
                self.bot.file_helper.send_image(path)
        except BaseException:
            pass

    def send_file(self, path):
        try:
            if not self.debug:
                self.bot.file_helper.send_file(path)
                self.bot_group.send_file(path)
            else:
                self.bot.file_helper.send_file(path)
        except BaseException:
            pass

    def gen_pdf_group_analysis(self, lang,
                               img_chat_history,
                               img_chat_freq_day,
                               img_chat_count_day,
                               img_chat_msg_type,
                               img_chat_heating_act,
                               img_member_gender_pie,
                               img_member_occupation_pie,
                               img_member_branches_all,
                               img_member_branches_male,
                               img_member_branches_female,
                               img_member_language_all,
                               img_member_language_male,
                               img_member_language_female,
                               img_member_language_employee,
                               img_member_language_student
                               ):
        with open('./assets/chat_analysis_%s.html' % lang, 'r') as file:
            file_data = file.read()

        # Replace the target string
        if not self.debug:
            file_data = file_data.replace('{{group_name}}', self.group_name)
        file_data = file_data.replace('{{date_begin}}', self.fl_days[0])
        file_data = file_data.replace('{{date_end}}', self.fl_days[1])

        file_data = file_data.replace('{{img_chat_history}}', Path(img_chat_history).name)
        file_data = file_data.replace('{{img_chat_freq_day}}', Path(img_chat_freq_day).name)
        file_data = file_data.replace('{{img_chat_count_day}}', Path(img_chat_count_day).name)
        file_data = file_data.replace('{{img_chat_msg_type}}', Path(img_chat_msg_type).name)
        file_data = file_data.replace('{{img_chat_heating_act}}', Path(img_chat_heating_act).name)

        file_data = file_data.replace('{{img_member_gender_pie}}', Path(img_member_gender_pie).name)
        file_data = file_data.replace('{{img_member_occupation_pie}}', Path(img_member_occupation_pie).name)
        file_data = file_data.replace('{{img_member_branches_all}}', Path(img_member_branches_all).name)
        file_data = file_data.replace('{{img_member_branches_male}}', Path(img_member_branches_male).name)
        file_data = file_data.replace('{{img_member_branches_female}}', Path(img_member_branches_female).name)
        file_data = file_data.replace('{{img_member_language_all}}', Path(img_member_language_all).name)
        file_data = file_data.replace('{{img_member_language_male}}', Path(img_member_language_male).name)
        file_data = file_data.replace('{{img_member_language_female}}', Path(img_member_language_female).name)

        file_data = file_data.replace('{{img_member_language_employee}}', Path(img_member_language_employee).name)
        file_data = file_data.replace('{{img_member_language_student}}', Path(img_member_language_student).name)

        path_html = os.path.join(self.path_analyse,
                                 '%s_group_analysis_%s_%s_%s.html'
                                 % (self.group_id, self.fl_days[0], self.fl_days[1], lang))
        path_pdf = os.path.join(self.path_analyse,
                                '%s_group_analysis_%s_%s_%s.pdf'
                                % (self.group_id, self.fl_days[0], self.fl_days[1], lang))

        # Write the file out again
        with open(path_html, 'w') as file:
            file.write(file_data)

        pdfkit.from_file(path_html, path_pdf)

        return path_pdf

    def start_analysis_tasks(self):
        if not self.debug:
            chat_csv_file_path = self.save_chat_in_current_month(self.group_id)
            member_detail_csv_file_path = self.save_member_detail_list()
        else:
            chat_csv_file_path = get_path_custom('analyse') + '/1_chat_2019-05-01_2019-06-30.csv'
            member_detail_csv_file_path = get_path_custom('group_member') + '/%s_member_detail_full.csv' % self.group_id

        # analysis for chat history
        img_chat_history = self.gen_wordcloud_chat_history(chat_csv_file_path)
        img_chat_freq_day = self.gen_bar_plot_chat_freq_day(chat_csv_file_path)
        img_chat_count_day = self.gen_spot_plot_chat_count_day(chat_csv_file_path)
        img_chat_msg_type = self.gen_bar_plot_msg_type(chat_csv_file_path)
        img_chat_heating_act = self.gen_heatmap_member_activity(chat_csv_file_path)

        # analysis for member profile
        img_member_branches_all = self.gen_wordcloud_info_nicknames(member_detail_csv_file_path, 'branch')
        img_member_branches_male = self.gen_wordcloud_info_nicknames(member_detail_csv_file_path, 'branch', 'male')
        img_member_branches_female = self.gen_wordcloud_info_nicknames(member_detail_csv_file_path, 'branch', 'female')
        img_member_language_all = self.gen_wordcloud_info_nicknames(member_detail_csv_file_path, 'language')
        img_member_language_male = self.gen_wordcloud_info_nicknames(member_detail_csv_file_path, 'language', 'male')
        img_member_language_female = self.gen_wordcloud_info_nicknames(member_detail_csv_file_path, 'language', 'female')
        img_member_language_employee = self.gen_wordcloud_info_occupation_nicknames(
            member_detail_csv_file_path, 'language', 'employee')
        img_member_language_student = self.gen_wordcloud_info_occupation_nicknames(
            member_detail_csv_file_path, 'language', 'student')

        img_member_gender_pie = self.gen_pie_member_gender(member_detail_csv_file_path)
        img_member_occupation_pie = self.gen_pie_member_occupation(member_detail_csv_file_path)

        params = {'img_chat_history': img_chat_history,
                  'img_chat_freq_day': img_chat_freq_day,
                  'img_chat_count_day': img_chat_count_day,
                  'img_chat_msg_type': img_chat_msg_type,
                  'img_chat_heating_act': img_chat_heating_act,
                  'img_member_gender_pie': img_member_gender_pie,
                  'img_member_occupation_pie': img_member_occupation_pie,
                  'img_member_branches_all': img_member_branches_all,
                  'img_member_branches_male': img_member_branches_male,
                  'img_member_branches_female': img_member_branches_female,
                  'img_member_language_all': img_member_language_all,
                  'img_member_language_male': img_member_language_male,
                  'img_member_language_female': img_member_language_female,
                  'img_member_language_employee': img_member_language_employee,
                  'img_member_language_student': img_member_language_student
                  }
        # path_pdf_en = self.gen_pdf_chat_analysis('en', **params)
        path_pdf_cn = self.gen_pdf_group_analysis('cn', **params)

        self.send_file(path_pdf_cn)
        if not self.debug:
            self.bot.file_helper.send('Analysis task finished')
        else:
            print('Analysis task finished')


# from ibot_db import *
# bot_db = BotDatabase.instance(db_config)
# ba = BotAnalyze(bot_db, '', '')
# ba.start_analysis_tasks()
