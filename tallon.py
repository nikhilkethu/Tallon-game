import numpy as np
import utils
import mdptoolbox
import config

from utils import Directions

class Tallon():

    def __init__(seeself, arena):

        
        seeself.gameWorld = arena
        seeself.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        seeself.move = [0,1,2,3]

    def makeMove(seeself):
        
        try:
            myplace = seeself.gameWorld.getTallonLocation()
            correctpoint = utils.pickRandomPose(myplace.x,myplace.y)
           
            P,R = seeself.probability()
           
            mdptoolbox.util.check(P,R)
 
            bmp3 = mdptoolbox.mdp.ValueIteration(P,R,0.99)
            bmp3.run()
            
           
            print('The coming  Policy :\n', bmp3.policy)
    
            caraterposition = lambda x: np.ravel_multi_index(x, (10,10))
        
            current_tallon = int(caraterposition((myplace.y,myplace.x)))
            print("Tallon's position  in the grid : ",current_tallon)
            
            if int(bmp3.policy[current_tallon]) == seeself.move[0]:
                print(" moves south")
                return Directions.SOUTH
            if int(bmp3.policy[current_tallon]) == seeself.move[1]:
                print(" moves north")
                return Directions.NORTH
            if int(bmp3.policy[current_tallon]) == seeself.move[2]:
                print(" moves east")
                return Directions.EAST
            if int(bmp3.policy[current_tallon]) ==seeself.move[3]:
                print("moves west")
                return Directions.WEST
               

        except Exception as e:
            print("searching...")
            if correctpoint.x > myplace.x:
                return Directions.EAST
            if correctpoint.x < myplace.x:
                return Directions.WEST
            
            if correctpoint.y > myplace.y:
                return Directions.NORTH
            if correctpoint.y < myplace.y:
                return Directions.SOUTH
            print(e)
        
        
        
    def probability(seeself):
        grid_size = (config.worldBreadth, config.worldLength)
       
        
        winesbous = seeself.gameWorld.getBonusLocation()
        enemiesahead= seeself.gameWorld.getMeanieLocation()
        noofpits = seeself.gameWorld.getPitsLocation()
        gridpoints = [(0,0),(0,10),(10,0),(10,10)]
        bounusreg= 1.0
        enemiereg= -1.0
        pitreg= -1.0
        empreg = -0.04
        acttallon=(.025, .025, config.directionProbability, 0.)     
          
        nosta = grid_size[0] * grid_size[1]
        num_actions = 4
        Pr = np.zeros((num_actions, nosta, nosta))
        Re = np.zeros((nosta, num_actions))
        try:
            myplace = seeself.gameWorld.getTallonLocation()
            caraterposition = lambda x: np.ravel_multi_index(x, (10,10))
            tallon_current = caraterposition((myplace.y,myplace.x))
            allpitsloc = lambda x: np.ravel_multi_index(x,(10,10))
            allmeaniesloc = lambda x: np.ravel_multi_index(x,(10,10))
            allbonusloc = lambda x: np.ravel_multi_index(x,(10,10))
            bonlog=[]
            pits_loc=[]
            meanies_loc=[] 
          
           
            for h in range(len(winesbous)):
                bonlog.append(allbonusloc((winesbous[h].y,winesbous[h].x)))
                nearbonus = min( bonlog,key=lambda x:abs(x- tallon_current))
                nearbonus = str(nearbonus)
                nearbonus = (int(nearbonus[0]),int(nearbonus[1])) if (len(nearbonus)>1) else (0,int(nearbonus))
                nearestbonus = nearbonus
                
            for k in range(len(enemiesahead)):
                meanies_loc.append( allmeaniesloc((enemiesahead[k].y,enemiesahead[k].x)))
                nearenemie = min( meanies_loc,key=lambda x:abs(x- tallon_current))
                nearenemie = str(nearenemie)
                nearenemie = (int(nearenemie[0]),int(nearenemie[1])) if (len(nearenemie)>1) else (0,int(nearenemie))
                nearestmeanie = nearenemie
              
            for p in range(len(noofpits)):
                pits_loc.append(allpitsloc((noofpits[p].y,noofpits[p].x)))
                nearpit = min(pits_loc,key=lambda x:abs(x- tallon_current))
                nearpit = str(nearpit)
                nearpit  = (int(nearpit[0]),int(nearpit[1])) if(len(nearpit)>1) else (0,int(nearpit))
                nearestpit = nearpit
                
            
            to_1d = lambda x: np.ravel_multi_index(x, grid_size)
            
            def itsbonus(cell):
                if cell in gridpoints:
                    return True
                try: 
                    to_1d(cell)
                except ValueError as e:
                    return True
                return False

           
            North = [acttallon[i] for i in (0, 1, 2, 3)]
            
            South = [acttallon[i] for i in (1, 0, 3, 2)]
          
            West = [acttallon[i] for i in (2, 3, 1, 0)]
           
            East = [acttallon[i] for i in (3, 2, 0, 1)]
            actions = [North, South, East, West]
            for i, a in enumerate(actions):
                actions[i] = {'North':a[2], 'South':a[3], 'West':a[0], 'East':a[1]}
                
            
            def tellprondrew(cell, jumpcell, someindex, a_prob):
                    
                if cell == nearestbonus:
                    Pr[someindex, to_1d(cell), to_1d(cell)] = 1.0
                    Re[to_1d(cell), someindex] = bounusreg
                    
                elif cell == nearestmeanie:
                    Pr[someindex, to_1d(cell), to_1d(cell)] = 1.0
                    Re[to_1d(cell), someindex] =enemiereg

                elif cell == nearestpit:  
                    Pr[someindex, to_1d(cell), to_1d(cell)] = 1.0
                    Re[to_1d(cell), someindex] = pitreg
                
                elif itsbonus(jumpcell):  
                    Pr[someindex, to_1d(cell), to_1d(cell)] += a_prob
                    Re[to_1d(cell), someindex] = empreg
                
                else:
                    Pr[someindex, to_1d(cell), to_1d(jumpcell)] = a_prob
                    Re[to_1d(cell), someindex] = empreg

            for someindex, action in enumerate(actions):
                for cell in np.ndindex(grid_size):


                     
                    jumpcell = (cell[0]-1, cell[1])
                    tellprondrew(cell, jumpcell, someindex, action['South'])
                    
                    jumpcell = (cell[0]+1, cell[1])
                    tellprondrew(cell, jumpcell, someindex, action['North'])

                     
                    jumpcell = (cell[0], cell[1]-1)
                    tellprondrew(cell, jumpcell, someindex, action['West'])
                   
                    jumpcell = (cell[0], cell[1]+1)
                    tellprondrew(cell, jumpcell, someindex, action['East'])
            
            return Pr, Re
        except Exception as e:
            print(e)