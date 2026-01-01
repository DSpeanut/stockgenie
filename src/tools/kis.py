from dotenv import load_dotenv
import os
import pandas as pd
import re


import sys
import logging
import pandas as pd
import sys
sys.path.append('/opentradingapi/')

import examples_user.kis_auth as ka
from examples_user.overseas_stock.overseas_stock_functions import *

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ka.auth()
trenv = ka.getTREnv()

# 삼성전자 현재가 시세 조회

result = inquire_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ovrs_excg_cd="NASD", tr_crcy_cd="USD")
print(result[0].head(2))


