import cherrypy
import os
#from dbschema import Base,Agents
from dbcherry import Workload,Agents,SAEnginePlugin,SATool
##courtesy http://www.defuze.org/archives/222-integrating-sqlalchemy-into-a-cherrypy-application.html
import random
from sqlalchemy import desc

#from dbsession import session

class HelloWorld:

    def index(self):
        # Let's link to another method here.
        document = 'We have an <a href="show_msg">important message guys</a> for you!'
        document += '<br>and <a href=here_my_rest> another link</a>'
        document += '<br>enter a <a href=give_info> new agent </a>'
        document += '<br>list <a href=leprecaun>the agents</a>'
        document += '<br><a href=tic_tac_toc?token=X> play tic tac toe</a>'
        return document
    
    index.exposed = True

    def show_msg(self):
        # Here's the important message!
        return "Hello world! I am here or there ?"
    show_msg.exposed = True
    
    def here_my_rest(self):
        return "this is new"
    here_my_rest.exposed = True
    
    def leprecaun(self):
        document ="<html>"
        document += "<img src=https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQyIrRjUlbgnl3DddUnDNqVfYCz_bzUy7VvaoPjSr8AEus4Op2Ezg>"
        agents = cherrypy.request.db.query(Agents).order_by(Agents.name).all()

        document +="""
<table border="1" style="width:100%">
   <tr>
    <th>Name</th>
    <th>Ip</th> 
    <th>Id</th>
   </tr>
"""
        for agent in agents:
            print agent.name,agent.ip,agent.id
            document +="<tr>"
            document +="<td>%s</td>"%agent.name
            document +="<td>%s</td>"%agent.ip
            document +="<td>%s</td>"%agent.id
            document +="</tr>"
            
        document += """   
</table>
"""
        
        document += "</html>"
        return document
    leprecaun.exposed = True
    
    
    def give_info(self):
        # Ask for the agents's name.
        return '''
            <form action="propagate_info" method="GET">
            Name of the agent<input type="text" name="name" /><br>
            IP of the agent<input type="text" name="ip" /><br>
            <input type="submit" />
            </form>'''
    give_info.exposed = True

    
    def all_agents(self, refresh=None,col=None,width=None,height=None):
        agents = cherrypy.request.db.query(Agents).order_by(Agents.name).all()
        col = int(col)
        refresh = int(refresh)
        if width:
            width=int(width)
        else:
            width = 400
        if height:
            height=int(height)
        else:
            height = 300
        document ="""
<html>
<meta http-equiv="refresh" content="%s">
<body>
<table border=1>
"""%( refresh )
        
        
        for i,agent in enumerate(agents):
            if divmod(i,col)[1]==0: document+="<tr>"
            document += '<td>%s<br><iframe  width="%s" height="%s"src="http://%s:8080/show_workload"></iframe></td>'%(agent.name,width,height,agent.ip)
            if divmod(i+1,col)[1]==0: document+="</tr>"
        document += """
</table>
</body>
</html>
"""
        return document
    all_agents.exposed = True
    
    def propagate_info(self, name=None, ip=None, workforce=None):
        # CherryPy passes all GET and POST variables as method parameters.
        # It doesn't make a difference where the variables come from, how
        # large their contents are, and so on.
        #
        # You can define default parameter values as usual. In this
        # example, the "name" parameter defaults to None so we can check
        # if a name was actually specified.
        if not name or not ip:
            return "wrong input"
        are_digits = all([bit.isdigit() for bit in ip.split(".")])
        #any([ not bit.isdigit() for bit in ip.split(".")]) 
        if ip.count(".") !=3 or not are_digits :
            return "IP is wrong"
        error_code = os.system('curl http://%s:8080/leprecaun --connect-timeout 2'% ip )
        if error_code !=0:
            return "not a real agent"
        
        exact_search = cherrypy.request.db.query(Agents).filter(Agents.name == name).filter(Agents.ip == ip).all()
        search = cherrypy.request.db.query(Agents).filter(Agents.name == name).all()

        msg =""
        
        ### if we know the agent then we do nothing
        if len(search):
            msg = "agent "+name+"already known"
        else:
            if not workforce:
                workforce = random.randint(3,10)
            ## add it to our db
            new_agent = Agents(name=name, ip=ip, workforce = workforce)
            
            cherrypy.request.db.add( new_agent)
            cherrypy.request.db.commit()
            ## get all our contact "except yourself"
            agents = cherrypy.request.db.query(Agents).all()
            # and send the new name:ip to everyone
            for agent in agents:
                #if agent.ip == cherrypy.server.socket_host:
                #    continue
                ## need to send the name:ip that we just got to the other
                propagation_msg = os.popen('curl -s "http://%s:8080/propagate_info?name=%s&ip=%s"'%(ip, agent.name, agent.ip)).read()
                msg += "send information to :"+ip+" about "+ agent.name +"<br>"
                msg += "&emsp;"+propagation_msg+"<br>"
        return msg

    
    propagate_info.exposed = True

    
    #def tic_tac_toe(self, c1=None, c2=None, c3=None, c4=None, c5=None, c6=None, c7=None, c8=None, c9=None, token=None):
    def tic_tac_toe(self, **params):
        token = params.get('token',None)
        
        ## what do we need in input
        # a table and it's content
        # what the the next token to play, or the last
        tokens = ['X','O']#,'A','B']
        game_size = int(params.get('game_size',3))
        callback = int(params.get('callback', 0))
        print "callback is",callback
        print params
        
        c =range( game_size*game_size )
        for row in range(game_size):
            for col in range(game_size):
                icell = row * game_size + col
                c[icell] = params.get('c%d'%(icell+1),None)
        print c
        print token
        #where to place the next token
        #only in the empty(None) cells
        empty_cells = []
        for i,cell in enumerate(c):
            if cell==None:
                # somewhere empty
                empty_cells.append( i )
        def table_content(c,highlight=None):
            msg = "<table border=1>"
            for row in range(game_size):
                msg += "<tr>"
                for col in range(game_size):
                    icell = row * game_size + col
                    if highlight and icell in highlight:
                        msg += "<td bgcolor=red>%s</td>"% c[ icell ]
                    else:
                        msg += "<td >%s</td>"% c[ icell ]
                msg += "</tr>"
            msg += "</table>"
            return msg
        
        #check whether the game is finished
        if len(empty_cells) == 0:
            msg = "there is no empty cell to play in. Start again, please.<br>"
            msg += table_content(c)
            msg += "click here to start again"
            return msg
        # pick at random (for starter)
        next_cell = random.choice( empty_cells)
        
        index_token = tokens.index( token )
        index_token += 1
        if index_token == len(tokens): index_token=0
        next_token = tokens[ index_token ]
        
        ## really play it
        c[next_cell]  = token
        
        #check if there is a win for the given token
        where_is_the_token = set([i for i,cell in enumerate(c) if cell==token])
        winning_conditions = [
        ##    [0,3,6],[1,4,7],[2,5,8], # colums
        ##    [0,1,2],[3,4,5],[6,7,8], # rows
        ##    [0,4,8],[2,4,6] # diagonals
            ]
        for row in range(game_size):
            winning = []
            for col in range(game_size):
                icell = row * game_size + col
                winning.append( icell )
            winning_conditions.append( winning )
        for col in range(game_size):
            winning = []
            for row in range( game_size ):
                icell = row * game_size + col
                winning.append( icell )
            winning_conditions.append( winning )
        diag1=[]
        diag2=[]
        for row in range(game_size):
            for col in range(game_size):
                icell = row * game_size + col
                if col == row:
                    diag1.append( icell )
                if col+row == game_size-1:
                    diag2.append( icell )
        winning_conditions.append( diag1 )
        winning_conditions.append( diag2 )
        
        for win in winning_conditions:
            if (set(win)&where_is_the_token) == set(win):
                ## we have a win
                msg = "We have a win %s for token %s at ip %s<br>"%(win, token, cherrypy.server.socket_host)
                msg += table_content(c, highlight=win)
                msg += "come play again with us, <a href=http://%s:8080/tic_tac_toe?token=%s>please.</a>"%( cherrypy.server.socket_host, next_token)
                return msg
        # pass it on to the next
        ## who's next
        agents = cherrypy.request.db.query(Agents).filter(Agents.ip != cherrypy.server.socket_host).order_by(Agents.name).all()
        ## find yourself in the list, and pick the next
        next_player = random.choice( agents )
        ## pass the table to the next
        "http://128.141.252.248:8080/tic_tac_toe?c1=X&c2=O&c3=X...&token=X"
        cell_string = "&".join(["c%d=%s"%(i+1, cell) for i,cell in enumerate(c) if cell])
        next_url = '"http://%s:8080/tic_tac_toe?%s&token=%s&game_size=%d&callback=%s"'%(next_player.ip, cell_string, next_token,game_size,callback) 
        next_url_auto = '"http://%s:8080/tic_tac_toe?%s&token=%s&game_size=%d&callback=%s"'%(next_player.ip, cell_string, next_token,game_size,1)
        if callback:
            msg = os.popen('curl -s %s'%(next_url)).read()
        else:
            msg = "This is the current table<br>"
            msg += table_content(c)
            msg +="click on <a href=%s>here for the next move</a>"% (next_url)
            msg +="click on <a href=%s>here for to leave them play the game</a>"% (next_url_auto)
        return msg
        
    tic_tac_toe.exposed = True    
    
    def add_info(self, name=None, ip=None, workforce=None):
      
        if not name or not ip:
            return "wrong input"
        are_digits = all([bit.isdigit() for bit in ip.split(".")])
        #any([ not bit.isdigit() for bit in ip.split(".")]) 
        if ip.count(".") !=3 or not are_digits :
            return "IP is wrong"
        if not workforce:
            workforce = random.randint(3,10)
            
        search = cherrypy.request.db.query(Agents).filter(Agents.name == name).all()
        if len(search)!=0:
            #we cannot add the agent
            for agent in search:
                agent.ip = ip
            msg="Modified the ip of "+name+" to "+ip
        else:
            new_agent = Agents(name=name, ip=ip, workforce=workforce)
            cherrypy.request.db.add( new_agent)
            msg="added the agent "+name+" with ip "+ip
        #cherrypy.request.db.commit()
        return msg
    
    add_info.exposed = True
    
    def push_workload(self,  **params): #A
        ### a third party (or any agent) injects some workload to a given agent
        ## get the workload from the passed parameters
        ## keep workload
        ## query agents for availability
        
        keep_it_for_yourself = int(params.get('keep_it_for_yourself',1))
        workload_name = params.get('workload',None)
        workload_CPUh = float(params.get('CPUh',0))
        if not workload_name or not workload_CPUh:
            return "no workload specified"

        if keep_it_for_yourself:
            new_load = Workload(name=workload_name, CPUh = workload_CPUh, status='next', remaining= workload_CPUh)
            cherrypy.request.db.add( new_load )
            cherrypy.request.db.commit()
            return "OK, workload registered"

        #agents = cherrypy.request.db.query(Agents).filter(Agents.ip != cherrypy.server.socket_host).all()
        agents = cherrypy.request.db.query(Agents).all()
        available_agents = []
        for agent in agents:
            ## query availability
            ## use the "query_workload" function of the other agent
            next_url = '"http://%s:8080/query_workload?"'%(agent.ip)
            msg = os.popen('curl -s %s'%(next_url)).read()
            if msg == 'N':
                continue
            elif msg == 'Y':
                available_agents.append( agent )
            elif msg == 'TOTO':
                pass
            else:
                pass
        
        if len(available_agents)==0:
            return "We are too busy, come back later, please."
        
        ## split this thing
        individual_CPUh = workload_CPUh / len(available_agents)
               
        msg = ""
        ## distribute workload to available agent(s)
        for agent in available_agents:
            ## send some workload to it
            ## use the "push_workload" function of the other agent
            next_url = '"http://%s:8080/push_workload?workload=%s&CPUh=%s"'%(agent.ip, workload_name,individual_CPUh)
            push_msg = os.popen('curl -s %s'%(next_url)).read()
            msg += "<br>"+push_msg

        return msg
    
    push_workload.exposed = True
    def show_workload(self,  **params): #B
        #workloads = cherrypy.request.db.query(Workload).order_by(desc(Workload.remaining)).all()
        #workloads = cherrypy.request.db.query(Workload).order_by(desc(Workload.status)).all()
        workloads = cherrypy.request.db.query(Workload).order_by(desc(Workload.status)).all()
        msg = "<table border=1>"
        msg += "<tr><th>name</th><th>CPUh</th><th>remaining</th><th>status</th></tr>"
        for workload in workloads:
            msg += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%( workload.name, workload.CPUh,workload.remaining, workload.status )
        msg += "</table>"
        return msg
    show_workload.exposed = True
    
    def query_workload(self,  **params): #B
        ### this is the function that looks up in self database of workload and check whether it's available for more
        
        # look in processing database
        #workloads = cherrypy.request.db.query(Workload).all()
        running_workloads = cherrypy.request.db.query(Workload).filter(Workload.status=='running').all()
        available_workloads = cherrypy.request.db.query(Workload).filter(Workload.status=='next').all()
      
        running_CPUh = sum([wl.remaining for wl in running_workloads])
        available_CPUh = sum([wl.CPUh for wl in available_workloads])

        ## check on something instead of the number workloads
        #if running_workloads or available_workloads:
        if running_CPUh < available_CPUh:
            ## not available
            return 'N'
        else:
            return 'Y'
    
    query_workload.exposed = True
    
    def pull_workload(self,  **params): #C
        return 'third guy'
    pull_workload.exposed = True
    
    # work load given to agent
    # agent detects alll other agents who have no work (x)
    # agent divides work load into x parts plus self
    #agent distributes work load between x and self using push
    # if an agent finishes before others, it will query all other agents to find available work loads
    #the agent who has finished will use pull to take extra work load from other agents
    #when these other agents finished, they will do the same thing until end of work load
    
    
    
#import os.path
conf = '/home/vlimant/cherrypy/cherrypy.conf'

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    #gconfig = {'global' :{'server.socket_host' : "128.141.252.248",
    #                'server.socket_port' : 8080,
    #               'server.thread_pool' : 10}}
    cherrypy.config.update( config = conf )#gconfig )
    config = {'/' :{'tools.db.on' : True }}
    #cherrypy.tree.mount(Root(), '/', {'/': {'tools.db.on': True}})
    #cherrypy.tree.mount(HelloWorld(), '/', {'/': {'tools.db.on': True}})
    #cherrypy.tree.mount(HelloWorld(), 'global', config=conf)
    cherrypy.tree.mount(HelloWorld(), '/', config )
    cherrypy.engine.start()
    cherrypy.engine.block()
    
    #cherrypy.quickstart(HelloWorld(), config=conf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(HelloWorld(), config=conf)
