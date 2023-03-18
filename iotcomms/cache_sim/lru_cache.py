import sys
sys.path.insert(0, '../app_gen')

from app_gen import Node , APP
from collections import OrderedDict



class Cache:
 
    # initialising capacity
    def __init__(self, capacity: int , type , name):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.cache_type = type
        self.cache_name = name
        
        print("Cache Type " , type)
        for i in range(capacity):
            self.cache[i] = Node("" , "", None, None)
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