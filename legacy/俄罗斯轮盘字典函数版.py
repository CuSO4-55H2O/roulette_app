import random
import json
import time
from 输出 import send_msg
from 读取文件 import cal

def ini_wheel():
    dic = {'turn': 0, 'stage': 0, 'over': 0,'group1':0,
           'mode': [], 'clip': [], 'players': [], 
           'nick': [], 'score': [0,0], 'loser': 0,
            'hp': [0,0], 'ment': {'knife':0,'chain':0,'handcuffs':0,'ban':0},
           'item': [{
               '刀': 0, '烟': 0, '放大镜': 0, '灌铅骰子': 0, '炸药': 0, '手铐': 0, 
               '铁索连环': 0, '洛欧塞布': 0, '死亡证明': 0,'午时已到':0,'baba':0
                     }, {
                         '刀': 0, '烟': 0, '放大镜': 0, '灌铅骰子': 0, '炸药': 0, '手铐': 0, 
                         '铁索连环': 0, '洛欧塞布': 0, '死亡证明': 0,'午时已到':0,'baba':0
                         }]
           ,'point':[0,0],'tar':8,'time':0,'turns':1,'cur_turns':1,'reset':0,'skip':[0,0]
           ,'artifact':[{'沃金的手':0,'莽':0,'整理好的茶具':0},{'沃金的手':0,'莽':0,'整理好的茶具':0}]}
    return dic

def add(turn,item,nick):
    t=''
    j = item[turn]
    k = 0
    for i in j:
        k += j[i]
    if k != 0:
        t+= f'{nick[turn]}现在拥有以下道具'
        for i in j:
            if j[i] != 0:
                t+= '，' + i + '*' + str(j[i])
    return t
def damage(hp,score,nick,loser,stage):
    i=-1
    text=''
    over=0
    loser=loser
    if hp[0]<=0:
        text+=f'\n{nick[0]}死亡。'
        i=0
    if hp[1]<=0:
        text+=f'\n{nick[1]}死亡。'
        i=1
    if hp[0] <= 0 and hp[1] <= 0:
        text+='\n双方同时死亡，本轮重赛。'
        over=1
    elif i != -1:
        loser=i
        stage+=1
        over=1
        score[1-i] += 1
    return over,loser,score,text,stage

def mode12(dic):
    tar=dic['tar']
    nick = dic['nick']
    group = dic['group1']
    turn = dic['turn']
    mode = dic['mode']
    hp = dic['hp']
    ment = dic['ment']
    nick = dic['nick']
    clip = dic['clip']
    stage=dic['stage']
    flag=clip.pop(0) == 1
    i = {True: '实弹', False: '空弹'}
    if flag:
        dmg = 1
    else:
        dmg = 0
    text=f'{nick[turn]}向靶子射击。是{i[flag]}。'
    if ment['knife']==1:
        if flag:
            dmg+=1
            text += '受到【刀】的影响，伤害+1。'
        else:
            text+='【刀】已失效。'
        ment['knife']=0
    if 5 in mode and flag and 1<=random.randint(1,100)<=15:
        dmg=dmg*2
        text+='受到【命运之轮】的影响，伤害翻倍。'
    text+=f'实际对靶子造成了{dmg}点伤害。'
    if ment['handcuffs']==1:
        ment['handcuffs']=0
        text+='手铐已失效。'
    tar-=dmg
    if flag:
        if stage==4 and hp[turn]<=3:
            text+='已经无法恢复生命值。'
        else:
            hp[turn]+=1
            text+=f'{nick[turn]}恢复了一点生命值。'
    text += f'\n当前剩余生命值：{nick[0]}：{hp[0]}，{nick[1]}：{hp[1]}，靶子：{tar}'
    i = sum(clip)
    if i != 0:
        text += f'\n弹夹剩余{i}颗实弹，{len(clip) - i}颗空弹。'
    send_msg({'msg_type': 'group', 'number': group, 'msg': text})
    turn = 1 - turn
    b=0
    if tar<=0:
        b=1
    return hp,tar,turn,ment,b,clip

