# -*- coding: UTF-8 -*-
import subprocess
import re
import bankcode
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# 启动Proxmark3
pm3 = subprocess.Popen("proxmark3 /dev/tty.usbmodem1421", shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
# 选择支付系统UID+ATQA(hf 14a reader)+PSE-1PAY.SYS.DDF01<=ASSIC=>315041592E5359532E4444463031,并建立连接
pm3.stdin.write('hf 14a reader')
head = pm3.communicate()[0].split('UID : ')[1].split(' SAK : ')[0].replace(' ','').replace('\n','').replace('ATQA:','').upper()
pm3 = subprocess.Popen("proxmark3 /dev/tty.usbmodem1421", shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
pm3.stdin.write('hf 14a raw -c -s -p '+head+'315041592E5359532E4444463031\n')
# 借记卡最后一位为1贷记卡为2
pm3.stdin.write('hf 14a raw -c 0300A4040008A000000333010101 -p\n')
# # 发送银行卡信息查询命令
# pm3.stdin.write('hf 14a raw -c 0200B2010C -p\n')
# # 发送卡主信息查询指令
# pm3.stdin.write('hf 14a raw -c 0300B2020C -p\n')
# pm3.stdin.write('hf 14a raw -c 0380CA9F79 -p\n')
pm3.stdin.write('hf 14a raw -c 0300B2011400 -p\n')
# pm3.stdin.write('hf 14a raw -a\n')
out = pm3.communicate()[0]
outarray = out.split("proxmark3>") 
for str in outarray:
	print str

# 9F7A01 (电子现金终端指示器): 01
# 9F0206 (授权金额)：000000000000
# 5F2A02 (交易货币代码)：0156
# pm3.stdin.write('hf 14a raw -c 0280A800000B8309010000000000010156 -p\n')
# 80CA9F79
# 9F6D:电子现金重置阈  
# 9F77:电子现金余额上线      
# 9F78:电子现金单笔交易限额
# 9F5D:脱机可用余额    
# 9F6B:读取卡片 CVM 限额
#[8:20]
# pm3.stdin.write('hf 14a raw -c 0380CA9F78 -p\n')
# pm3.stdin.write('hf 14a raw -c 0380CA9F6B -p\n')
# pm3.stdin.write('hf 14a raw -c 0380CA9F5D -p\n')
# pm3.stdin.write('hf 14a raw -c 0380CA9F79 -p\n')
