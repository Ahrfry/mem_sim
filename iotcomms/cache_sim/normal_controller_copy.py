import sys
sys.path.insert(0, '../app_gen')

from app_gen import Node , APP
from collections import OrderedDict
import string
import random
import numpy as np
import graphviz
import json

def get_prime(start):
    
    end = start + 25
    
    for i in range(start, end+1):
        if i>1:
            for j in range(2,i):
                if(i % j==0):
                    break
            else:
                return i

class HashNode:
 
    # initialising capacity
    def __init__(self ,  topic):
        self.valid = False
        self.topic = topic
        self.probe_count = 0

class Cache:
 
    # initialising capacity
    def __init__(self, capacity: int , type , name):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.cache_type = type
        self.cache_name = name
        
        print("Cache Type " , type)
        for i in range(capacity):
            self.cache[i] = Node("" , "", None)
    #function to make a reference to to the Topic Hash
    #if not found, return -1
    #else return the node
    
    def get(self, key):
        #print("ENTERED HASH GET " , key , " type " , self.cache_type)
        if self.cache_type != "FLAT":
            #print("Going to LRU GET " , key , " type " , self.cache_type)
            return self.lru_get(key)
        
        else:
            #print("Going to flat GET")
            return self.flat_get(key)
    
    def flat_get(self, key):
        #print("ENTERED flat GET")
        if key not in self.cache:
            #print("FLAT miss " , key , " topic " , self.cache[key].topic)
            return [0 , None]
        
        else:
            #print("FLAT hit " , key, " topic " , self.cache[key].topic)
            return [2 , key]    
    
    def lru_get(self, key):
        #print("LRU GET KEY " , key , " cache type ", self.cache_name)
        if key not in self.cache:
            
            return False
        else:
            
            self.cache.move_to_end(key)
            return True    
    
    
    def put(self, key: int, value: Node) -> None:
         
        self.cache[key] = value
        #print("put key " , key , " topic " , value.topic)
        
        if self.cache_type != "FLAT": 
            self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            
            node = self.cache.popitem(last = False)
            #print("Popping ", node[1])
            return node[1]
        else:
            return None    
        
