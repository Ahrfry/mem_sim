import sys
sys.path.insert(0, '../app_gen')

from app_gen import Node , APP
from vazado_cache_controller import VazadoCacheController , CacheController
import random
import numpy as np
import graphviz
import json
import matplotlib.pyplot as plt
import os
def print_tree(node , dot):
    if len(node.children) == 0:
        return
    dot.node(node.topic , node.topic)
    for child in node.children:
        dot.node(child.topic , child.topic)
        
        dot.edge(node.topic , child.topic)
        print_tree(child , dot)

f = open("../app_gen/config.json")
config = json.load(f)

depth = 2

set_lam = 70
set_k = 1
tot = 0
num_of_apps = 5
num_of_experiments = 5
k_lam_rate = 10

def full_poisson():
    dist = []
    dist.append([4])
    for i in range(depth):
        temp = np.random.poisson(lam=set_lam , size=set_k).tolist()
        set_k = np.sum(temp)
        set_lam = (set_k)/len(temp)
        dist.append(temp)
        
def regular(n_area):
    dist = []
    n_area = int(n_area)
    dist.append([n_area])
    for i in range(depth):
        temp = []
        for j in range(int(np.sum(dist[i]))):
            temp.append(i+5)
        dist.append(temp)

    return dist



def poisson_dev(dist, lam):
    k = np.sum(dist[len(dist)-1])
    
    
    devs = np.random.poisson(lam=lam , size=k)
    
    return [devs, k]








app = []
app_bucket = [] 
devs = None

for j in range(num_of_experiments):
    total_area = 0
    app = []
    total_devices = 0
    for i in range(num_of_apps):
        dist = regular((j+1)*k_lam_rate)
        for a in dist:
            total_area += np.sum(a)

        res = poisson_dev(dist, (set_lam - j*k_lam_rate))
        devs = res[0]
        list_dev = devs.tolist()
        total_devices = np.sum(list_dev)
        dist.append(list_dev)
        app.append(APP(dist , config["topic_size"]))

    app_bucket.append([total_area, set_lam - j*k_lam_rate , res[1], devs, app, total_devices])

#print(dist[len(dist)-1])



dot = graphviz.Digraph(comment='Normal')
dot.graph_attr['rankdir'] = 'LR'

if config["display_graph"]:
    print_tree(app[0].root, dot)
    dot.render('test-output/gen_tree.gv', view=True) 

for k in range(num_of_experiments):
    current_directory = os.getcwd()
    final_directory_name = 'experiment_'+str(k)
    final_directory = os.path.join(current_directory, final_directory_name)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    app = app_bucket[k][4]
    devs = app_bucket[k][3]
    
   

    hash_m = 1
    cache_size_dev = 5000
    cache_size_dev_vazado = 3800
    #cache_size_area = app_bucket[k][0]
    cache_size_area = 5407
    print("Number of Areas ", app_bucket[k][0], " lam ", app_bucket[k][1], " k ", app_bucket[k][2], 'devices', app_bucket[k][5])
    plt.hist(devs, bins=np.arange(devs.min(), devs.max()+1), align='left')
    #plt.show()
    plt.savefig(final_directory_name+'/'+'histogram.pdf')
    plt.clf()
    #quadd_cache_controller = VazadoCacheController(cache_size_dev_vazado , cache_size_area, "LRUQUADD" , "LRUQUADD", hash_m)
    flat_cache_controller = CacheController(cache_size_dev , cache_size_area, "FLAT" , "FLAT" , hash_m) 
    lrum_cache_controller = CacheController(cache_size_dev , cache_size_area, "LRU" , "LRU", hash_m)
    #quad_cache_controller = CacheController(cache_size_dev_vazado , cache_size_area, "LRUQUAD" , "LRUQUAD", hash_m)
    quadd_cache_controller = CacheController(cache_size_dev_vazado , cache_size_area, "LRUQUADD" , "LRUQUADD", hash_m)


    countif = 0
    countelse = 0
    total_messages = 1000000




    for i in range(total_messages):
        rand_app = random.randint(0 , 0)
        rand = random.randint(0 , 99)
        n_dev = len(app[rand_app].devices) -1
        most_frequent = int(0.99*n_dev)
        
        if rand < 99:
            index = random.randint(0 , most_frequent)
            countif  = countif + 1
            
            #print("If index is " , index , " count " , count)
        else:
            countelse = countelse + 1
            index = random.randint(most_frequent +1 , n_dev -1)
            #print("Else avgcount " , count)
    
        topic = app[rand_app].compose_topic(app[rand_app].devices[index])
        
        flat_cache_controller.FE2HASH(topic)
        lrum_cache_controller.FE2HASH(topic)
        #quad_cache_controller.FE2HASH(topic)
        quadd_cache_controller.FE2HASH(topic)



    print("FLAT")
    flat_cache_controller.print_stats()
    print("LRUM")
    lrum_cache_controller.print_stats()
    print("QUADD")
    quadd_cache_controller.print_stats()




#for i , conf in cache_controller.conflicts.items():
#    print(len(conf))

#print("Number of devices " , len(app.devices))
#print(app.order_lvl_print())
