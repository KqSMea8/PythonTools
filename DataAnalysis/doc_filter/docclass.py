#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Xuecheng Yu'
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2017-02-13 14:11:40

# from pysqlite2 import dbapi2 as sqlite
from  MySQLdb import connect
import sys
import os
import re
import math
import jieba
from jieba import analyse
import glob
import excel_to_json
import xlrd
import utility
import traceback

chinese = re.compile(u'[\u4e00-\u9fa5]+')


def getwords(doc):
    splitter = re.compile('\\W*')
    print doc
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]

    # Return the unique set of words only
    return dict([(w, 1) for w in words])


def getchinesewords(doc):
    #words = jieba.cut(doc)
    words = analyse.extract_tags(doc, topK=20, withWeight=False)
    return dict([(w, 1) for w in words])


class Classifier:
    def __init__(self, getfeatures, filename=None):
        # Counts of feature/category combinations
        self.fc = {}
        # Counts of documents in each category
        self.cc = {}
        self.getfeatures = getfeatures

    def connect_db(self):
        self.con = connect(host="127.0.0.1", user="root", passwd="Mypassword@2qq", port=3306, charset="utf8",
                           db="docfilter")
        self.con.cursor().execute(
            "CREATE TABLE IF NOT EXISTS fc (feature VARCHAR(512) NOT NULL, category VARCHAR(512) NOT NULL, count int(10) DEFAULT 0, PRIMARY KEY (feature, category)) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
        self.con.cursor().execute(
            "CREATE TABLE IF NOT EXISTS cc (category VARCHAR(512) NOT NULL, count int(10) DEFAULT 0, PRIMARY KEY (category)) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
        # self.con=sqlite.connect(dbfile)
        # self.con.cursor().execute('create table if not exists fc(feature,category,count)')
        # self.con.cursor().execute('create table if not exists cc(category,count)')

    def incf(self, f, cat):
        count = self.fcount(f, cat)
        if count == 0:
            self.con.cursor().execute("insert into fc values ('%s','%s',1)"
                                      % (f, cat))
        else:
            self.con.cursor().execute(
                "update fc set count=%d where feature='%s' and category='%s'"
                % (count + 1, f, cat))

    def fcount(self, f, cat):
        cur = self.con.cursor()
        cur.execute('select count from fc where feature="%s" and category="%s"' % (f, cat))
        res = cur.fetchone()
        if res is None:
            return 0
        else:
            return float(res[0])

    def incc(self, cat):
        count = self.catcount(cat)
        if count == 0:
            self.con.cursor().execute("insert into cc values ('%s',1)" % (cat))
        else:
            self.con.cursor().execute("update cc set count=%d where category='%s'"
                                      % (count + 1, cat))

    def catcount(self, cat):
        cur = self.con.cursor()
        cur.execute('select count from cc where category="%s"' % (cat))
        res = cur.fetchone()
        if res is None:
            return 0
        else:
            return float(res[0])

    def categories(self):
        cur = self.con.cursor()
        cur.execute('select category from cc')
        res = cur.fetchall()
        return [d[0] for d in res]

    def totalcount(self):
        cur = self.con.cursor()
        cur.execute('select sum(count) from cc')
        res = cur.fetchone();
        if res is None: return 0
        return res[0]

    def train(self, item, cat):
        features = self.getfeatures(item)
        # Increment the count for every feature with this category
        for f in features:
            self.incf(f, cat)

        # Increment the count for this category
        self.incc(cat)
        self.con.commit()

    def fprob(self, f, cat):
        if self.catcount(cat) == 0: return 0

        # The total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f, cat) / self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # Calculate current probability
        basicprob = prf(f, cat)

        # Count the number of times this feature has appeared in
        # all categories
        totals = sum([self.fcount(f, c) for c in self.categories()])

        # Calculate the weighted average
        bp = ((weight * ap) + (totals * basicprob)) / (weight + totals)
        return bp


class NaiveBayes(Classifier):
    def __init__(self, getfeatures):
        Classifier.__init__(self, getfeatures)
        self.thresholds = {}

    def docprob(self, item, cat):
        features = self.getfeatures(item)

        # Multiply the probabilities of all the features together
        p = 1
        for f in features: p *= self.weightedprob(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount()
        docprob = self.docprob(item, cat)
        return docprob * catprob

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}
        # Find the category with the highest probability
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # Make sure the probability exceeds threshold*next best
        for cat in probs:
            if cat == best: continue
            if probs[cat] * self.getthreshold(best) > probs[best]: return default
        return best


class FisherClassifier(Classifier):
    def cprob(self, f, cat):
        # The frequency of this feature in this category
        clf = self.fprob(f, cat)
        if clf == 0: return 0

        # The frequency of this feature in all the categories
        freqsum = sum([self.fprob(f, c) for c in self.categories()])

        # The probability is the frequency in this category divided by
        # the overall frequency
        p = clf / (freqsum)

        return p

    def fisherprob(self, item, cat):
        # Multiply all the probabilities together
        p = 1
        features = self.getfeatures(item)
        for f in features:
            p *= (self.weightedprob(f, cat, self.cprob))

        # Take the natural log and multiply by -2
        fscore = -2 * math.log(p)

        # Use the inverse chi2 function to get a probability
        return self.invchi2(fscore, len(features) * 2)

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df // 2):
            term *= m / i
            sum += term
        return min(sum, 1.0)

    def __init__(self, getfeatures):
        Classifier.__init__(self, getfeatures)
        self.minimums = {}

    def setminimum(self, cat, min):
        self.minimums[cat] = min

    def getminimum(self, cat):
        if cat not in self.minimums: return 0
        return self.minimums[cat]

    def classify(self, item, default=None):
        # Loop through looking for the best result
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherprob(item, c)
            # Make sure it exceeds its minimum
            if p > self.getminimum(c) and p > max:
                best = c
                max = p
        return best


def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')


current_path = os.path.split(os.path.realpath(__file__))[0] + '/'
TRAIN_DIR = current_path + 'trainfile/'
TEST_DIR = current_path + 'testfile/'


def chinese_train(cl):
    for file in glob.glob(TRAIN_DIR + "*.xlsx"):
        print file
        excel_file = xlrd.open_workbook(file)
        for sheet_name in excel_file._sheet_names:
            sheet = excel_file.sheet_by_name(sheet_name)
            for i in range(sheet.nrows):
                cat = None
                url = None
                content = None
                try:
                    cat = sheet.cell(colx=0, rowx=i).value
                    cat = str(cat).decode('utf-8', 'ignore')
                    cat = excel_to_json.purify_search_word(cat)
                    cat = cat.strip()
                    if not cat:
                        continue
                except IndexError:
                    continue

                try:
                    url = sheet.cell(colx=1, rowx=i).value
                    url = str(url).decode('utf-8', 'ignore')
                    url = url.strip()
                    if not url:
                        continue
                except IndexError:
                    continue

                print url
                try:
                    content = sheet.cell(colx=2, rowx=i).value
                    content = str(content).decode('utf-8', 'ignore')
                    content = excel_to_json.purify_search_word(content)
                    content = content.strip()
                    if not content:
                        continue
                except IndexError:
                    continue

                if cat is None or content is None:
                    continue
                body = content.decode('utf-8', 'ignore')
                body = body.replace('\01', ' ')
                if not chinese.search(body):
                    continue

                cl.train(body, cat)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage python docclass.py [train|test <filename>]"
        sys.exit(0)

    # cl = fisherclassifier(getchinesewords)
    cl = NaiveBayes(getchinesewords)
    cl.connect_db()
    if sys.argv[1] == "train":
        chinese_train(cl)
    else:
        if len(sys.argv) < 3:
            print "Usage python docclass.py [train|test <filename>]"
            sys.exit(0)
        print cl.classify("""皮皮小说网_色色_无弹窗小说网^A色色;无弹窗小说网;皮皮小说网^A皮皮小说网是无弹窗广告的小说网，为大家免去弹窗广告的烦劳，欢迎个位读者来阅读最新小说，这里提供最好看无弹窗小说阅读网站，蛟龙戏水承诺做永久无弹窗的小说网。^A^A皮皮小说网 首页 都市小说 玄幻小说 仙侠小说 历史小说 科幻小说 悬疑小说 其他小说 全本小说 我的书架 姻差郎错：扑倒呆萌相公 天庭小狱卒 火影鹿雪 重生洪荒之三界妖尊 攀上漂
    亮女局长之后 盛宠豪门重生锦绣年华 废材狂妻极品七小姐 反扑大神：师尊羞想逃 庄稼地里的诱惑 神棍夫人：夫君，要听话 绝宠第一毒妃 抱个总裁上直播 万世尊宠 我们的青春时代 战神伪高冷：天降医妃拐回家 邻家少妇(雁惊云) 一夜情凉：腹黑首席扑上瘾 tfboys之转角遇到王俊凯 幸得相遇离婚时 先婚后爱：总裁别太猛 hp斯内普牌小巨怪的快乐生活 万古至尊 军婚绵绵：顾少，宠妻无度 斗罗大陆3龙王传说 仙域天尊 绝世高手在都市 穿越侏罗纪传
    奇 总裁爹地:不要弄疼我妈咪 我的女友是狐仙 都市绝品妖孽 武道系统之草民崛起 倾国佳人爱上我 劣妃情殇：暴君夺爱 权倾一世 飞刀问道 最强反派系统 征战天下-雨过天晴 重生西游之万界妖尊 特种校医 轮回在三千世界 [重
    生]叔在上,不着寸缕 犬夜叉之优雅就是错 漫威太阳神 都市修真之超级空间 青蛇再起 洪荒之龙君 灵鼎 妻手遮天：全能灵师 凤凰逆天：腹黑<E5><86>是DZ程序，今天检查死链的时候发 个人博客如何才能做成功 20大seo常识 网站优化中我们需要革新的一些方法 优化用户体验是经典 ·淡定是SEOer必修的科目！ ·网站建设进入洗牌时代，“誉字号”X7致力打造有 ·一个网站的权重所表现的几个方面 ·利用问答平台推广的效果好吗？ ·百度是不是周末发福利了？ ·网站被处罚的解决办法 ·把握七点要素做好关键字排名 ·经验中总结的几点外链技巧 ·有多少人跟我情况一样 ·提高seo排名关键是什么 ·如何获取有效有质量的外链 ·网站优化系列之谈网站曝光度 ·问战ol礼包 ·世界ol大刀侠客
    装备 ·魔兽世界大刀 ·希望ol暴力祭祀 ·世界ol暴力大剑 ·世界ol战士烈焰箭 ·世界ol战士加点 ·世界ol大刀战士技能 ·世界ol暴力大刀战士 ·世界ol大刀战士加点 ·世界ol全敏侠客 ·世界ol大刀侠客加点 ·世界ol大剑侠客攻略 ·世界ol装备鉴定属性 ·世界ol战士装备 ·世界ol装备属性 ·舞侠ol官方 ·使命召唤ol活动枪 ·真三国无双ol螺旋枪 绿色网站 杂七搜 站点地图 换物网 植物之家""")
        print cl.classify("""蝴蝶谷中文娱乐网,蝴蝶谷中文网,蝴蝶谷娱乐,哥也色蝴蝶谷娱乐网站^A蝴蝶谷中文娱乐网,蝴蝶谷中文网,蝴蝶谷娱乐,哥也色蝴蝶谷娱乐网站,蝴蝶谷中文网,哥也色蝴蝶谷娱乐网,蝴蝶谷娱乐网新网站,哥要搞蝴蝶谷中文网,哥也爱蝴蝶谷娱乐网^A蝴蝶谷中文娱乐网,蝴蝶谷中文网,蝴蝶谷娱乐,哥也色蝴蝶谷娱乐网站,蝴蝶谷中文网,哥也色蝴蝶谷娱乐网,蝴蝶谷娱乐网新网站,哥要搞蝴蝶谷中文网,哥也爱蝴蝶谷娱乐网^A^A首页 亚洲无码
    亚洲有码 中文字幕 偷窥自拍 欧美视频 强暴乱伦 制服扮演 珍藏卡通 巨乳波霸 另类癖好 经典三级 色情贴图 偷拍自拍 亚洲色图 欧美色图 亚洲诱惑 欧美诱惑 另类性虐 街拍美女 卡通动漫 激情小说 生活情感 人妻女友 乱伦小说 校园情色 古典武侠 意淫强奸 交通性爱 性爱技巧 先锋电影 亚洲情色 制服师生 强奸乱伦 偷拍自拍 三级伦理 中文字幕 人妻熟女 无码专区 丝袜美腿 欧美性爱 成人动漫 变态另类 HND-354  真正中出し解禁！！  栄川乃亜 GESU-019  巨乳演奏傢復讐SEX HNJC-006  微乳A罩杯  小宮山加奈子 GETS-019  內見案內中に失禁著衣SEX EIKI-031  人妻中出  葉月美音 DANDY-518  採精室2発目の精液検査 CMI-084  極映像 39人目 DASD-359  復讐劇58日間 GDHH-031  奇跡！授業中 GS-079  同級生強制援交 DANDY-521  看護師の巨乳姉禁欲 GVG-387  鉄拘束拷問  黒木いくみ HAR-048  強制欲情全身敏感女 HND-355  本物中出！  咲坂花戀 DDK-134  學級委員長女子校生  跡美しゅり GETS-018  OL超淫亂！中出誘惑 BUZ-006  盜撮06 DXYB-025  殘虐拷問執行所 恥辱の性奴開発  長谷川夏樹 DDB-310   若槻みづな EBOD-553  本物蕓能人の奉仕風俗嬢Icup密著  八神さおり GYAZ-142  快楽度400％！発狂確定 DVAJ-188  性交記録！ HND-358  女の子學校中出！  河野アキ GDMQ-23  突然宅派遣。 ABBA-321  熟女の矯正下著 20人4時間 BABA-087   「性生活研究所」人妻！欲求不満 ANB-117  巨乳叔母  久保裡奏子 BCV-015  TV×PRESTIGE PREMIUM 15 更多>> 更多 THE 未公開 ～カメラの前でおしっこ発射～ エロし恥ずかし絶頂天国 美微乳 真鍋はるか マンコ図鑑 美月優芽 出張キャバ嬢はスキだらけ～デカパイ感じるんだろ？～ - 深美せりな 更多 11-今晚
    ，跟上司的太太兩人獨處… 中谷有希[中文字幕] 5-[MXBD-200] 未亡人奴隷 麻生希 6-[MXBD-200] 未亡人奴隷 麻生希 10-[MXBD-200] 未亡人奴隷 麻生希 小模特泳池边打炮实录 更多 ゲスの极み映像 五人目 すぐにお漏らししち
    ゃうから外でエッチしよう 瑠川リナ お母さんが初めての女になってあげる 市来美保 うまのりパンストお姉さんのいやらしい淫语骑乗位 饭冈かなこ おやじっち 中年の俺が家事代行サービスを頼んだら 更多 骚妞假装不理我
    ，其实也是一个荡妇，被干出白带了 龌龊男搞非常可爱的学生制服美眉，射了一脸白浆 表姐被我强行扒开了双腿后立刻淫态百出 国内小伙让在自己性感漂亮妻子趴在电脑桌上撅着屁股干 国语对白 浴池强逼情人给毒龙俩人对话精
    彩 更多 Summer Heat Serve It Up Squirting teen loves anal fingering Spanked And Fucked Ariel Skye 更多 3-老爸出門2秒就幹砲的母子 柳美和子[中文字幕] 8-老爸出門2秒就幹砲的母子 柳美和子[中文字幕] 9-老爸出門2秒就幹砲的母子 柳美和子[中文字幕] 3- 大嫂被幹翻天了 佐佐木明希[中文字幕] 可爱妹妹不让哥哥看成人漫画让玩她 更多 素人学生妹 下海拍AV 直接被插到尖叫 清纯可爱的学生妹 被无限挑逗 可爱妹子大胆尝试双龙戏凤 上门
    服务的援交学生妹 还在上学的女朋友 敏感身体不堪挑逗 更多 初めての家庭教師 後編 欲望学院 第2章 クール_ディバイシス_シリーズ  7 肢体を洗う THE ANIMATION CASE クール_ディバイシス_シリーズ 3 愛玩少女 更多 8-I
    罩杯爆乳女教師乳交AV志願 三島奈津子[中文字幕] 11-I罩杯爆乳女教師乳交AV志願 三島奈津子[中文字幕] 8-神巨乳小蠻腰 超威猛幹砲 5 夢乃愛華[中文字幕] 10-神巨乳小蠻腰 超威猛幹砲 5 夢乃愛華[中文字幕] 5-神巨乳小蠻
    腰 超威猛幹砲 5 夢乃愛華[中文字幕] 更多 千人大乱交-比谁肏的最猛 性感骚妹穿着齐逼小短裙去台球厅狩猎男人 当着女友的面与床下的小三偷情 女友的闺蜜与我的兄弟们-高潮不断 A Dick Before Divorce ABBA-320  AV撮影現場素人 20人4時間 BABA-088  人間 MRI精密検査 ABP-535  鈴村あいり BDSR-271  篠田あゆみ4時間 巨乳美人淫語。 BCV-013  TV×PRESTIGE PREMIUM 13 BF-492  生中出  桃瀬ゆり ABP-536  従順  若菜奈央 AFS-018   人妻6人 in西新宿青山麻佈 vol.15 AUKG-364  大興奮！場景女同 ABP-541  風俗3時間SPECIAL  今永さな AWT-072  淫語中出  二階堂ゆり BCV-014  TV×PRESTIGE PREMIUM 14 ABP-539  凰かなめの極上 10 AVNT-028  在街上泄漏的新混血 AP-366  固定媚薬 映畫館癡漢 ARM-547  あるある」 ABP-534  加藤ほのか Pacopacomama-020416_02  豐滿人妻 Nyoshin-1214 つかさ Pacopacomama-012816_020 熟女 萩原しおり Muramura-011216_337 殘業！ 西門和恵 Pacopacomama-012916_021 人妻：ようこ MKD-S123 KIRARI 123  : 篠田あゆみ Pacopacomama-052816_094 爆乳巨尻：新崎雛子 Nyoshin-n1235  つかさ ＳＥＸ MKD-S125 KIRARI 125 肉壺生徒會長 : 高山玲奈 Pacopacomama-021216_029 夫人 三木谷梨果 更多 更多>> 不入虎穴焉得双姝共九章 情色聊斋完 混沌神眼 完 最经典的骂人的话！ 我与我的二婶的一段情完（作者：不详） 第一次为男友吹箫完 疯狂的报复作者bbbb81 换妻使我疯狂换妻,使妻高潮我疯狂
    我现在知道老婆为什么喜欢坐公车了完（作者：不详） 寡妇日记完 娇妻物语完 把小护士给啪啪了完（作者：不详） 美女一边打电话一边给我草完（作者：不详） 我操了我的淫荡女经理完（作者：不详） 九寨沟艳遇完（作者：不详） 三洞轮流插的感觉 性爱最佳时期，把握4个关键时机 居然怀孕了 保险没用上等5则 上帝在造女人的时候，在女人下面放了个鲍鱼 爆笑喝酒和醉酒后的各种趣事 我與表妹那段刻骨銘心的往事 人间烟火（４） 天人 【水浒揭秘：高衙内与林娘子不为人知的故事】（又名贞芸劫）（八）（上中下） 素描画上的半张画 护花剑（修改版）第06章惊闻噩耗 更多>> 排行榜 百度地图 RSS订阅 广告联系 discuz!3.2""")
        print cl.classify("""论坛 -  Powered by Discuz!^A论坛^A论坛^A只需一步，快速开始 提供最新 Discuz! 产品新闻、软件下载与技术交流^A找回密码 立即注册 搜索 帖子 用户 设为首页 收藏本站 开启辅助访问 切换到窄版 登录 立即注册 道具 勋章 任务 设置 我的收藏 退出 Discuz! Board 论坛 Howardrog 关注微信 最新回复 Discuz! 默认版块 新注册会员【送288奖金，3倍流水 ... grbii 在线会员 fxb491g get454f 官方论坛 Comsenz 漫游平台 Yeswan 专用主机 Archiver 手机版 小黑屋 Comsenz Inc. All rights reserved. Discuz!""")
        print cl.classify("""天天射-天天射综合网^A天天射-天天射综合网^A天天射-天天射综合网^A^A天天射-天天射综合网_帮帮撸_www.bangbanglu.com 浏览器设置 加入收藏夹 电影 亚 洲 AV 欧美性爱 偷窥自拍 美腿制
    服 少妇人妻 另类重口 群交乱伦 综合影院 图片 亚洲图片 欧美色图 网友自拍 美腿丝袜 清纯唯美 熟女乱伦 同性另类 动漫卡通 下载 在线视频 日韩bt区 欧美bt区 亚洲有码 迅雷电驴 合辑下载 情色三级 网盘综合 小说 激情文学 人妻意淫 乱伦迷情 古典武侠 另类综合""")
        print cl.classify("""首页 - 景洪市审计局公开指南 机构职能 公告公示 工作动态 政务公开 公开目录 学习培训 政策解读和新闻发布 我们一起看变化 规划和总结 领导简历 财政预决算及“三公”经费 党的群众路线教育实践活动 精神文明建设 公文 规章、规范性文件 政策法规 其他文件 办事服务 下载中心 >> 更多 景洪市民政局2015年... 景洪市2015年国家农... 景洪市勐养镇为民服... 景洪市2016年小型农... 景洪市农产品质量安... 景洪市2013年巩固退... 西双版纳小冬瓜牧业... 2016年3月景洪市财... >> 更多 2016年年景洪市审计... 2016年景洪市审计局... 2016年景洪市审计局... >> 更多 景洪市审计局机构职... 景 洪 市 审 计 局 ... 什么是金审工程？ 什么是“小金库”，... 什么是领导干部的直... 审计人员是否可以直... >> 更多 更多>> 景洪市多措施高位推进2016年领导干部经济责... 景洪市审计局贯彻落实全省审计机关党建暨党... 市审计局学习贯彻全市党建工作会议精神 景洪市审计局专题谋划“七五”普法规划 景洪市审计局召开党员组织生活会民主评议党... 景洪市审计局召开2016年度领导班子民主生活... 市人大常委会热议审计查出问题整改情况 景洪市审计局启动景洪大桥至景兰大桥市政基... 市审计局学习殡葬政策倡导文明殡葬 景洪市人民医院HIS信息系统审计完美收官 >> 更多 审计署关于适应新常态践行新理念... 审计署关于印发“十三五”国家审... 全国人大常务委员会工作报告（摘... 中国共产党巡视工作条例(全文) 全国人民代表大会常务委员会关于... 中华人民共和国行政诉讼法（2014... 中华人民共和国国家审计准则（审... 《审计机关封存资料资产规定》（... >> 更多 投资效益审计的指标是什么 财政支农资金效益审计 认真细致开展工作 景洪市审计局会议及学习生活 >> 更多 景洪市审计局审计文明用语 >> 更多 2015年景洪市审计局工作总结和20... 景洪市审计局十二五工作总结及十... 关于景洪市审计局2015年部门预算... 2011年景洪市审计局政府信息公开... 景洪市审计局2009年度民主评议政... 系统管理维护""")

        filename = sys.argv[2]
        full_filename = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + filename
        with open(full_filename, "r") as data_file:
            for line in data_file:
                try:
                    line = line.strip()
                    if line is None or len(line) == 0 or line.find('\t') == -1:
                        continue
                    url, body = line.split("\t", 1)
                    body = body.decode('utf-8', 'ignore')
                    body = body.replace('\01', ' ')
                    if not chinese.search(body):
                        continue
                    cat = cl.classify(body)
                    print u"\t".join([cat, url])
                except UnicodeDecodeError:
                    traceback.print_exc()
                    pass

