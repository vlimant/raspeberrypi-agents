
# coding: utf-8

# In[4]:

from dbschema import Agents,Workload
from dbsession import get_session
import time
import os
import sys
import random

# In[15]:


# ## define finished workload
## running an available one
#myip= os.popen("ifconfig | grep eth0 -A1 | grep inet | awk '{ print $2}' | cut -d : -f 2").read().split('\n')[0]
myip = sys.argv[1]
print "my ip is",myip

### start an inifinit time loop
time_tick =0
while True:

    draw = random.random()
    if draw < 0.05:
        ##inject some work
        name =list('thisisapayload')
        random.shuffle(name)
        wln = ''.join(name)
        wls = random.randint( 200, 600 )
        os.system('curl "http://%s:8080/push_workload?workload=%s&CPUh=%s&keep_it_for_yourself=0"'%(myip,wln,wls))
    
    #print time_tick,"tick"
    time_tick+=1
    time.sleep(1)
    ## this is a  time tick
    ### query on running and available workload
    asession = get_session()
    #print "my ip is",myip
    myself = asession.query(Agents).filter(Agents.ip == myip).first()
    if not myself:
        break
    workforce = myself.workforce
    #print workforce,"is the work force"
    
    availables = asession.query(Workload).filter(Workload.status == 'next').all()
    runnings = asession.query(Workload).filter(Workload.status == 'running').all()
    ### running - workforce/tick
    next_time_tick=False
    capacity = workforce
    for wl in runnings + availables:
        ## there supposed to be only one.
        ####total = wl.CPUh
        remaining = wl.remaining
        #print capacity,"to account for"
        left_to_do = remaining - capacity 
        if left_to_do>0:
            wl.remaining = left_to_do
            wl.status = 'running'
            #print wl.name,"is running with",wl.remaining,"left to do"
            asession.commit()
            next_time_tick = True
            break
        else: ## left to do is negative
            wl.remaining = 0
            capacity = -left_to_do
            #print wl.name,"is finished"
            wl.status = 'finished'
            asession.commit()
            
    if next_time_tick:
        continue    











# In[ ]:




# In[ ]:



