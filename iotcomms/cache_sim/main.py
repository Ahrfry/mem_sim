import sys
sys.path.insert(0, '../app_gen')

from app_gen import Node , APP
from vazado_cache_controller import VazadoCacheController , CacheController
import random
import numpy as np
import graphviz
import json

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

depth = 4

set_lam = 2
set_k = 1
tot = 0

def full_poisson():
    dist = []
    dist.append([4])
    for i in range(depth):
        temp = np.random.poisson(lam=set_lam , size=set_k).tolist()
        set_k = np.sum(temp)
        set_lam = (set_k)/len(temp)
        dist.append(temp)
        
def regular():
    dist = []
    dist.append([5])
    for i in range(depth):
        temp = []
        for j in range(np.sum(dist[i])):
            temp.append(i+1)
        dist.append(temp)

    return dist



def poisson_dev(dist, lam):
    k = np.sum(dist[len(dist)-1])
    devs = np.random.poisson(lam=lam , size=k).tolist()
    dist.append(devs)
    return dist

dist = regular()

total_area = 0

for a in dist:
    total_area += np.sum(a)

dist = poisson_dev(dist, 2)

print("Number of Areas ", total_area)
app = APP(dist , config["topic_size"])


dot = graphviz.Digraph(comment='Normal')
dot.graph_attr['rankdir'] = 'LR'

if config["display_graph"]:
    print_tree(app.root, dot)
    dot.render('test-output/gen_tree.gv', view=True) 


topic_indexes = []

for i in range(len(app.devices) -1):
    topic_indexes.append(i)

hash_m = 1
cache_size_dev = 5000
cache_size_dev_vazado = 3800
cache_size_area = 9000

#quadd_cache_controller = VazadoCacheController(cache_size_dev_vazado , cache_size_area, "LRUQUADD" , "LRUQUADD", hash_m)
#flat_cache_controller = CacheController(cache_size_dev , cache_size_area, "FLAT" , "FLAT" , hash_m) 
#lrum_cache_controller = CacheController(cache_size_dev , cache_size_area, "LRU" , "LRU", hash_m)
#quad_cache_controller = CacheController(cache_size_dev_vazado , cache_size_area, "LRUQUAD" , "LRUQUAD", hash_m)
quadd_cache_controller = CacheController(cache_size_dev_vazado , cache_size_area, "LRUQUADD" , "LRUQUADD", hash_m)


countif = 0
countelse = 0
total_messages = 2

topic = app.compose_topic(app.devices[0])
       
quadd_cache_controller.FE2HASH(topic)

topic = app.compose_topic(app.devices[1])
       
quadd_cache_controller.FE2HASH(topic)


topic = app.compose_topic(app.devices[len(app.devices)-1])
       
quadd_cache_controller.FE2HASH(topic)

topic = app.compose_topic(app.devices[len(app.devices)-2])
       
quadd_cache_controller.FE2HASH(topic)

"""
for i in range(total_messages):
    
    for j in range(total_messages):
        topic = app.compose_topic(app.devices[0])
       
        quadd_cache_controller.FE2HASH(topic)


for i in range(total_messages):
    random.shuffle(topic_indexes)
    for dev_index in topic_indexes:
        topic = app.compose_topic(app.devices[dev_index])
        flat_cache_controller.FE2HASH(topic)
    
        lrum_cache_controller.FE2HASH(topic)
        quad_cache_controller.FE2HASH(topic)
        quadd_cache_controller.FE2HASH(topic)

for i in range(total_messages):
    
    rand = random.randint(0 , 99)
    n_dev = len(app.devices) -1
    most_frequent = int(0.9*n_dev)
    
    if rand < 99:
        index = random.randint(0 , most_frequent)
        countif  = countif + 1
        
        #print("If index is " , index , " count " , count)
    else:
        countelse = countelse + 1
        index = random.randint(most_frequent +1 , n_dev -1)
        #print("Else avgcount " , count)
        
    topic = app.compose_topic(app.devices[index])
    
    flat_cache_controller.FE2HASH(topic)
    lrum_cache_controller.FE2HASH(topic)
    quad_cache_controller.FE2HASH(topic)
    quadd_cache_controller.FE2HASH(topic)




print("LRUM")
lrum_cache_controller.print_stats()
print("QUAD")
quad_cache_controller.print_stats()
"""
print("QUADD")
quadd_cache_controller.print_stats()


#for i , conf in cache_controller.conflicts.items():
#    print(len(conf))

#print("Number of devices " , len(app.devices) ,  " size " , a3*a2)
print(app.order_lvl_print())