def mode11(dic):
    nick = dic['nick']
    stage=dic['stage']
    group=dic['group1']
    item = dic['item']
    turn = dic['turn']
    mode = dic['mode']
    hp = dic['hp']
    loser = dic['loser']
    ment = dic['ment']
    nick = dic['nick']
    score = dic['score']
    text=f'{nick[turn]}使用【苦肉】，受到了一点伤害。'
    hp[turn]-=1
    distribute(turn, mode, item)
    t = add(turn, item, nick)
    text += t+'。'
    if ment['chain'] == 1:
        ment['chain'] = 0
        hp[1-turn] -= 1
        text += f'受到【铁索连环】的影响，{nick[1-turn]}也受到了伤害。'
    over, loser, score, t ,stage= damage(hp, score, nick, loser,stage)
    text += t
    send_msg({'msg_type': 'group', 'number': group, 'msg': text})

    return hp,over, loser,score,ment,stage

def settle(win,dic,name):
    tar=dic['tar']
    group=dic['group1']
    item = dic['item']
    stage = dic['stage']
    mode = dic['mode']
    players = dic['players']
    loser = dic['loser']
    nick = dic['nick']
    score = dic['score']
    point=dic['point']
    start=dic['time']
    turns=dic['turns']
    artifact=dic['artifact'][win]
    end=time.time()
    dur=round(end-start)
    min=dur//60
    sec=dur%60
    text_time=f'总时长：{min}分{sec}秒，回合数：{turns}'
    text_mode='模式：'
    text=''
    if mode == []:
        text_mode+='无'
    else:
        for i in mode:
            text_mode=text_mode+name[i]
    times=1
    if stage==4:
        times+=1
    if 3 in mode:
        times+=1
    if 100 in mode:
        times+=1
    if turns<=8:
        times+=1
    if 6 in mode:
        times*=0.3
    j=0
    for i in artifact:
        j+=artifact[i]
    for i in range(j):
        times*=3
    if 4 in mode:
        times *= 8
    if stage==3:
        times*=25
    i=item[win]
    k=100
    for j in i:
        if j=='死亡证明':
            k += i[j]*50
        else:
            k+=i[j]*10
    if tar<=0:
        k+=150
        text+='击破靶子！\n'
    k+=point[win]
    k1=round(k*times,1)
    a={players[win]:[nick[win],k1],players[loser]:[nick[loser],k1*(-1)]}
    cal(a)
    text+= f'''比分：{nick[0]}：{score[0]},{nick[1]}：{score[1]}\n{text_mode}\n{text_time}\n分数：{k}，倍数：{times}
{nick[win]}赢走了{nick[loser]}{k1}铸币'''
    f = open('../json/俄罗斯轮盘胜率.json', 'r')
    i = json.load(f)
    f.close()
    for j in [0,1]:
        k=str(players[j])
        if k not in i:
            i[k]=[0,0,0]
        i[k][0]=nick[j]
        if win==j:
            i[k][1]+=1
        else:
            i[k][2]+=1
    f = open('../json/俄罗斯轮盘胜率.json', 'w')
    json.dump(i, f)
    f.close()
    f = open('../json/俄罗斯轮盘历史记录.json', 'r')
    i = json.load(f)
    f.close()
    i.append(text)
    f = open('../json/俄罗斯轮盘历史记录.json', 'w')
    json.dump(i, f)
    f.close()
    text='游戏结束\n'+text
    send_msg({'msg_type': 'group', 'number': group, 'msg': text})

