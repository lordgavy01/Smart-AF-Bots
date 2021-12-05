"""
Which rack has which item

total items in workshop, item type id in :{all the racks that have it}


Item - Item  type Id ,Item ID, Rack Numbers in which it is stored
 
Gen_order():
  rand item id

Call_Truck():
    for item in type of items:
        d=rand_quantity()

"""
import uuid
import re
import time
import collections
from Map_Simul import *
import random
random.seed(2500)
import numpy as np
import logging
# def generate_order():
#     item = rand() % num_of_items
#     quant = rand() % 10
#     return (item, quant)

import pymongo
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)

item_types_in_db = set()

db = connection['Warehouse']
collection = db["big_database"]
order_db = db["order_db"]
order_history = db["order_history"]

order_db.drop()
collection.drop()

type_of_items = 5
max_order_limit = 5

# Creating Log File
logging.basicConfig(filename="Warehouse.log",
                    format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def assign_rack(orders):
  racks_dict={}
  for order in orders:
    docker=collection.find({"type":order[0]})
    target=order[1]
    lst=[]
    collection.update_one({"type":order[0]},{"$inc":{"quantity":-1*target}})   
    for nobj in list(docker):
        for obj in nobj['shelves']:
          shelf=obj['shelf']
          quant=obj['quantity']
          lst.append([quant,shelf])
        lst.sort(reverse=True)
        for j in range(len(lst)):
          if lst[j][0]>target:
            collection.update_one({"type":order[0],"shelves.shelf":lst[j][1]},{"$inc":{"shelves.$.quantity":-1*target}})  
            if lst[j][1] in racks_dict:
              racks_dict[lst[j][1]].append([order[0],target])
            else:
              racks_dict[lst[j][1]]=[[order[0],target]]
            target=0
          else:
            target-=lst[j][0]
            collection.update_one({"type":order[0]},{"$pull":{"shelves":{"shelf":lst[j][1], "quantity":lst[j][0]}}})
            if lst[j][1] in racks_dict:
              racks_dict[lst[j][1]].append([order[0],lst[j][0]])
            else:
              racks_dict[lst[j][1]]=[[order[0],lst[j][0]]]
          if target<=0:
            break
            
    if collection.find_one({"type":order[0]}): 
      if collection.find_one({"type":order[0]})["quantity"]==0:
        collection.delete_one({"type":order[0]})

  return racks_dict

def gen_a_order(): 
  global item_types_in_db
  num_types_ordered=random.randint(1,3)
  order=[]
  sum=0  
  types_chosen=random.sample(item_types_in_db,min(num_types_ordered,len(item_types_in_db)))
  for type in types_chosen:
    if collection.find_one({"type":type}):
      quant=collection.find_one({"type":type})["quantity"]
      low=1
      high=min(max_order_limit,quant)
      if low>high:
        continue
      order.append([type,random.randint(low,high)])
      sum+=order[-1][1]
      
  racks=assign_rack(order)
  
  human_counter= random.randint(0,2*m-1)

  order_id=str(uuid.uuid4())
  if len(order)==0:
    return "Nothing"
  sorting_random=(random.randint(0,2*sorting_n-1),random.randint(0,2*sorting_m-1))
  # logger.info('New Order is Placed with Order ID: '+str(order_id)+' which consists of '+str(order))
  logger.info('New Order'+','+str(order_id)+','+'-'+','+'-'+','+'New Order is Placed.')
  order_db.insert_one({"_id":order_id,"order_progress":0,"ordered_quantity":sum,"Target_Racks":racks,"human_counter":human_counter})  
  order_history.insert_one({"_id":order_id,"ordered":order,"address":sorting_random})  
  return (racks,human_counter,order_id)  




def add_items(count):
  global item_types_in_db
  for _ in range(count):
    type=random.randint(0,type_of_items)
    item_types_in_db.add(type)
    quantity=random.randint(1,3)
    shelf=str((random.randint(0, n-1), random.randint(0,m-1), random.randint(0, 4), random.randint(0, 4)))
    if collection.find_one({"type":type}):
      collection.update_one({"type":type},{"$inc":{"quantity":quantity}})
      if collection.find_one({"type":type, "shelves":{"$elemMatch":{"shelf":shelf}}}):
        collection.update_one({"type":type,"shelves.shelf":shelf},{"$inc":{"shelves.$.quantity":quantity}})
      else:
        collection.update_one({"type":type},{"$push":{"shelves":{"shelf":shelf, "quantity":quantity}}}) 
    else:
      collection.insert_one({"type":type, "quantity":quantity, "shelves":[{"shelf":shelf, "quantity":quantity}]})
  return item_types_in_db

def add_item(type, quantity, shelf):
    global item_types_in_db
    item_types_in_db.add(type)
    if collection.find_one({"type": type}):
        collection.update_one({"type": type}, {"$inc": {"quantity": quantity}})
        if collection.find_one({"type": type, "shelves": {"$elemMatch": {"shelf": shelf}}}):
            collection.update_one({"type": type, "shelves.shelf": shelf}, {
                                  "$inc": {"shelves.$.quantity": quantity}})
        else:
            collection.update_one(
                {"type": type}, {"$push": {"shelves": {"shelf": shelf, "quantity": quantity}}})
    else:
        collection.insert_one({"type": type, "quantity": quantity, "shelves": [
                              {"shelf": shelf, "quantity": quantity}]})


add_items(75)
