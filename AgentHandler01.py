from window_Util import *   
from math import *   
Number_of_Agents=config['Number_of_Agents']
Number_of_SAgents= config['Number_of_SAgents']
Number_of_TAgents=len(truck_resting)
Agents = []
Conveyor_Agents=[]
Sorting_Agents=[]
Truck_Agents=[]
All_Agents=[]
random_intersection_flag=config['random_intersection_flag']
epsilon=config['epsilon']
SBIG=config['SBIG']



# Used for Initialising our agents of rack/truck/sorting
def init_agents():
 
    for _ in range(Number_of_Agents):
        nAgent=Agent(0,n,m)
        nAgent.CurRack=str((random.randint(0,m-1), random.randint(0,n-1), random.randint(0, 4), random.randint(0, 4)))
        nAgent.position=numofrack[nAgent.CurRack]
        Agents.append(nAgent)
        All_Agents.append(nAgent)

    for _ in range(Number_of_SAgents):
        nAgent=Agent(2,n,m)
        nAgent.color=colors.PALEGREEN
        # while 1:
        sorting_random=(random.randint(0,2*sorting_n-2),random.randint(0,2*sorting_m-2))

        nAgent.position=numofdump[str(sorting_random)]
        All_Agents.append(nAgent)
        Sorting_Agents.append(nAgent)
        
    for i in range(Number_of_TAgents):
        nAgent=Agent(1,n,m)
        nAgent.truck_rest=i
        nAgent.position=truck_resting[i]
        All_Agents.append(nAgent)
        Truck_Agents.append(nAgent)

# Get the nearest agent from the rack given

def get_Agent(rack_pos):
    mindis = 99999999999999999
    for agent in Agents:
        d = ManhattanDistance(rack_pos, agent.position)
        if agent.Wait == True and mindis > d and agent.charge > 20:  # 10*agent.charge>=d:TODO: change to charge
            mindis = d

    for i in range(len(Agents)):
        if Agents[i].Wait == True:
            if mindis == ManhattanDistance(rack_pos, Agents[i].position) and Agents[i].charge > 20:
                return i
    return -1


def get_SAgent(rack_pos):
    mindis = 99999999999999999
    for agent in Sorting_Agents:
        if agent.Wait == True and mindis > ManhattanDistance(rack_pos, agent.position):
            mindis = ManhattanDistance(rack_pos, agent.position)

    for i in range(len(Sorting_Agents)):
        if Sorting_Agents[i].Wait == True:
            if mindis == ManhattanDistance(rack_pos, Sorting_Agents[i].position):
                return i+Number_of_Agents
    return -1


def get_TAgent():
    for i in range(len(Truck_Agents)):
        if Truck_Agents[i].Wait == True:
            return i + Number_of_Agents + Number_of_SAgents
    return -1

def robo_rack_entry(agent_id):
    # find nearest intersection 
    First=nearest_intersection((int(All_Agents[agent_id].position[0]),int(All_Agents[agent_id].position[1])))                
    # go in back direction from intersection
    D=Matrix.grid[int(All_Agents[agent_id].position[0])][int(All_Agents[agent_id].position[1])]
    if len(D)>2:
        print('dikkat h bhai')
        input()
    D=D[1]
    revD=revdir[D] 
    pos=(int(All_Agents[agent_id].position[0]),int(All_Agents[agent_id].position[1]))
    while pos not in Intersections:
        pos=(pos[0]+revD[0],pos[1]+revD[1])
    Sec=pos
    # print("Firs,sec",First,Sec)
    Road=Roads_Grid[(Sec,First)]
    safe=True
    for agent in Road:
        if agent.direction=="rest":
            continue
        if abs(agent.position[0]-All_Agents[agent_id].position[0])+abs(agent.position[1]-All_Agents[agent_id].position[1])<3:
            safe=False
              
    if safe==False:
        return -1,First       
    index=0
    for agent in Road:
        if D==1:
            if agent.position[1]<=All_Agents[agent_id].position[1]:
                break
        elif D==2:
            if agent.position[1]>=All_Agents[agent_id].position[1]:
                break
        elif D==3:
            if agent.position[0]>=All_Agents[agent_id].position[0]:
                break
        elif D==4:
            if agent.position[0]<=All_Agents[agent_id].position[0]:
                break
        index+=1
    
    Roads_Grid[(Sec,First)].insert(index,All_Agents[agent_id])
    return 1,First

