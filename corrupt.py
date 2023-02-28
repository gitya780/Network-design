# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 12:35:42 2022

@author: Geetesh
"""

import random

send_d = [1,2,3,4,5,6,7,8,9,10]
send_c = [0 if random.randint(0, len(send_d)) < 1 else i for i in send_d]
print('a:', send_d)
print('b:', send_c)