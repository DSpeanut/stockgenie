from dotenv import load_dotenv
import os
import pandas as pd
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import logging
import pandas as pd
import sys
import sys
import os
from src.config.config import INVENTORY_PATH

import opentradingapi.examples_user.kis_auth as ka
from opentradingapi.examples_user.overseas_stock.overseas_stock_functions import *

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ka.auth()
trenv = ka.getTREnv()
result = inquire_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ovrs_excg_cd="NASD", tr_crcy_cd="USD")

result[0].to_csv(INVENTORY_PATH, index=False)