def transform(over, mode, loser, turn, group, hp,score,stage,item,ment,clip,nick,point):
    if over == 1 and stage!=5 and 2 not in score:
        for k in [0,1]:
            i=item[k]
            for j in i:
                if j == '死亡证明':
                    point[k]+= i[j] * 50
                else:
                    point[k]+= i[j] * 10
        hps=stage*2-2
        if 10 in mode:
            hps+=1
        if 18 in mode:
            hps*=2
        hp = [hps,hps]
        i = {2: '无道具', 3: '每回合获得一个道具', 4: '每回合获得两个道具，当生命值小于或等于3时，无法恢复生命值'}
        if 1 in mode:
            text=f'现在是第{stage-1}阶段，受【西部对决】影响，无道具，每个玩家有{hps}点生命值。'
        else:
            text= f'现在是第{stage-1}阶段，此阶段{i[stage]}，每个玩家有{hps}点生命值。'
        turn = loser
        item=[{
               '刀': 0, '烟': 0, '放大镜': 0, '灌铅骰子': 0, '炸药': 0, '手铐': 0,
               '铁索连环': 0, '洛欧塞布': 0, '死亡证明': 0,'午时已到':0,'baba':0
                     }, {
                         '刀': 0, '烟': 0, '放大镜': 0, '灌铅骰子': 0, '炸药': 0, '手铐': 0,
                         '铁索连环': 0, '洛欧塞布': 0, '死亡证明': 0,'午时已到':0,'baba':0
                         }]
        if 8 in mode:
            j = {2: 1, 3: 1, 4: 2}
            for i in range(j[stage]):
                item=distribute(1-turn,mode,item)
            t=add(1-turn, item, nick)
            text+=t
        ment={'knife':0,'chain':0,'handcuffs':0,'ban':0}
        send_msg({'msg_type': 'group', 'number': group, 'msg': text})
        clip = load(stage, group)
    return turn,hp,item,ment,clip,point

def use(dic,j,group,name):
    nick=dic['nick']
    mode=dic['mode']
    item = dic['item']
    turn1=turn = dic['turn']
    stage = dic['stage']
    mode = dic['mode']
    hp = dic['hp']
    players = dic['players']
    loser = dic['loser']
    ment = dic['ment']
    nick = dic['nick']
    clip = dic['clip']
    over = dic['over']
    score = dic['score']
    text = '没有该道具/你已使用过这个效果。'
    k=0
    if j[:5]=='baba#':
        i=j[5:]
        j='baba'
    if item[turn][j] > 0:
        item[turn][j] -= 1
        k=1
    elif item[turn]['死亡证明']>0:
        item[turn]['死亡证明'] -= 1
        k=2
    if k!=0:
        if j == '刀' and ment['knife'] != 1:
            ment['knife']=1
            text = '已使用。'
        elif j=='午时已到':
            hp[0]=hp[1]=1
            for i in item[turn]:
                item[turn][i]=0
            clip = load(stage, group)
            text='It`s high noon.'
        elif j=='烟':
            hp[turn]+=1
            if stage==4 and hp[turn]<=4:
                hp[turn]-=1
                text='已经无法恢复生命值。'
            else:
                text = '已使用。'
        elif j=='放大镜':
            i={1:'实弹',0:'空弹'}
            text =f'是{i[clip[0]]}。'
        elif j=='灌铅骰子':
            clip=load(stage, group)
            item=distribute(turn, mode, item)
            text = '已使用。'
        elif j == '炸药':
            hp[1-turn]-=1
            text=f'{nick[1-turn]}受到了一点伤害。'
            if ment['chain'] == 1:
                ment['chain']=0
                hp[turn]-=1
                text+=f'受到【铁索连环】的影响，{nick[turn]}也受到了伤害。'
            over, loser, score, t ,stage= damage(hp, score, nick, loser,stage)
            text += t
            if ment['handcuffs']==1:
                ment['handcuffs']=0
                text+='【手铐】已失效'
            turn = 1-turn
        elif j == '手铐' and ment['handcuffs'] !=1:
            ment['handcuffs']= 1
            text = '已使用。'
        elif j == '铁索连环' and ment['chain'] !=1:
            ment['chain']=1
            text = '已使用。'
        elif j == '洛欧塞布'and ment['ban'] != 2:
            ment['ban']=2
            text='已使用。'
        elif j=='baba':
            try:
                i = int(i)
                if i not in mode:
                    mode.append(i)
                    text=f'baba is baba.已开启模式{name[i]}。'
                else:
                    text='该模式已经开启，请勿重复。'
                    if k == 1:
                        item[turn][j] += 1
                    else:
                        item[turn]['死亡证明'] += 1
            except:
                text='检查你的指令格式。'
                if k == 1:
                    item[turn][j] += 1
                else:
                    item[turn]['死亡证明'] += 1
        else:
            if k==1:
                item[turn][j] += 1
            else:
                item[turn]['死亡证明'] += 1
    t=add(turn1, item, nick)
    text+=t
    send_msg({'msg_type': 'group', 'number': group, 'msg': text})
    return ment, turn, loser, hp, item, clip, over, stage, score,mode