def is_overshoot(D,agent, GG):
    flag=0
    if D==1 and agent.position[1]<=GG[1]:
        flag=1
    elif D==2 and agent.position[1]>=GG[1]:
        flag=1
    elif D==3 and agent.position[0]>=GG[0]:
        flag=1
    elif D==4 and agent.position[0]<=GG[0]:
        flag=1

    return flag

def motion_to_rest(agent):
    agent.Wait=True
    agent.Index=-1
    agent.goalindex=-1
    agent.direction="rest"
    agent.goals=[]
    agent.nearestgoals=[]
    agent.size=2

def get_direction(a,b):
    x1,y1=a
    x2,y2=b
    
    if x1==x2:
        if y1<y2:
            return 2
        else:
            return 1
    elif y1==y2:
        if x1<x2:
            return 3
        else:
            return 4
    

def intT(A):
    B=(int(A[0]),int(A[1]))
    return B

def change_signal():
    for I in Intersections:
        index=0
        for j in range(1,len(Matrix.grid[I[0]][I[1]])):
            if j==0:
                continue
            D=Matrix.grid[I[0]][I[1]][j]
            if Intersection_Gateway[I][D]==1:
                index=j
                break
        if index==len(Matrix.grid[I[0]][I[1]])-1:
            index=0

        nxtD=Matrix.grid[I[0]][I[1]][index+1]
        Intersection_Gateway[I]=[0]*5
        Intersection_Gateway[I][nxtD]=1
        Intersection_Timeout[I]=50

def traffic_intersection(P,D):
    Pos=intT(P)
    if Intersection_Gateway[Pos][D]==1:
        return True,Intersection_Timeout[Pos]
    
    return False,-1

def update_intersection():
    for I in Intersections:
        if Intersection_Timeout[I]==0:
            change_signal()
        else:
            Intersection_Timeout[I]-=1