class CacheController:
    def __init__(self, dev_cache_capacity, area_cache_capacity, dev_cache_type, area_cache_type, hash_multiplier):
        self.miss_dict = ["cache miss" , "cache miss conflict"]
        self.controller_type = dev_cache_type
        self.dev_cache_capacity = dev_cache_capacity
        self.area_cache_capacity = area_cache_capacity
        self.hash_multiplier = hash_multiplier
        self.ram_hash_multiplier = 100
        self.window_size = 1000
        self.window_count = 0
        self.epoch_size = 2^31
        self.epoch = 0
        self.color = 0
        self.probe = 10
        self.caches = {}
        self.caches["dev"] = Cache(dev_cache_capacity , dev_cache_type , "dev") 
        self.caches["area"] = Cache(area_cache_capacity , area_cache_type , "area")
        self.hash = {}
        self.hash["dev"] = {}
        self.hash["area"] = {}
        self.hash["ram"] = {}
        self.hash_capacity = {}
        self.hash_capacity["dev"] = get_prime(int(dev_cache_capacity*self.hash_multiplier))
        self.hash_capacity["area"] = get_prime(int(area_cache_capacity*self.hash_multiplier))
        self.hash_capacity["ram"] = get_prime(int(area_cache_capacity*self.ram_hash_multiplier))
        print("Dev hash Size ", self.hash_capacity["dev"], " Area hash Size ", self.hash_capacity["area"], " RAM Hash Size ", self.hash_capacity["ram"])
        self.stats = {}
        self.conflicts = {}
        self.stats["dev"] = []
        self.stats["dev"].append({"cache miss":0 , "cache miss conflict":0})
        self.stats["area"] = []
        
        for i in range(self.hash_capacity["dev"]):
            self.hash["dev"][i] = HashNode("")

        for i in range(self.hash_capacity["area"]):
            self.hash["area"][i] = HashNode("")
        
        

        for depth in range(6):
            self.stats["area"].append({"cache miss":0 , "cache miss conflict":0})
            self.stats["area"][depth]["cache miss"] = 0
            self.stats["area"][depth]["cache miss conflict"] = 0
    
    def update_window(self):
        self.window_count = self.window_count + 1
        if self.window_count > self.window_size:
            self.window_size = 0
            self.epoch = self.epoch + 1
            if self.epoch > self.epoch_size:
                self.epoch = 0
                if self.color == 0:
                    self.color = 1
                else:
                    self.color = 0        

    def get(self, key , topic , hash_type):
        topicz = topic
        if self.controller_type != "LRUQUAD" and self.controller_type != "LRUQUAD":
            #print("HASH GET , " ,  hash_type , " topic ", topic, " key " , key, " controller type ", self.controller_type)
            if self.hash[hash_type][key].valid == False:
                #print("hash miss " , hash_type)
                return [0 , key]
            elif self.hash[hash_type][key].topic != topic:
                #print("hash conf " , hash_type)
                return [1 , key]
            else:
                #print("HASH GET HIT, " ,  hash_type , " topic ", topicz, " key " , key)
                if self.caches[hash_type].get(topicz):
                    #print("Cache Hit " , hash_type , " topic ", topic)
                    return [2 , key]
                else:
                    #print("Hash Hit Cache Miss" , hash_type , " topic ", topic)
                    return [0 , key]
        else:
            
            max_probbed = key
            if self.hash[hash_type][key].valid == False:
                #print("hash miss 1 invalid" , key)
                return [0, key]
            else:
                #print("START PROBBING")    
                key2 = (key % (self.hash_capacity[hash_type] - 2))
                for i in range(self.probe):
                    if self.hash[hash_type][key2].valid == False:
                        #print("hash miss 2 invalid")
                        return [0 , key2]
                    elif self.hash[hash_type][key2].topic != topic:
                        key2 = (key + i*key2) % self.hash_capacity[hash_type]   
                        if self.controller_type == "LRUQUADD":
                            self.hash[hash_type][key2].probe_count = self.hash[hash_type][key2].probe_count + 1 
                            print("GET PROBING key " , key, " key2 " , key2 , " prob count ", self.hash[hash_type][key2].probe_count)
                            if self.hash[hash_type][max_probbed].probe_count < self.hash[hash_type][key2].probe_count:
                                max_probbed = key2
                        else:
                            max_probbed = key2        
                    elif self.hash[hash_type][key2].topic == topic:
                        self.hash[hash_type][key2].probe_count = 0
                        
                        if self.caches[hash_type].get(topic):
                            #print("Hash HIT Cache HIT")
                            return [2 , key2]
                        else:
                            #print("Hash HIT Cache MISS")
                            return [0 , key2]    
                #print("Probe Miss key " , max_probbed , self.hash[hash_type][key2].probe_count)    
                return [1 , max_probbed]

    def stats_update(self, stats_name, cache_type, index):
        
        self.stats[cache_type][index][stats_name] = self.stats[cache_type][index][stats_name] + 1
        
    
    
    
    
    def FE2HASH(self , topic):
        
       
        areas = topic.split('/')
        areas.pop()
        areas.pop(0)
        #Check dev chache for topic
      
        
        if  self.controller_type != "FLAT":
            #check area cache for areas
            for depth , topic in enumerate(areas):
                topic_key = hash(topic) % self.hash_capacity["area"] 
        
                get_return = self.get(topic_key , topic , "area")
                                
                if get_return[0] < 2:
                   
                    self.stats_update(self.miss_dict[get_return[0]] , "area" , depth)
                    rnode = Node("" , topic , get_return[1])
                    rnode.valid = True
                    hash_node = HashNode(topic)
                    hash_node.valid = True
                   
                    self.hash["area"][get_return[1]] = hash_node
                    put_ret = self.caches["area"].put(topic , rnode)
                    #print("Calling get again " , topic_key, "topic " , topic , " depth " , depth, " valid ", self.hash["area"][get_return[1]].valid)
                    #n_ret = self.get(topic_key , topic , "area")
                   
                   
                    if put_ret:
                        
                        if put_ret.valid:
                            self.hash["area"][put_ret.hash_key].valid = False
        else:

            topic_key = hash(topic) % self.hash_capacity["area"]
            get_return = self.get(topic_key , topic , "area")
                                
            if get_return[0] < 2:
                
                self.stats_update(self.miss_dict[get_return[0]] , "area" , depth)
                rnode = Node("" , topic , get_return[1])
                rnode.valid = True
                hash_node = HashNode(topic)
                hash_node.valid = True
                
                self.hash["area"][get_return[1]] = hash_node
                put_ret = self.caches["area"].put(topic , rnode)
                #print("Calling get again " , topic_key, "topic " , topic , " depth " , depth, " valid ", self.hash["area"][get_return[1]].valid)
                #n_ret = self.get(topic_key , topic , "area")
                
                
                if put_ret:
                    
                    if put_ret.valid:
                        self.hash["area"][put_ret.hash_key].valid = False

        
    def print_stats(self):
        for cache , value in self.stats.items():
            for stat_type in value:
                print(cache , stat_type)


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

depth = 3

set_lam = 2
set_k = 1
tot = 0
def full_poisson():
    dist = []
    dist.append([2])
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
            temp.append(i+3)
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

dist = poisson_dev(dist, 50)




app = APP(dist , config["topic_size"])


dot = graphviz.Digraph(comment='Normal')
dot.graph_attr['rankdir'] = 'LR'

if config["display_graph"]:
    print_tree(app.root, dot)
    dot.render('test-output/gen_tree.gv', view=True) 



topic_indexes = []

for i in range(len(app.devices) -1):
    topic_indexes.append(i)

hash_m = 2
cache_size_dev = 2000
cache_size_dev_vazado = 4000
cache_size_area = 400
#flat_cache_controller = CacheController(cache_size_dev , cache_size_area, "FLAT" , "FLAT" , hash_m) 
lrum_cache_controller = CacheController(cache_size_dev , cache_size_area, "LRU" , "LRU", hash_m)



countif = 0
countelse = 0
total_messages = 10000





for i in range(total_messages):
    
    rand = random.randint(0 , 99)
    n_dev = len(app.devices) -1
    most_frequent = int(0.075*n_dev)
    
    if rand < 90:
        index = random.randint(0 , most_frequent)
        countif  = countif + 1
        
        #print("If index is " , index , " count " , count)
    else:
        countelse = countelse + 1
        index = random.randint(most_frequent +1 , n_dev -1)
        #print("Else avgcount " , count)
        
    topic = app.compose_topic(app.devices[index])
    #print(topic)
    #flat_cache_controller.FE2HASH(topic)
    
    lrum_cache_controller.FE2HASH(topic)
    

print(app.order_lvl_print())    
print("countif " , countif, " else ", countelse)

#print("LRU")
#lru_cache_controller.print_stats()
print("LRUM")
lrum_cache_controller.print_stats()


#for i , conf in cache_controller.conflicts.items():
#    print(len(conf))

print("Number of devices " , len(app.devices), " number of areas ", total_area)
