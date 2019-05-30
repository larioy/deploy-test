# -*- coding: utf-8 -*-
"""
用于测试环境的全局配置
"""
from settings import APP_ID


# ===============================================================================
# 数据库设置, 测试环境数据库设置
# ===============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': APP_ID + "-test",                        # 测试数据库名 (请保持APP_ID+-test,否则APP部署脚本创建不了对应的数据库)
        'USER': 'root',                            # 你的数据库user
        'PASSWORD': 'TqcAtuef7G',                        # 你的数据库password
        'HOST': '192.168.165.42',                   		   # 数据库HOST
        'PORT': '3306',                        # 默认3306
    },
}