def handle_rack_agents(key,coloring):
    current_items=0
    orders_completed_now=0
    # update_intersection()
    for Road in Roads_lr:
        if Roads_lr[Road]==-1:      #Road in Reverse Direction
            continue
        removal,remover=[],[]
        for i in range(len(Roads_Grid[Road])): 
            agent=Roads_Grid[Road][i]
            
            if agent.type==0:
                agent.charge-=0.05
       #     print(Road,agent.ind,len(Roads_Grid[Road]))
            # if agent.type==1:
            #     print("WOW")
            #     input()
            if i==len(Roads_Grid[Road])-1:
                next_agent=Roads_Grid[Road][i]
            else:
                next_agent=Roads_Grid[Road][i+1]
            k=intT(agent.path[agent.Index])
         #   pygame.draw.circle(screen,colors.GREEN1,(k[0],k[1]),5)
            D=Matrix.grid[int(Roads_Grid[Road][i].position[0])][int(Roads_Grid[Road][i].position[1])]
            if len(D)>2:
                new_point=((agent.position[0]+k[0])/2,(agent.position[1]+k[1])/2) 
             #   D=Matrix.grid[int(new_point[0])][int(new_point[1])][1]
                print("WTH")
                print(agent.ind)
                print(agent.position,new_point,k)
                print(agent.path,agent.stopped)
                print(agent.Index,agent.CurRack)
                for i in range(1,100000000):
                    pygame.draw.circle(screen,(255,0,0),(int(agent.position[0]),int(agent.position[1])),2)
                    pygame.draw.circle(screen,(0,255,0),(int(k[0]),int(k[1])),5) 
                    pygame.display.flip()   
                input()
            else:
                try:
                    D=D[1]
                except:

                    print(agent.position)
                    print(agent.path)
                    print(k)
                    print(agent.Index)
                    print(agent.ind)
                    # for i in range(1,100000000):
                    #     pygame.draw.circle(screen,(255,0,0),(int(agent.position[0]),int(agent.position[1])),10)
                    #     pygame.display.flip()
                        
                    x=input()
            if agent.key_field==key:
                continue
            agent.key_field=key
            
            if agent.Index==0:
              #  print("potOOOO",agent.ind)
                flag=0
                # next_agent==agent or distance between agent and next_agent is greater than distance between agent and agent.valet
                if next_agent==agent or (abs(agent.position[0]-next_agent.position[0])+abs(agent.position[1]-next_agent.position[1]))>abs(agent.position[0]-agent.valet.position[0])+abs(agent.position[1]-agent.valet.position[1]):
                    if agent.v==0: # can improve upon this condition but will work fine till any bot does not malfunction and stop in between
                        # Reached the valet
                        flag=1
                    agent.update(agent.valet,D)
                else:
                    agent.update(next_agent,D)

                if flag:
                    agent.position=agent.valet.position
                    agent.Index-=1
                    agent.goalindex+=1
                    if agent.goalindex<len(agent.goals):
                        if agent.type==0:
                            if agent.goals[agent.goalindex]==[-2,-2]:
                                if agent.position in israck:
                                    remover.append((Road,agent))
                                logger.info('Order'+','+str(agent.order_id)+','+'Warehouse'+','+str(agent.ind)+','+'Bot Reached the Rack No. '+str(agent.goalindex))
                                agent.goalindex+=1        
                            elif agent.goals[agent.goalindex]==[-7,-7]:
                                if agent.position in israck:
                                    remover.append((Road,agent))
                                logger.info('Order'+','+str(agent.order_id)+','+'Warehouse'+','+str(agent.ind)+','+'Bot Reached the Desired Rack.')
                                agent.goalindex+=1    
                                
                            elif agent.goals[agent.goalindex]==[-14,-14]:
                                agent.human_delay=25
                                logger.info('Order'+','+str(agent.order_id)+','+'Warehouse'+','+str(agent.ind)+','+'Bot Reached the Human Counter with few items.')
                                doc=order_db.find_one({"_id":agent.order_id})
                                quantity=doc["ordered_quantity"]
                                progress=doc["order_progress"]
                                human_ct=doc["human_counter"]
                                total_items_carrying=0
                                if SBIG:
                                    for rack in agent.items_carrying:
                                        for items in agent.items_carrying[rack]:
                                            # print(items)
                                            total_items_carrying+=items[1]  
                                else:
                                    for items in agent.items_carrying:
                                        total_items_carrying+=items[1]
                                current_items=total_items_carrying
                                if total_items_carrying+progress==quantity:
                                    orders_completed_now+=1
                                    logger.info('Finished Order'+','+str(agent.order_id)+','+'Warehouse'+','+str(agent.ind)+','+'Order is completed.')
                                    conveyor_agent= Agent(1,n,m)
                                    conveyor_agent.position=HCtoConveyor[human_ct]
                                    conveyor_agent.order_id=agent.order_id
                                    if human_ct<m: 
                                        conveyor_agent.path=HCtoSorting[str((0,human_ct))].copy()
                                    else:
                                        conveyor_agent.path=HCtoSorting[str((1,human_ct-m))].copy()
                                    conveyor_agent.path.reverse()
                                    conveyor_agent.Index=len(conveyor_agent.path)
                                    Conveyor_Agents.append(conveyor_agent)

                                order_db.update_one({"_id":agent.order_id},{"$inc":{"order_progress":total_items_carrying}})                            
                                agent.goalindex+=1
                                agent.Index=-1
                            elif  agent.goals[agent.goalindex]==[-21,-21]:
                                if agent.position in israck:
                                    remover.append((Road,agent))
                                logger.info('Event'+','+'-'+','+'Warehouse'+','+str(agent.ind)+','+'Kept the Rack back which it was carrying.')
                                motion_to_rest(agent)
                                rack_available[agent.CurRack]=1
                                agent.color = colors.YELLOW1
                                remove=[]
                                for colo in range(len(coloring)):
                                    if coloring[colo][2]==agent:
                                        remove.append(coloring[colo])
                                for i in remove:
                                    coloring.remove(i)
                                                            
                            elif agent.goals[agent.goalindex]==[-11,-11]:
                                logger.info('Charging'+','+'-'+','+'Warehouse'+','+str(agent.ind)+','+'Bot Reached the Charging Station.')
                                motion_to_rest(agent)
                                agent.Wait=False
                              #  remover.append((Road,agent))

                            elif agent.goals[agent.goalindex]==[-200,-200]:
                                logger.info('Charging'+','+'-'+','+'Warehouse'+','+str(agent.ind)+','+'Bot Reached back to its Rack with full Charge.')
                                motion_to_rest(agent)
                                agent.color = colors.YELLOW1
                        
                        elif agent.type==1:
                            if agent.goals[agent.goalindex]==[-7,-7]:
                                agent.goalindex+=1
                                add_item(agent.items_carrying[0],agent.items_carrying[1],agent.CurRack)
                                remover.append((Road,agent))
                                # logger.info('Truck Bot '+str(agent.ind)+': Reached the Desired Rack with item type'+str(agent.items_carrying[0])+' with quant '+str(agent.items_carrying[1]))
                                logger.info('Trucks in Warehouse'+','+'-'+','+'Truck Bot'+','+'-'+','+"Reached the Desired Rack with some new item type.")
                            elif  agent.goals[agent.goalindex]==[-14,-14]:
                                agent.path = []
                                rack_available[agent.CurRack]=1
                                agent.Wait = True   
                                agent.size=2
                                agent.direction="rest"  
                                agent.goals=[]
                                agent.nearestgoals=[]
                                agent.goalindex=0
                                agent.Index=-1
                                # remover.append((Road,agent))
                        elif agent.type==2:
                            if agent.goals[agent.goalindex]==[-7,-7]:
                                agent.goalindex+=1
                            elif  agent.goals[agent.goalindex]==[-14,-14]:
                                # logger.info("Sorting Bot dumped the order with Order ID: "+str(sagent.order_id)+" to it's dumping point")
                                logger.info('Sorting Order'+','+str(agent.order_id)+','+'Sorting Bot'+','+str(agent.ind)+','+"Bot placed the order to it's dumping point.")
                                agent.Wait=True       
                                agent.path=[]
                                agent.size=2
                                # sagent.color=colors.PALEGREEN
                                agent.direction="rest"
                                agent.goals=[]
                                agent.nearestgoals=[]
                                agent.goalindex=0
                                agent.Index=-1
                                remover.append((Road,agent))

            elif i==len(Roads_Grid[Road])-1:
                agent.unstop()
                dist_remaining=ManhattanDistance(agent.position,k)
                passing=True
                if dist_remaining<8:    # Booking Check
                    if Intersection_Booking[k] in [-1,agent.ind]:
                        Intersection_Booking[k]=agent.ind
                    else:
                        passing=False
            #    print("GOOOOOO",passing,agent.ind)
                if passing:
                    agent.update(None,D)
                else:
                    agent.update(Intersection_Bot[k],D)
                
                dist_r=ManhattanDistance(agent.position,k)
             #   print("Going",dist_r,k)
             # TODO : Try to adjust speed as bots enter intersection
                if dist_r<=1.6 and passing:
    
                    removal.append(Road)
                    agent.position=k
                    agent.Index-=1
            else:
                # if distance between k and agent.position is less than 5
             #   print("ROxOOOO",agent.ind)
                if ManhattanDistance(agent.position,k)<=5:
                    agent.stop()
                else:
                    agent.update(next_agent,D)
        
        for r in removal:   
            Roads_Grid[r].pop()
        for r,a in remover:
            Roads_Grid[r].remove(a)

    for I in Intersections:
        if Intersection_Booking[I]==-1:
            continue
        print("HEY")
        agent=All_Agents[Intersection_Booking[I]]
     #   print("HERE ")
        if agent.key_field==key:
            print("WWW",agent.key_field)
            continue
        nextI=intT(agent.path[agent.Index])
        #    raod joining I and nextI
        Road=(I,nextI)
     #   print("ROADD",Road,agent.Index)
        if Roads_Grid[Road]==[] or ManhattanDistance(I,Roads_Grid[Road][0].position)>2.5: # TODO: can improve this 2.5 later
            # move 1 pixel in direction of nextI
            x_gap=nextI[0]-I[0]
            y_gap=nextI[1]-I[1]
            if x_gap==0:
                # move in y
               # print(agent.type)
                agent.position=(I[0],I[1]+y_gap/abs(y_gap))
            elif y_gap==0:
                # move in x
                agent.position=(I[0]+x_gap/abs(x_gap),I[1])
            agent.v=0.1
            Roads_Grid[Road]=[agent]+Roads_Grid[Road]
            Intersection_Booking[I]=-1
            agent.key_field=key
        else:
            print("wrong")
    
    dupl=[] 
    totlset=[]

    for i in range(len(All_Agents)):
        
        agent=All_Agents[i]
      #  print(agent.type)
        if agent.direction=="motion":
            pt=int(agent.position[0]),int(agent.position[1])
            if pt in totlset:
                dupl.append(pt)
            totlset.append(pt)
            
        # if agent is at a rack

        if i==1:
            # for points in agent.path:
            #     pygame.draw.circle(screen,colors.RED1,(int(points[0]),int(points[1])),2)
            pygame.draw.circle(screen,(255,0,0),(int(agent.position[0]),int(agent.position[1])),5)
            #print(agent.charge,agent.cStation,agent.Index)
         #   print(agent.position,agent.path,agent.Index,agent.goalindex,agent.goals)
        elif agent.type==0:
            if agent.position in israck:
                pygame.draw.circle(screen, agent.color, (agent.position[0]+10,agent.position[1]),2)
            else: 
                pygame.draw.circle(screen, agent.color, agent.position, agent.size)
        elif agent.type==1:
            pygame.draw.circle(screen, agent.color, agent.position, agent.size)
        elif agent.type==2:
            pygame.draw.circle(screen, agent.color, agent.position, agent.size)  

        if agent.type==0 and agent.cStation!=-1 and agent.position==charging_loc[agent.cStation] and abs(agent.charge-agent.maxcharge)<=1:
            print("AL")
            charging_state[agent.cStation]=0
            agent.cStation=-1
            agent.color = colors.LIGHTBLUE1
            agent.size = 3
            agent.needcharge=False
            agent.goals=[numofrack[agent.CurRack],[-200,-200]]
            agent.nearestgoals=[]
            agent.goalindex=0
            agent.direction="motion"
          #  agent.Index=-1
            for xx in range(len(agent.goals)):
                if agent.goals[xx][0]<0:
                    agent.nearestgoals.append(agent.goals[xx])
                    continue
                togoal=agent.goals[xx]
                nearestIntersec=nearest_intersection(togoal,rev=True) 
                agent.nearestgoals.append(nearestIntersec)

        if agent.direction=='motion' and agent.Index==-1: #Order assigned hua h bhai ko naya naya --> nope               
         #   print("BOAT",agent.ind)
            print("BL")
            Source=nearest_intersection(intT(agent.position))
            if agent.position in israck or agent.position in isdump:
                allowed,First=robo_rack_entry(i)
                if allowed==-1:
                    continue
                else:
                    Source=First

            # else:

            # else:
            #     # append in road
            #     #if agent.type!=0:
            #     Previous=nearest_intersection(intT(agent.position),rev=True)
            #     # APpend n Road
            #     if agent not in Roads_Grid[(Previous,Source)]:
            #         Roads_Grid[(Previous,Source)]=[agent]+Roads_Grid[(Previous,Source)]
            
            togoal=agent.goals[agent.goalindex]
            Ghost=Agent(0,n,m)
            Ghost.position=togoal
            agent.valet=Ghost
            nearestIntersec=agent.nearestgoals[agent.goalindex]
            nAgent = Search(Source,nearestIntersec)
            if nearestIntersec==None:
                print(togoal,"F")
                for i in range(1000000):
                    pygame.draw.circle(screen,colors.TEAL,(int(agent.position[0]),int(agent.position[1])),5)
                    pygame.draw.circle(screen,colors.TEAL,(int(Source[0]),int(Source[1])),5)
                    pygame.draw.circle(screen,colors.TEAL,(int(togoal[0]),int(togoal[1])),5)                     
                    pygame.display.flip()
                x=input()
                # continue
            nAgent.AStar(agent.theta,Agents,Truck_Agents,Sorting_Agents,0)
            nextIntersec_path=nAgent.getPathLong()
            agent.path=nextIntersec_path
            if agent.path==[]:
                print("FF")
                for i in range(1,100000000):
                    pygame.draw.circle(screen,colors.GOLDENROD,Source,4)
                    pygame.draw.circle(screen,colors.GOLDENROD,nearestIntersec,4)
                    pygame.display.flip() 
                x=input()
            last=nearest_intersection(togoal)
            agent.path.append(last)
            agent.path.reverse()
            agent.Index=len(nextIntersec_path)-1

        if agent.type==0 and agent.Index <= -1 and agent.direction=="rest":
            
            # Increasing charge
            if agent.needcharge==True:
                agent.color = colors.GREEN
                agent.charge+=.1
            # Assigning agent a charging station if charge is low
            if agent.charge<20 and agent.needcharge == False and agent.cStation==-1:
                charge_ind,charge_box=get_charging()
                if charge_box==-1:
                    continue
                print("CL")
                agent.color = colors.LIGHTBLUE1
                agent.cStation=charge_ind
                agent.needcharge=True
                agent.direction="motion"
                agent.goals=[charge_box,[-11,-11]]
                agent.nearestgoals=[]
                agent.goalindex=0
                for xx in range(len(agent.goals)):
                    if agent.goals[xx][0]<0:
                        agent.nearestgoals.append(agent.goals[xx])
                        continue
                    togoal=agent.goals[xx]
                    nearestIntersec=nearest_intersection(togoal,rev=True) 
                    agent.nearestgoals.append(nearestIntersec)

                agent.Wait = False
    return current_items,orders_completed_now
            
            














