## StoreQ&AToMongo

### 简介
存储stackoverflow的数据集到mongodb中。

数据集链接：https://www.kaggle.com/stackoverflow/stacksample/data

### 环境
- python3.4

### 运行前提
- 安装pymongo
```
pip install pymongo
```
- 数据集文件
代码中使用了三个数据集文件，变量及对应路径如下
```
tags_filename = './static/Tags.csv'
questions_filename = './static/Questions.csv'
answers_filename = './static/Answers.csv'
```

### 运行
运行`storeQ&AToMongo/index.py`
```
python index.py
```
