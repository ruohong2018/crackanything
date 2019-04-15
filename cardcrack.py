# -*- coding: UTF-8 -*-
import subprocess
import re
import bankcode
import binascii
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
#响应包如下 17 09 13 (17年9月13号) 16 45 38 (16:45:38) 00 00 00 35 00 00 (3500.00元) 00 00 00 00 00 00 (其他金额) 01 56 (中国) 01 56 (人民币)
#00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0A (空) 21 (交易类型) 00 31 (应用交易计数器) 90 00 (状态字：成功)
def getHistory(ascii,i):
    if len(ascii[i]) < 98:
        return 0
    strascii=ascii[i]
    date='20'+strascii[0:2]+u'年'+strascii[2:4]+u'月'+strascii[4:6]+u'日 '+strascii[6:8]+u'时'+strascii[8:10]+u'分'+strascii[10:12]+u'秒'
    money=re.sub(r"\b0*([1-9][0-9]*|0)", r"\1", strascii[12:22]+u'元'+strascii[22:24]+u'分')
    if strascii[36:40] == '0156':
        position = u'中国'
    if strascii[40:44] == '0156':
        currency = 'RMB'
    
    tmp = strascii[44:84]
    while 1:
        if tmp[-1]=='0' and tmp[-2]=='0':
            tmp=tmp[0:len(tmp)-2]
        elif tmp[-1] != '0':
            break;
    business = str(binascii.a2b_hex(tmp))

    return (' %d'+'\t'+date+'\t'+money+'\t'+business+'\t\t\t'+position+'\t\t\t\t'+currency)%i
# 启动Proxmark3
pm3 = subprocess.Popen("proxmark3 /dev/tty.usbmodem1421", shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
# 选择支付系统UID+ATQA(hf 14a reader)+PSE-1PAY.SYS.DDF01<=ASSIC=>315041592E5359532E4444463031,并建立连接
pm3.stdin.write('hf 14a reader')
head = pm3.communicate()[0].split('UID : ')[1].split(' SAK : ')[0].replace(' ','').replace('\n','').replace('ATQA:','').upper()
pm3 = subprocess.Popen("proxmark3 /dev/tty.usbmodem1421", shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
pm3.stdin.write('hf 14a raw -c -s -p '+head+'315041592E5359532E4444463031\n')
# 借记卡最后一位为1贷记卡为2,00A40400固定08后续长度（可以读出来）A000000333(RID)+010101(认证中心公钥索引PKI)
#6F6(FCI文件控制信息)68408A000000333010101A55A500A50424F432044656269748701015F2D047A68656E9F1101019F120D494342432050626F63436172649F381B9F66049F02069F03069F1A0295055F2A029A039C019F37049F2103BF0C0FD1023132C204494342439F4D020B0A90004261
pm3.stdin.write('hf 14a raw -c 0300A4040008A000000333010101 -p\n')
# 发送银行卡信息查询命令，00B2 01第一条记录0C选择返回的目录文件短标志+读P1指定目录
# 70标签 64长度 5713（二磁道等价数据）6212261115000459789（卡号）D2701（有效期）2207149991204F（补足）5F20（磁道一自定义数据） 
# 14 202020202020202020（可能是身份证）20202020202020202020209F1F18 303032303（补足）4303030303030303030303731343030303030305F3401019F61122020202020202020202020202020202020209F6201209000B482
pm3.stdin.write('hf 14a raw -c 0200B2010C -p\n')
# 发送卡主信息查询指令
# 70（模板）  09 5F20（持卡人姓名） 02 2020(有的银行是存放的是姓名的拼音的ACII码，但是PBOC3.0建议不要存放私人信息) 9F62（证件类型） 01 00（身份证）
pm3.stdin.write('hf 14a raw -c 0300B2020C -p\n')
# 循环发送消费记录查询命令
for i in range(1, 11):
    head = '02'
    if i % 2 == 0: head = '03'
    if i != 10: i = "0" + str(i)
    pm3.stdin.write('hf 14a raw -c ' + head + '00B2'+ str(i) +'5C00 -p\n')
# 断开银行卡连接,此处报错
# pm3.stdin.write('hf 14a raw -a\n')
out = pm3.communicate()[0]
outarray = out.split("proxmark3>")
cardnumber = outarray[3].split('\n')[2].replace(' ','')[10:29]
idnumber = outarray[4].split('\n')[2].replace(' ','')
history = list()
#print outarray
# 循环添加交易记录到history列表
for i in range(5,15):
    history.append(outarray[i].split('\n')[2].replace(' ','')[2:100])
print '--------------------------------------------------------------------------------------------'
print '                                   银行闪付卡信息显示                                   '
print '--------------------------------------------------------------------------------------------'
if len(idnumber) >= 90:
    print u'姓      名：' + binascii.a2b_hex(idnumber[60:-8]).decode('gbk')
    print u'卡主身份证：' + binascii.a2b_hex(idnumber[12:48]).decode('gbk')
print u'银行卡卡号：' + cardnumber
if cardnumber:
	print u'银行卡类型：' + bankcode.getCardType(cardnumber)
#print u'身份证号码：' + idnumber
print '--------------------------------------------------------------------------------------------'
print u'编号         交易时间               交易金额         商户名称          交易地点         交易币种'
#print history
for i in range(len(history)):
    result=getHistory(history,i)
    if result != 0:
        print '--------------------------------------------------------------------------------------------'
        print result
#3os.system("rm proxmark3.log")