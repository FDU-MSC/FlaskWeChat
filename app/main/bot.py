import jieba
import re
from .. import db
from ..models import User

# 问题库
QandA = {
    "你好": "你好呀/::*/:heart",
    "俱乐部": "微软学生俱乐部是微软亚洲研究院与高校合作培养人才的一种探索，是联系微软与高校的桥梁",
    "复旦大学": "复旦大学（Fudan University），简称“复旦”，位于中国上海,是一所综合性研究型的全国重点大学。",
    "微软公司": "微软，是一家美国跨国科技公司，也是世界PC（Personal Computer，个人计算机）软件开发的先导",
    "微软亚洲研究院": "微软亚洲研究院(MSRA)为微软公司在美国本土以外最大的基础研究机构,目前主要从事的研究领域包括:自然用户界面、新一代多媒体、以数字为中心的计算和互联网搜索等",
    "微软学生俱乐部": "微软学生技术俱乐部是微软亚洲研究院与高校合作培养人才的一种探索，是联系微软与高校的桥梁",
    "复旦大学校长": "复旦大学的校长是许宁生",
    "如何报名俱乐部": "输入'报名'进入报名流程",
    "俱乐部日常活动": "在9月我们有俱乐部大会；10月有五校联合举办的骇客马拉松比赛；更多活动，尽请期待！",
    "俱乐部主席": "俱乐部的主席是15CS的郑逸宁",
    "俱乐部副主席": "俱乐部的副主席是16CS的王佳羽，15大数据的张曾光",
    "俱乐部多少人": "2016-2017年度有31名同学，2017-2018招新活动已经开始~",
    "复旦大学成立": "复旦大学建校于1905年",
    "复旦大学校区": "复旦大学共有4个校区，分别是邯郸校区、张江校区、枫林校区和江湾校区",
    "复旦大学标志": "复旦大学的标志是其最高建筑光华楼",
    "俱乐部成立时间": "微软学生俱乐部成立于2007年",
    "复旦大学食堂": "复旦有旦苑食堂，北区食堂，南区食堂，春晖食堂，南小食堂，张江食堂，枫林食堂和江湾食堂，总计8个食堂，开放时间等具体信息详见http://www.xyfw.fudan.edu.cn/",
    "复旦大学校车": "复旦校车时刻表详见 http://www.xyfw.fudan.edu.cn/",
    "复旦大学澡堂": "复旦澡堂位置及开发时间详见 http://www.xyfw.fudan.edu.cn/",
    "俱乐部例会": "复旦大学微软学生俱乐部暂时没有例会，但会对应Penta-Hackathon,编程之美等活动，进行讨论和培训",
    "俱乐部常规活动": "复旦大学微软学生俱乐部暂时没有常规活动，但会对应Penta-Hackathon,编程之美等活动，进行讨论和培训",
    "复旦大学计算机学院": "，于2008年5月27日正式挂牌成立。下设计算机科学与技术，信息安全，保密管理等专业。学院官网 \n www.cs.fudan.edu.cn/",
    "复旦大学软件学院": "复旦大学软件学院成复旦大学计算机科学技术学院在整合复旦大学计算机学科现有各方力量基础上立于2002年，是国家教育部与国家发展计划委员会联合批准成立的全国首批35所国家示范性软件学院之一。学院官网 \nhttp://www.software.fudan.edu.cn/",
    "俱乐部定位": "复旦大学微软学生俱乐部是一个非盈利的技术组织，把爱好科技的同学们聚在一起，通过传播先进技术，培养大家对技术的热爱与研究，并利用各种方式促进技术的推广、实践与转化。微软学生俱乐部的宗旨是“学习先进技术，开拓创新思维，体验多元文化，培养一流人才”。",
    "俱乐部核心成员": "俱乐部核心成员有主席和两名副主席，以及特定活动的负责人，积极参与俱乐部的活动可以成为活动负责人，竞聘下一届主席和副主席",
    "俱乐部招新": "请输入\"报名\"进行报名~",
    "俱乐部男女比例": "男女比例约为一比一呦~",
    "活动": """新学年已经确定的活动有:\n-9月针对新生的IDE使用讲座\n-10月的由华东五校举办的PentaHackthona\n-18年4月或5月的编程之美比赛及微软AI讲座\n-18年暑假的微软夏令营\n\n"""
    + """新学年正在筹划的活动有:\n-和ACM队合办的编程比赛\n-参观苏州微软新园区\n\n可输入具体活动的名称查看活动内容哟~"""
}
# 不会回答的回答
notGood = ["我们的公众号比较迟钝，暂时还不会回答这个问题/:P-(您可以输入help查看公众号功能"]
# 相似度矩阵
mapQ = {
    "复旦大学,复旦": 1, "老大,主席": 0.9, "老大,校长": 0.9, "老二,副主席": 0.9,
    "餐厅,食堂": 1, "澡堂,浴室": 1, "澡堂,淋浴间": 1, "常规活动,例会": 0.8,
    "简介,简单介绍": 1, "主席,郑逸宁": 0.7, "副主席,王佳羽": 0.7,
    "你好,Hello": 1, "你好,hello": 1, "你好,hi": 1, "你好,Hi": 1,
}
# 单词相似度


def words(wordA, wordB):
    key = wordA+","+wordB
    if key in mapQ:
        return mapQ[key]
    key = wordB + "," + wordA
    if key in mapQ:
        return mapQ[key]
    return 1 if wordA == wordB else 0
#


def outof(text):
    return re.sub("[\s+\.\!\/_,$?,.%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "", text)
# 问题相似度


def similar(quesA, quesB):
    quesA = outof(quesA)
    quesB = outof(quesB)
    listA = [each for each in jieba.cut_for_search(quesA)]
    listB = [each for each in jieba.cut_for_search(quesB)]
    cnt = len(listA)
    num = sum(len(each)for each in listA)
    goal = 0
    goalnum = 0
    for each in listA:
        maxT = max(words(each, ii)for ii in listB)
        goal += maxT
        goalnum += maxT * len(each)
    goal /= cnt
    goalnum /= num
    return goal, goalnum
# 处理问题的方法


def answer(context):
    #print("\n\n\n\n",context,"\n\n\n\n")
    maxGoal = 0
    maxAns = 0
    for each in QandA.keys():
        A = similar(context, each)
        B = similar(each, context)
        goal = max(A[1]*0.4+B[1]*0.6, A[1]*0.8+B[1]*0.2)
        if maxGoal < goal:
            maxGoal = goal
            maxAns = QandA[each]
    if maxGoal < 0.2:
        return notGood[0]
    if maxGoal < 0.6:
        return notGood[0]
    return maxAns


if __name__ == "__main__":
    print(answer("复旦大学有几个校区"))