def hurt(dic,obj,group):
    item=dic['item']
    turn = dic['turn']
    stage = dic['stage']
    mode = dic['mode']
    hp = dic['hp']
    point=dic['point']
    players = dic['players']
    loser = dic['loser']
    ment = dic['ment']
    nick = dic['nick']
    clip = dic['clip']
    over = dic['over']
    score = dic['score']
    flag=clip.pop(0)==1
    i={True:'实弹',False:'空弹'}
    if flag:
        dmg=1
    else:
        dmg=0
    text=f'{nick[turn]}向{nick[obj]}射击。是{i[flag]}。'
    if flag and obj==turn and ment['handcuffs']==1:
        ment['handcuffs']=0
        text+='由于向自己开枪且为实弹，【手铐】已失效。'
    if 6 in mode and random.randint(1, 5) == 1:
        obj = 1-obj
        text+='受到【浑水摸鱼】的影响，方向错了。'
    if ment['knife']==1:
        if flag:
            dmg+=1
            text += '受到【刀】的影响，伤害+1。'
        else:
            text+='【刀】已失效。'
        ment['knife']=0
    if 5 in mode and flag and 1<=random.randint(1,100)<=15:
        dmg=dmg*2
        text+='受到【命运之轮】的影响，伤害翻倍。'
    text+=f'实际对{nick[obj]}造成了{dmg}点伤害。'
    if turn==obj and not flag:
        if 7 in mode:
            text+= '受到【亡命之徒】的影响，对对手造成一点伤害。'
            hp[1-turn]-=1
            if ment['chain'] == 1:
                hp[turn]-=1
                text += f'受到【铁索连环】的影响，{nick[turn]}也受到了伤害。'
                ment['chain']=0
    hp[obj] -= dmg
    if ment['chain']==1 and flag:
        hp[1-obj]-=dmg
        text+=f'受到【铁索连环】的影响，{nick[1-obj]}也受到了伤害。'
        ment['chain']=0
    text += f'\n当前剩余生命值：{nick[0]}：{hp[0]}，{nick[1]}：{hp[1]}'
    over,loser,score,t,stage=damage(hp,score,nick,loser,stage)
    text+=t
    if 9 in mode and flag and obj!=turn:
        item = distribute(turn, mode, item)
        text+='\n'
        t=add(turn,item,nick)
        text+=t
    if flag or obj != turn:
        turn=1-turn
        if ment['handcuffs']==1:
            turn=1-turn
            text+=f'\n受到【手铐】的影响，仍然是{nick[turn]}的回合。'
            ment['handcuffs']=0
    if flag and obj!=turn:
        point[turn]+=5
    if turn == obj and not flag:
        point[turn]+=2
    i=sum(clip)
    if i!=0:
        text+=f'\n弹夹剩余{i}颗实弹，{len(clip)-i}颗空弹。'
    send_msg({'msg_type': 'group', 'number': group, 'msg': text})

    return ment,over,stage,hp,loser,turn,score,item,point,clip

def load(stage, group):
    if stage == 2:
        shot = random.randint(1, 2)
        full = 3
    elif stage == 3:
        shot = random.randint(2, 3)
        full = 5
    else:
        shot = random.randint(2, 4)
        full = 6
    clip = [0 for i in range(full)]
    ran = random.sample(range(len(clip)), shot)
    for i in ran:
        clip[i] = 1
    text = f'装弹！装入了{shot}颗实弹，{full-shot}颗空弹'
    send_msg({'msg_type': 'group', 'number': group, 'msg': text})
    return clip

