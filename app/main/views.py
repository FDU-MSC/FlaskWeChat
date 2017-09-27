from flask import request
from ..models import Talk, User
from . import main
from .. import db
from .bot import answer
from .receive import parse_xml
from .reply import TextMsg
from ..email import send_email


@main.route('/wx', methods=['POST'])
def index():
    webData = request.get_data()
    recMsg = parse_xml(webData)
    toUser = recMsg.FromUserName
    fromUser = recMsg.ToUserName
    try:
        print("This is context", recMsg.Content, "\n")
    except:
        print()
    with open("data.txt", "a", encoding='utf-8') as fin:
        print("", file=fin)
        print(toUser, file=fin)
        print(recMsg.Content, file=fin)
    # 快速查询
    content = ""
    if recMsg.Content == "TellMeAll":
        user1 = User.query.filter_by(state=7).all()
        user2 = User.query.filter_by(state=8).all()
        content = [each.name for each in user1]
        for each in user2:
            content.append(each.name)
        content.append(len(content))
        replyMsg = TextMsg(toUser, fromUser, content)
        return replyMsg.send()
    if recMsg.Content == "help":
        content = """-输入"我是XXX"告诉我您的姓名\n-输入"报名"进入报名流程\n-输入"活动"查看新学年活动\n除此之外，公众号还可以回答一些简单的关于俱乐部的问题\n\n如果您在报名流程中，\n-输入q退出报名"""
        replyMsg = TextMsg(toUser, fromUser, content)
        return replyMsg.send()
    # 用户对话
    user = User.query.filter_by(wcid=toUser).first()
    talk1 = Talk(come=True, wcid=toUser, context=recMsg.Content)

    if user is None:
        # 第一次对话
        user = User(wcid=toUser)
        if talk1.context == "报名":
            user.state = 12
            content = """您好~这是我们的第一次对话，请您先输入"我是XXX"告诉我您的姓名后再进行报名"""
        else:
            content = """您好~这是我们的第一次对话，您可以输入"我是XXX"告诉我您的姓名，或者输入help查看公众号的功能"""
    elif talk1.context == "q":
        if user.state < 7:
            user.state = 2 if user.state > 2 else 1
            content = "您已退出报名流程"
        else:
            content = "您已报名成功，无需退出"
    elif user.state == 12:
        if talk1.context[0:2] == "我叫" or talk1.context[0:2] == "我是":
            user.name = recMsg.Content[2:]
            user.state = 3
            content = """您好/::*%s\n您已进入报名流程,请告诉我您的学号\n\n(您随时可以输入q退出)""" % (
                user.name)
        else:
            content = answer(talk1.context)
            user.state = 1
    elif user.state > 2 and user.state < 8:
        if user.state == 3:
            if len(talk1.context) != 11:
                content = "您的学号输入貌似有误，请重新输入"
            else:
                user.sid = talk1.context
                user.state = 4
                content = "%s,您好！报名微软学生俱乐部需要回答三个问题\n\n1.您觉得以下哪些选项可以描述你?（多选）\n\nA. 技术萌新\nB. 讲座爱好者\nC. 软件设计能手\nD. ACMer or OIer\nE. 实验室大佬\nF. 实习搜寻者\n\n您可以回答上面字母的组合，或者在字母后添加你对自己的描述" % user.name
        elif user.state == 4:
            user.ans1 = talk1.context
            user.state = 5
            content = "2.简单地考一下你的知识面，以下哪些产品或技术是微软研发的呢?（多选）\n\nA. PyCharm\nB. Visual Studio\nC. Cortana语音助手\nD. 小冰聊天机器人\nE. Azure云服务\nF. 游戏：魔兽世界\nG. 游戏：帝国时代\nH. Open Mind Studio\n\n您可以回答上面字母的组合"
        elif user.state == 5:
            user.ans2 = talk1.context
            user.state = 6
            content = "3.最后一个问题有些难？请问您了解以下哪些技术呢?（多选）\n\nA. 会写AVL树\nB. 会用Photoshop\nC. 了解SVM和K-means\nD. 熟悉软件开发流程 \nE. 了解网站运营\nF. 会用LateX\n\n您可以回答上面字母的组合，或者说说你擅长的技术~"
        elif user.state == 6:
            user.ans3 = talk1.context
            user.state = 7
            content = "%s,恭喜您报名成功~请注意查收你的学邮~\n如果学邮没有收到我们的群二维码，您可以尝试在浏览器打开此链接查看二维码\nhttp://115.159.59.44/static/ScanMe.jpg\n\n有其他想和我们说的话，请继续留言~（我们会在留言的人中抽奖的哟！）" % user.name
            send_email(user.sid+"@fudan.edu.cn", '欢迎加入微软学生俱乐部',
                       '/confirm', user=user.name)
        elif user.state == 7:
            user.ans4 = talk1.context
            user.state = 8
            content = "谢谢，我们已收到您的消息~\n如果学邮没有收到我们的群二维码，您可以尝试点击此链接查看二维码http://115.159.59.44/static/ScanMe.png"
    elif talk1.context == "报名":
        if user.state == 1:
            content = """您好~我还不知道您的姓名，请您先输入"我是XXX"告诉我您的姓名后再进行报名"""
        elif user.state == 7:
            content = """%s，您好！您已成功报名，不用重复操作"""
        else:
            content = "%s，您已进入报名流程,请告诉我您的学号\n\n(您随时可以输入q退出)~" % user.name
            user.state = 3
    elif talk1.context[0:2] == "我叫" or talk1.context[0:2] == "我是":
        # 确认姓名
        user.name = recMsg.Content[2:]
        user.state = 2
        content = """您好/::*%s\n您可以问我关于俱乐部的问题~\n或者输入"报名"进入报名流程~\n或者输入help查看公众号功能\n（如果想修改您的姓名，您可以再次告诉我您的名字）""" % (
            user.name)
    elif user.state == 1:
        content = answer(recMsg.Content)
    else:
        content = """%s,您好！\n%s""" % (user.name, answer(recMsg.Content))
    talk2 = Talk(come=False, wcid=toUser, context=content)
    db.session.add(user)
    db.session.add(talk1)
    db.session.add(talk2)
    db.session.commit()
    replyMsg = TextMsg(toUser, fromUser, content)
    return replyMsg.send()
