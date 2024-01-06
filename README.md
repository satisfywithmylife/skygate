<h1 align="center">Skygate</h1>

<p align="center">注册推荐小号<a href="https://skygate.skyarkchronicles.com/">Skygate</a></p>
<p align="center">
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
</p>

## ⚡ 安装
+ 安装 [python](https://www.google.com/search?client=opera&q=how+install+python)
+ [下载项目](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github) 并解压
+ 安装依赖包:
```python
pip install web3
pip install pyuseragents
```

## 💻 第一次跑
```python
proxy = {}
# 代理
# proxy = {
#     'http': '127.0.0.1:10809',
#     'https': '127.0.0.1:10809',
# }



# 生成主钱包地址数
main_account_num = 100
# 每个主钱包邀请的小号数
invite_num = 20
for i in range(main_account_num):
    main_account_pk = Skygate.get_random_account_pk()
    main_sg = Skygate(pk=main_account_pk, proxy=proxy)
    try:
        main_sg.checkin()
    except Exception as e:
        print(str(e))
        continue
    invite_code = str(main_sg.account.address)
    for z in range(invite_num):
        sub_account_pk = Skygate.get_random_account_pk()
        sub_sg = Skygate(pk=sub_account_pk, invite_code=invite_code, proxy=proxy)
        try:
            sub_sg.checkin()
        except Exception as e:
            print(str(e))
            continue
```

## ✔️ 日常签到
```python
proxy = {}
# 代理
# proxy = {
#     'http': '127.0.0.1:10809',
#     'https': '127.0.0.1:10809',
# }
Skygate.daily_checkin(proxy)
```
**第一次跑，会把主号和小号保存在当前文件夹下的 ```checkin_account.txt``` 文件内**

**日常签到，自动把 ```checkin_account.txt``` 文件内的账号跑一遍签到**

## 其他
**接口经常502，可能是刷的人太多了**

**已经优化加入自动重试机制**

## 📧 Contacts
+ 推特 - [@shawngmy](https://twitter.com/shawngmy)
+ tks for following，if u want get more info