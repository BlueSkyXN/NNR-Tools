# NNR-Tools
这是一个对接NNR的工具库，非官方开发
- 不对工具库可用性/安全性/合规性提供任何支持和保证，仅供自行学习使用
- 看不懂请V50学费，你可以用 [Lark](https://bit.ly/LarkSKY) 联系我 
- 不对NNR相关工具提供的服务的可用性/安全性/合规性提供任何支持和保证，本人和NNR运营方无利益关系，只是单纯的消费者。

[NNR邀请链接](https://bit.ly/nnrinvite)

# NNR-Sync-HUAWEI.py
华为云相关使用手册 [HUAWEI_CLOUD.MD](HUAWEI_CLOUD/README.MD)
- 根据NNR的节点信息API，同步解析数据到华为云DNS解析
- 需要指定配置文件``-c NNR.conf``或者使用默认同目录的``NNR.conf``来使用

对于多IP的节点会采用母子策略，也就是母域名是完整的记录集，同时对每一个IP设置-01/-02之类的后缀加在域名中，你可以自己挑选单一的域名以便异常快速切换

## NNR.conf
本工具的主要配置文件 [NNR.conf](NNR.conf)

- [NNR_API] NNR的配置文件相关，主要包括固定的APIURL，你可以换成其他反代的URL；以及API_TOKEN需要在NNR的用户中心控制台中获取
- [HUAWEI_API] 华为云的配置文件相关，主要包括一些认证信息
- [DOMAIN_MAP] 域名映射的配置，包括根域名和UUID对应的域名前缀，UUID来自NNR的API中的SID，你可以参考 [SID.md](SID.md)
- [HUAWEI_DNS] 华为云DNS的配置文件相关，主要包括使用的域名对应的空间区域号码，也就是ZONE_ID

当然，我提供的是 ``NNR-Template.conf``，你需要改名为 ``NNR.conf`` 后编辑，建议根据自己的实际情况设置映射关系

## NNR-Sync-HUAWEI-HWS.py

- [NNR-Sync-HUAWEI.py](NNR-Sync-HUAWEI.py) 是在华为云云函数的无服务器环境中的实现，更方便简单

## CONFtoOneFile.py

- 你可以使用[CONFtoOneFile.py](CONFtoOneFile.py) 将``NNR.conf``转为可替换集成云函数py的配置部分，方便你编译云函数版本（HWS）的配置区块


# FAQ

1. 本工具是NNR官方的吗？
    - 不是，自己写的，与官方无任何关联和利益关系，不提供任何支持和保证，如果哪天跑路了别找我

2. 本工具提供免费技术支持和答疑吗？
    - 不提供，V50再说

3. 为什么没有CloudFlare/DNSPod/腾讯DNS/阿里DNS/亚马逊DNS等平台的对接？
    - 没人打钱

4. 使用你的邀请链接有什么好处吗？
    - 没有，只会让我多白嫖几天NNR的套餐

5. 快速打钱怎么弄

     [![赞助](https://img.shields.io/badge/-赞助-ff69b4?style=for-the-badge&logo=github)](https://github.com/sponsors/blueskyxn) -> [https://github.com/sponsors/blueskyxn](https://github.com/sponsors/blueskyxn)
