# NNR-Tools
这是一个对接NNR的工具库，非官方开发
- 不对工具库可用性/安全性/合规性提供任何支持和保证，仅供自行学习使用
- 看不懂请V50学费
- 不对NNR相关工具提供的服务的可用性/安全性/合规性提供任何支持和保证，本人和NNR运营方无利益关系，只是单纯的消费者。

# NNR-Sync-HUAWEI.py
- 根据NNR的节点信息API，同步解析数据到华为云DNS解析
- 需要指定配置文件``-c NNR.conf``或者使用默认同目录的``NNR.conf``来使用

## NNR.conf
本工具的主要配置文件
- [NNR_API] NNR的配置文件相关，主要包括固定的APIURL，你可以换成其他反代的URL；以及API_TOKEN需要在NNR的用户中心控制台中获取
- [HUAWEI_API] 华为云的配置文件相关，主要包括一些认证信息
- [DOMAIN_MAP] 域名映射的配置，包括根域名和UUID对应的域名前缀，UUID来自NNR的API中的SID，你可以参考[SID.md](SID.md)
- [HUAWEI_DNS] 华为云DNS的配置文件相关，主要包括使用的域名对应的空间区域号码，也就是ZONE_ID

## NNR-Sync-HUAWEI-HWS.py

- ``NNR-Sync-HUAWEI.py`` 在华为云云函数的无服务器环境中的实现，更方便简单

## CONFtoOneFile.py

- 你可以使用 ``CONFtoOneFile.py``将NNR.conf转为可替换集成云函数py的配置部分，方便你编译云函数版本（HWS）的配置区块