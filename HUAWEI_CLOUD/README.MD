# HUAWEI华为云 引导手册

如果你看不懂如何使用，建议V我50教你怎么用华为云，你可以用 [Lark](https://bit.ly/LarkSKY) 联系我 

[NNR邀请链接](https://bit.ly/nnrinvite)

## 获取IAM用户Token（使用密码）
官方文档 [https://support.huaweicloud.com/api-iam/iam_30_0001.html](https://support.huaweicloud.com/api-iam/iam_30_0001.html)

根据文档指引进行TOKEN获取，我的测试环境为华为账号，我感觉应该基本都要求升级华为账号了，华为云账号我没有测试

配置文件中有
```
[HUAWEI_API]
HUAWEI_IAM_AccountName = hw
HUAWEI_IAM_UserName = iamname
HUAWEI_IAM_Password = iampwd
HUAWEI_IAM_Project = ap-southeast-3
```
- 其中 ``HUAWEI_IAM_AccountName``就是你的华为账号用户名，通常是hw开头的，也就是右上角默认登录后显示的名字
- 其中 ``HUAWEI_IAM_UserName``就是你的创建的子账号IAM的用户名，通常是自己设置的，以及它的密码  ``HUAWEI_IAM_Password``
- 其中 ``HUAWEI_IAM_Project`` 为请求接口区，部分接口不支持统一入口，通常情况下，我用的是新加坡的，你可以自己挑。（在右上角用户名->统一身份认证->项目，可以看到你的可用区）

## 设置DNS的ZONE区域
也就是你的域名的id

配置文件中有
```
[HUAWEI_DNS]
HUAWEI_DNS_ZONE_ID = xxx
```

- 你可以在WEB控制台的，打开具体哪个主域名的记录的页面的URL看到 ``zoneid``
- 也可以用我给的测试接口示例 ``TEST_HUAWEI_DNS_ZONE.py``中获取

# 华为云函数部署方法

- 选择任意可用区，比如新加坡等，注意NNR的接口屏蔽中国大陆和部分ISP，不保证可用性的
- 你可以使用 ``CONFtoOneFile.py``将NNR.conf转为可替换集成云函数py的配置部分
- 你需要修改云函数的配置部分后，把整个 ``NNR-Sync-HUAWEI-HWS.py`` 的内容复制到华为云函数的 Python 3.10环境的index.py中
- 你需要修改超时时间，默认是3s是不够的，大概需要20多秒，建议设置60s左右
- 实际内存使用大概40MB上下，因此最小的那档128MB即可
- 不需要修改函数执行入口，不需要配置环境变量
- 触发方式自己去触发器设置定时任务即可，不建议设置太快，用多了可能收费以及被NNR防火墙屏蔽