def distribute(turn,mode,item):
    s=0
    j=item[turn]
    for i in j:
        s+=j[i]
    j = random.randint(1, 100)
    if 14 in mode and s>=3:
        return item
    if 2 in mode:
        if 1<=j<=15:
            k='刀'
        elif 16<= j <=30:
            k='烟'
        elif 31<= j <= 45:
            k='放大镜'
        elif 46<= j <= 60:
            k='灌铅骰子'
        elif 61 <= j <= 75:
            k='手铐'
        elif 76<= j <= 85:
            k='炸药'
        elif 86<=j<=90:
            k = '铁索连环'
        elif 91<= j <= 94:
            k = '洛欧塞布'
        elif 95<=j<=97:
            k='baba'
        elif 98<= j <= 99:
            k = '午时已到'
        elif j== 100:
            k = '死亡证明'
    else:
        if 1 <= j <= 20:
            k = '刀'
        elif 21 <= j <= 40:
            k = '烟'
        elif 41<= j <= 60:
            k = '放大镜'
        elif 61 <= j <= 80:
            k = '灌铅骰子'
        elif 81<=j<=100:
            k='手铐'
    item[turn][k]+=1
    return item

def wheel(dic,rev):
    text=''
    s=0
    item=dic['item']
    turn=dic['turn']
    stage= dic['stage']
    mode= dic['mode']
    mes = rev['raw_message']
    hp=dic['hp']
    players=dic['players']
    loser=dic['loser']
    ment=dic['ment']
    nick=dic['nick']
    clip=dic['clip']
    over=dic['over']
    group1=dic['group1']
    score=dic['score']
    qq=rev['sender']['user_id']
    group=rev['group_id']
    nickname=rev['sender']['nickname']
    point=dic['point']
    tar=dic['tar']
    time1=dic['time']
    turns=dic['turns']
    cur_turns=dic['cur_turns']
    reset=dic['reset']
    skip=dic['skip']
    artifact=dic['artifact']
    name= {1: '【西部对决】', 2: '【奇珍异宝】', 3: '【一决胜负】', 4: '【孤注一掷】', 5: '【命运之轮】',
         6: '【浑水摸鱼】', 7: '【亡命之徒】', 8: '【后发制人】', 9: '【乘胜追击】', 10: '【旷日持久】'
           ,11:'【生命分流】',100:'【风起云涌】',12:'【正中靶心】',13:'【以逸待劳】',14:'【狡兔三窟】'
           ,15:'【幸运观众】',16:'【死亡计时】',17:'【上古神器】',18:'【病入膏肓】'}
    if stage == 0:
        if mes=='加入轮盘':
            if group1==0:
                nick.append(nickname)
                players.append(qq)
                text='加入成功'
                group1=group
            else:
                if len(players)!=2:
                    if qq not in players:
                        nick.append(nickname)
                        players.append(qq)
                        text='加入成功'
                    else:
                        text='请勿重复加入'
                else:
                    text='人数已满'
        elif mes=='退出轮盘':
            if qq in players:
                ind=players.index(qq)
                players.pop(ind)
                nick.pop(ind)
                text= '退出成功'
                if len(players) == 1:
                    group1=0
            else:
                text='你还没有加入游戏'
        elif mes=='开始轮盘':
            if qq in players:
                if len(players)==2:
                    stage=1
                    text='请选择模式'
                else:
                    text='人数不足'
            else:
                text='有其他群正在使用该功能'
    elif stage==1:
        if qq in players and len(mes)>=4 and mes[0:3]=='模式#':
            try:
                if '，' in mes:
                    j=mes[3:]
                    k=j.split('，')
                    print(k)
                    text='已开启模式'
                    for i in k:
                        i=int(i)
                        if i not in mode:
                            mode.append(i)
                            text+=f'{name[i]}'
                else:
                    i=int(mes[3:])
                    if i in mode:
                        mode.remove(i)
                        text=f'已关闭模式{name[i]}'
                    else:
                        mode.append(i)
                        text=f'已开启模式{name[i]}'
            except:
                text='请检查你的指令'
        elif qq in players and mes == '开始轮盘':
            time1=time.time()
            if 100 in mode:
                i=random.randint(2,5)
                j=list(name)
                j.remove(100)
                random.shuffle(j)
                mode=j[:i]
                mode.append(100)
            text=f'本局对战的模式：'
            for i in mode:
                text+=name[i]
            send_msg({'msg_type': 'group', 'number': group, 'msg': text})
            stage=2
            if 3 in mode:
                stage=4
            if 17 in mode:
                k=list(artifact[0])
                for i in [0,1]:
                    j=random.choice(k)
                    artifact[i][j]+=1
                    text='你获得了'+j
                    send_msg({'msg_type': 'private', 'number': players[i], 'msg': text})
            over=1
            loser=turn=random.randint(0,1)
            text=f'现在是{nick[turn]}的回合。'
            turn, hp ,item,ment,clip,point= transform(over, mode, loser, turn, group, hp, score,stage,item,ment,clip,nick,point)
            if 3 in mode:
                if 1 not in mode:
                    for i in range(2):
                        item = distribute(turn, mode, item)
                    t = add(turn, item, nick)
                    text += t
            over=0
        elif qq not in players:
            text = '有其他人在进行游戏'
    elif stage not in [0, 1]:
        if qq==players[turn]:
            turn1=turn
            a=b=c=0 #a是否需要结算阶段结束，b是否直接结算胜利，c是否使用以逸待劳
            if mes=='向自己开枪' or mes=='向自己射击':
                ment,over, stage, hp, loser,turn,score,item,point,clip= hurt(dic, turn,group)
                a=1

            elif mes == '向对手开枪' or mes=='向对手射击':
                ment,over, stage, hp, loser,turn,score,item,point,clip= hurt(dic, 1-turn,group)
                a=1

            elif len(mes) > 2 and mes[:2] == '使用':
                j=mes[2:]
                if j in artifact[0]:
                    if artifact[turn][j]>0:
                        artifact[turn][j]-=1
                        if j=='沃金的手':
                            hp[0],hp[1]=hp[1],hp[0]
                            text=f'当前剩余生命值：{nick[0]}：{hp[0]}，{nick[1]}：{hp[1]}'
                        elif j=='莽':
                            for i in range(6):
                                item = distribute(turn, mode, item)
                            text= add(turn, item, nick)
                        elif j=='整理好的茶具':
                            item[turn]['死亡证明']+=3
                            text = add(turn, item, nick)
                        send_msg({'msg_type': 'group', 'number': group, 'msg': text})
                        text=essay(j)
                    else:
                        text='你没有该神器。'
                else:
                    if ment['ban']!=1:
                        if j in item[0] or len(j)>5 and j[:5]=='baba#':
                            ment, turn, loser, hp, item, clip, over, stage,score,mode= use(
                            dic, j, group,name)
                            a=1
                    else:
                        text='受【洛欧塞布】影响，该回合不能使用道具。'

            elif mes=='苦肉':
                if 11 in mode:
                    hp,over, loser,score,ment,stage=mode11(dic)
                    a=1
                else:
                    text='本局对战中没有模式【生命分流】'

            elif mes=='向靶子射击' or mes=='向靶子开枪':
                if 12 in mode:
                    hp,tar,turn,ment,b,clip=mode12(dic)
                    a=1
                else:
                    text='本局对战中没有模式【正中靶心】'

            elif mes=='跳过回合':
                if 13 in mode:
                    if skip[turn]==0:
                        item=distribute(turn, mode, item)
                        text=f'{nick[turn]}使用【以逸待劳】，获得了一个道具。'
                        t = add(turn, item, nick)
                        skip[turn]=1
                        c=1
                        text += t
                        turn = 1 - turn
                    else:
                        text='上回合已使用过【以逸待劳】'
                else:
                    text='本局对战中没有模式【以逸待劳】'
                send_msg({'msg_type': 'group', 'number': group, 'msg': text})

            elif mes[:2]=='重置':
                if 15 in mode:
                    i=mes[2:]
                    if reset==0:
                        if i in item[turn]:
                            if item[turn][i]>0:
                                item[turn][i]-=1
                                reset=1
                                item=distribute(turn, mode, item)
                                text = f'{nick[turn]}使用【六面骰】，重置了{i}。'
                                t = add(turn, item, nick)
                                text += t
                            else:
                                text='没有这个道具'
                        else:
                            text='检查你的道具名'
                    else:
                        text='本回合已重置过'

            i = {2: 6, 3: 10, 4: 14}
            if (stage != 5 and 2 not in score and b==0) and cur_turns==i[stage] and 16 in mode and over!=1 and turn!=turn1:
                over = 1
                a = 1
                if hp[0]==hp[1]:
                    text='死亡计时已到，双方同时死亡。'
                else:
                    stage += 1
                    if hp[0]>hp[1]:
                        loser=1
                        score[0]+=1
                        text=f'死亡计时已到，{nick[1]}死亡。'
                    else:
                        loser=0
                        score[1] += 1
                        text=f'死亡计时已到，{nick[0]}死亡。'
                send_msg({'msg_type': 'group', 'number': group, 'msg': text})

            if (stage != 5 and 2 not in score and b==0) and 18 in mode and turn!=turn1:
                hp[0]-=1
                hp[1]-=1
                text='受【病入膏肓】影响，双方受到了一点伤害。'
                over, loser, score, t, stage = damage(hp, score, nick, loser, stage)
                text+=t
                send_msg({'msg_type': 'group', 'number': group, 'msg': text})


            if (stage != 5 and 2 not in score and b==0) and a==1:
                turn, hp, item, ment, clip,point= transform(over, mode, loser, turn, group, hp, score, stage, item, ment,
                                                       clip, nick,point)
                if sum(clip) == 0:
                    clip = load(stage, group)

            if stage== 5 or 2 in score or b==1:
                if b==1:
                    winner=1-turn
                else:
                    if 2 in score:
                        winner = score.index(2)
                    else:
                        winner = score.index(1)
                dic = {'turn': turn, 'stage': stage, 'over': over,
                       'mode': mode, 'clip': clip, 'players': players, 'nick': nick
                    , 'score': score, 'loser': loser, 'hp': hp, 'ment': ment, 'item': item, 'group1': group1,
                       'point':point,'tar':tar,'time':time1,'turns':turns,'cur_turns':cur_turns,'reset':reset
                       ,'skip':skip,'artifact':artifact}
                settle(winner,dic,name)
                s=1

            elif turn1!=turn or over==1:
                if c==0:
                    skip[turn]=0
                reset=0
                cur_turns+=1
                turns+=1
                if over==1:
                    cur_turns=1
                j={2:0,3:1,4:2}
                if 1 not in mode:
                    for i in range(j[stage]):
                        item=distribute(turn, mode, item)
                text = f'第{cur_turns}回合（共{turns}回合），轮到{nick[turn]}行动。'
                if ment['ban']>0:
                    ment['ban']-=1
                t=add(turn,item,nick)
                text+=t
                over=0

        elif qq==players[1-turn] and group==group1:
            text='不是你的回合'
        elif group1 != group:
            text = '有其他群正在使用该功能'
        elif qq not in players:
            text = '有其他人在进行游戏'
    if text != '':
        send_msg({'msg_type': 'group', 'number': group, 'msg': text})
    if s==0:
        dic = {'turn': turn, 'stage': stage, 'over': over,
        'mode':mode,'clip':clip,'players':players,'nick':nick
        ,'score':score,'loser':loser,'hp':hp,'ment':ment,'item':item,'group1':group1
        ,'point':point,'tar':tar,'time':time1,'turns':turns,'cur_turns':cur_turns,'reset':reset
        ,'skip':skip,'artifact':artifact}
    else:
        dic=ini_wheel()
    return dic