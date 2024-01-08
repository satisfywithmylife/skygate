import requests
from eth_account import Account
from eth_account.messages import encode_defunct
import time
from web3 import Web3, HTTPProvider
from pyuseragents import random as random_ua
from functools import wraps
import json

def retry(max_retries=3, wait_time=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:  
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Caught exception {e}, retrying in {wait_time} seconds...")
                    retries += 1
                    time.sleep(wait_time)
            raise Exception(f"Max retries exceeded ({max_retries})")

        return wrapper
    return decorator

class Skygate():

    log_file_name = 'checkin_account.txt'
    
    def __init__(self, pk, invite_code='', jwt='', is_daily=False, proxy={}):
        self.web3 = Web3(HTTPProvider('https://opbnb.publicnode.com'))
        self.host = 'https://apisky.ntoken.bwtechnology.net/api/{}'
        self.invite_code = invite_code # 邀请码（邀请人钱包地址）
        self.pk = pk # 签到账号私钥
        self.account:Account = self.web3.eth.account.from_key(pk)
        self.sign_str = 'skygate' # personal_sign 签名字符串
        self.jwt = jwt # jwt
        self.is_daily = is_daily
        self.proxy = proxy
        self.block_scan_tx_url = 'https://opbnbscan.com/tx/{}' # 区块浏览器
        
    
    def check_balance(self):
        opbnb_balance = self.web3.eth.get_balance(self.account.address)
        return opbnb_balance
    
    def check_has_slime_nft(self):
        nft_contract_address = Web3.to_checksum_address('0x961a98999f14e8c5e69bdd4ee0826d6e0c556a0d')
        nft_contract = self.web3.eth.contract(address=nft_contract_address, abi=self.load_abi('erc721.json'))
        return nft_contract.functions.balanceOf(owner=self.account.address).call()
    
    def dispatch_squead(self, data):
        address = Web3.to_checksum_address('0x9465fe0e8cdf4e425e0c59b7caeccc1777dc6695')
        tx = self.web3.eth.contract(address=address, abi=self.load_abi('abi.json')).functions.signin(data)
        tx_hash = self.make_tx(tx)
        return tx_hash
    
    def adventure(self):
        data = 2
        tx_hash = self.dispatch_squead(data)
        print(f'adventure success ! | Tx: {self.block_scan_tx_url.format(tx_hash)}')

    def treasure(self):
        data = 1
        tx_hash = self.dispatch_squead(data)
        print(f'collect treasure success ! | Tx: {self.block_scan_tx_url.format(tx_hash)}')
    
    def explore(self):
        address = Web3.to_checksum_address('0xd42126d46813472f83104811533c03c807e65435')
        tx = self.web3.eth.contract(address=address, abi=self.load_abi('abi.json')).functions.signin(1)
        tx_hash = self.make_tx(tx)
        print(f'explore success ! | Tx: {self.block_scan_tx_url.format(tx_hash)}')
        
    def make_tx(self, tx):
        tx = tx.build_transaction({
            'value': 0,
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'from': self.account.address,
            'gas': 0,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0
        })
        tx.update({'maxFeePerGas': self.web3.eth.gas_price})
        tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})
        tx.update({'gas': self.web3.eth.estimate_gas(tx)})
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        while tx_receipt is None or tx_receipt['status'] is None:
            time.sleep(1)
            tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)

        tx_hash = Web3.to_hex(tx_hash)
        return tx_hash

        
    def load_abi(self, abi_name):
        with open(abi_name, 'r') as f:
            json_data = json.load(f)
            return json_data

    @retry(max_retries=30, wait_time=5)
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

    @retry(max_retries=30, wait_time=5)
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
    
    @retry(max_retries=30, wait_time=5)
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
            if res["0"] == "already rewarded the daily points":
                print(f'{self.account.address} has checkin today')
                return True
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
    def daily_explore_treasure_adventure():
        # 每日冒险和收集宝藏可以获得积分的次数，各6次
        daily_treasure_adventure_times = 6
        for log_str in Skygate.iter_file(Skygate.log_file_name):
            tmp = log_str.split('----')
            _, pk, jwt, invite_code = tmp[0], tmp[1], tmp[2], tmp[3]
            sg = Skygate(pk=pk, jwt=jwt, invite_code=invite_code, is_daily=True, proxy={})
            if not sg.check_balance():
                print(f'{sg.account.address} have no opbnb balance as gas fee, skip this account daily explore,treasure,adventure')
                continue
            
            print(f'========================={sg.account.address} daily explore_treasure_adventure start============================')
            # 每日探索1次，10积分
            sg.explore()
            # 检查账户是否有史莱姆nft
            slime_nft_num = sg.check_has_slime_nft()
            if not slime_nft_num:
                print(f'{sg.account.address} don‘t have slime nft, skip this account daily treasure,adventure')
                print(f'========================={sg.account.address} daily explore_treasure_adventure end============================')
                continue
            else:
                print(f'{sg.account.address} have {slime_nft_num} slime nft, start daily treasure,adventure')

            
            # 每日探险6次，每次获得积分随机              
            for i in range(daily_treasure_adventure_times):
                print(f'{str(i+1)}th adventure start')
                try:
                    sg.adventure()
                except Exception as e:
                    print(f'{sg.account.address} adventure error , reason {e}, skip adventure')
                    break
                
            # 每日收集宝藏6次，每次获得积分随机
            for i in range(daily_treasure_adventure_times):
                print(f'{str(i+1)}th treasure start')
                try:
                    sg.treasure()
                except Exception as e:
                    print(f'{sg.account.address} treasure error, reason {e}, skip collect treasure')
                    break
            print(f'========================={sg.account.address} daily explore_treasure_adventure end============================')

 
 
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
# # 生成主钱包地址数
# main_account_num = 100
# # 每个主钱包邀请的小号数
# invite_num = 20
# for i in range(main_account_num):
#     main_account_pk = Skygate.get_random_account_pk()
#     main_sg = Skygate(pk=main_account_pk, proxy=proxy)
#     try:
#         main_sg.checkin()
#     except Exception as e:
#         print(str(e))
#         time.sleep(3)
#         continue
#     invite_code = str(main_sg.account.address)
#     for z in range(invite_num):
#         sub_account_pk = Skygate.get_random_account_pk()
#         sub_sg = Skygate(pk=sub_account_pk, invite_code=invite_code, proxy=proxy)
#         try:
#             sub_sg.checkin()
#         except Exception as e:
#             print(str(e))
#             time.sleep(3)
#             continue
# ==================================每日签到==================================
# Skygate.daily_checkin(proxy)

# ==================================每日explore，collect treasure, adventure==================================
# Skygate.daily_explore_treasure_adventure()