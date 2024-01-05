import requests
from eth_account import Account
from eth_account.messages import encode_defunct
import time
from web3 import Web3
from pyuseragents import random as random_ua

class Skygate():

    log_file_name = 'checkin_account.txt'
    
    def __init__(self, pk, invite_code='', jwt='', is_daily=False, proxy={}):
        self.host = 'https://apisky.ntoken.bwtechnology.net/api/{}'
        self.invite_code = invite_code # 邀请码（邀请人钱包地址）
        self.pk = pk # 签到账号私钥
        self.account:Account = Web3().eth.account.from_key(pk)
        self.sign_str = 'skygate' # personal_sign 签名字符串
        self.jwt = jwt # jwt
        self.is_daily = is_daily
        self.proxy = proxy

    def get_info(self):
        # 根据jwt获取账号信息
        url = self.host.format('get_skyGate_coin.php')
        payload = {
            'api_id': 'skyark_react_api',
            'api_token': '3C2D36F79AFB3D5374A49BE767A17C6A3AEF91635BF7A3FB25CEA8D4DD',
            'jwt': self.login()
        }
        res = requests.post(url=url, data=payload, timeout=30, proxies=self.proxy, headers=self.get_headers())
        if res.status_code != 200:
            raise Exception(f'get_info error, status code {res.status_code}')
        
        res = res.json()
     
        if res['err'] != 0:
            raise Exception(f'get_info error, error code {res["err"]}, error message {res["0"]}')

        # {"err":0,"uName":"0x1ad453068d1808e213b46ce415a51d38b8419e57","gateWalletAddr":"9aPW9RhQ9c9eWBK","uWalletAddr":"0x1ad453068d1808e213b46ce415a51d38b8419e57","coin":"100","participationTime":"","week":"","scheduleStart":1700179200,"scheduleEnd":1734393599,"joinAmount":"100","additionalCost":"0","winAnnDate":1702857600,"advName":"31thadvanture","inviteCode":"9aPW9","uId":"21244085","userLevel":"1"}
        return res
    
    def get_headers(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Origin': 'https://skygate.skyarkchronicles.com',
            'Referer': 'https://skygate.skyarkchronicles.com/',
            'User-Agent': random_ua(),
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }

        return headers

    def login(self):
        # 获取登录态jwt
        if self.jwt:
            return self.jwt
        
        msghash = encode_defunct(text=self.sign_str)
        sign = Account.sign_message(msghash, self.pk)
       
        url = self.host.format('wallet_signin.php')
        payload = {
            'api_id': 'skyark_react_api',
            'api_token': '3C2D36F79AFB3D5374A49BE767A17C6A3AEF91635BF7A3FB25CEA8D4DD',
            'uWalletAddr': str(self.account.address),
            'sign': str(sign.signature.hex())
        }
        if self.invite_code:
            payload['inviter'] = self.invite_code

        res = requests.post(url=url, data=payload, timeout=30, proxies=self.proxy, headers=self.get_headers())
        if res.status_code != 200:
            raise Exception(f'login error, status code {res.status_code}')
        
        res = res.json()
        if res['err'] != 0:
            raise Exception(f'login error, error code {res["err"]}, error message {res["0"]}')
        
        self.jwt = res['jwt']
        if not self.is_daily:
            self.save()
        #{"err":0,"msg":"verify_success","jwt":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1SWQiOiIyMTI0NDA4NSIsInVXYWxsZXRBZGRyIjoiMHgxYWQ0NTMwNjhkMTgwOGUyMTNiNDZjZTQxNWE1MWQzOGI4NDE5ZTU3In0.shwMdrnWwqQJy3taJxhT2_mIsPsCF3e8CsWsmm_oTG4xhZsh_WOEqQlWC7AULffc1hj3xrx6btwEcXBO_MXu8yPqkDF6LN1rPtVNLEK3ISOCpbzfHMcMOpodZgmsPsd3YkDkqAnklQIO6rW3wAKhWgbZO1HHW5fhQM8sN-7cWXo","uWalletAddr":"0x1ad453068d1808e213b46ce415a51d38b8419e57"}
        return self.jwt
    
    def checkin(self):
        # 签到
        url = self.host.format('checkIn_skyGate_member.php')
        payload = {
            'api_id': 'skyark_react_api',
            'api_token': '3C2D36F79AFB3D5374A49BE767A17C6A3AEF91635BF7A3FB25CEA8D4DD',
            'jwt': self.login()
        }

        res = requests.post(url=url, data=payload, timeout=30, proxies=self.proxy, headers=self.get_headers())
        if res.status_code != 200:
            raise Exception(f'{self.account.address} checkin error, status code: {res.status_code}')  

        res = res.json()
        if res['err'] != 0:
            raise Exception(f'{self.account.address} checkin error, error code {res["err"]}, error message {res["0"]}')  
        
        # {"err":1,"0":"already rewarded the daily points"}
        # {"err":0,"dailyGift":50,"SlimeGift":0,"fullCost":150,"dailyclaimInWeek":[{"Time":1704267789,"Amount":"50"},{"Time":1704422086,"Amount":"50"}],"indicator":1}
        
        return res


    def save(self):
        # 保存账号到当前文件夹的checkin_account.txt文件, 格式： 地址----私钥----jwt----邀请人地址（邀请码）
        log_str = f'{self.account.address}----{self.pk}----{self.jwt}----{self.invite_code}\n'
        
        with open(self.log_file_name, 'a') as f:
            f.write(log_str)

    @staticmethod
    def iter_file(file_name):
        # 迭代文件
        with open(file_name, encoding='utf-8') as f:
            for line in f:
                the_line = line.strip()
                yield the_line

    @staticmethod
    def daily_checkin(proxy):
        for log_str in Skygate.iter_file(Skygate.log_file_name):
            tmp = log_str.split('----')
            _, pk, jwt, invite_code = tmp[0], tmp[1], tmp[2], tmp[3]
            sg = Skygate(pk=pk, jwt=jwt, invite_code=invite_code, is_daily=True, proxy=proxy)
            try:
                sg.checkin()
            except Exception as e:
                print(str(e))
                time.sleep(3)
                continue
 
    @staticmethod
    def get_random_account_pk(): 
        # 随机生成以太坊地址私钥
        return Account.create().key.hex()
    

proxy = {}
# 代理
# proxy = {
#     'http': '127.0.0.1:10809',
#     'https': '127.0.0.1:10809',
# }



# ================================第一次跑====================================
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
        time.sleep(3)
        continue
    invite_code = str(main_sg.account.address)
    for z in range(invite_num):
        sub_account_pk = Skygate.get_random_account_pk()
        sub_sg = Skygate(pk=sub_account_pk, invite_code=invite_code, proxy=proxy)
        try:
            sub_sg.checkin()
        except Exception as e:
            print(str(e))
            time.sleep(3)
            continue
# ==================================每日签到==================================
# Skygate.daily_checkin(proxy)