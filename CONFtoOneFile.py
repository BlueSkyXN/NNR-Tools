import configparser

# 创建配置解析器对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('NNR-Template.conf')

# 转换为Python格式的字符串
python_config_str = "CONFIG = {\n"

# 遍历配置节和键值对，将其添加到字符串中
for section in config.sections():
    python_config_str += f"    \"{section}\": {{\n"
    for key, value in config.items(section):
        python_config_str += f"        \"{key}\": \"{value}\",\n"
    python_config_str += "    },\n"

# 添加字符串结尾
python_config_str += "}\n"

# 输出转换后的Python格式字符串
print(python_config_str)
