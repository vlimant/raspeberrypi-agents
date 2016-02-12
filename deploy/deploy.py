#!/usr/bin/env python                                                                                                                  

import os
import optparse

parser = optparse.OptionParser()
parser.add_option('--python',default=False,action='store_true')
parser.add_option('--jupyter',default=False,action='store_true')
parser.add_option('--extra',default=False,action='store_true')
parser.add_option('--cherry',default=False,action='store_true')
parser.add_option('--master',default=None)
parser.add_option('--install',default=False,action='store_true')
parser.add_option('--config',default=False,action='store_true')
parser.add_option('--init',default=False,action='store_true')
parser.add_option('--run',default=False,action='store_true')
parser.add_option('--kill',default=False,action='store_true')

(options,args) = parser.parse_args()


nodes = {
'jr-raspberrypi-1':'128.141.252.248',
'jr-raspberrypi-2':'128.141.252.23',
'jr-raspberrypi-3':'128.141.252.222',
'jr-raspberrypi-4':'128.141.252.66',
'jr-raspberrypi-5':'128.141.252.95'
}

nodes_name = nodes.keys()
if options.master and options.master in nodes_name:
    nodes_name = [options.master] + list(set(nodes.keys())-set([options.master]))

for name in nodes_name:
    ip = nodes[name]
    print "setting up",name,"@",ip
 
    ##redo from scratch
    if options.install:
        scripts=[
            #'all_in_one.sh',
            ]
        if options.python :
            scripts.append('install_python.sh')
        if options.jupyter:
            scripts.append('install_jupyter.sh')
        if options.extra:
            scripts.append('install_extra.sh')
        for script in scripts:
            os.system("scp %s %s:/home/vlimant/."%(script,ip))
            os.system("ssh %s chmod 755 %s"%(ip,script))
            os.system("ssh %s sudo ./%s"%(ip,script))

    if options.jupyter and options.config:
        cfg_name = 'jupyter_notebook_config_%s.py'% name
        os.system("sed 's/JUPYTERIP/%s/' jupyter_notebook_config.py > %s"%( ip,cfg_name ))
        os.system("ssh %s mkdir -p /home/vlimant/.jupyter/"%ip)
        os.system("scp notebook.* %s:/home/vlimant/.jupyter/"%ip)
        os.system("scp %s %s:/home/vlimant/.jupyter/jupyter_notebook_config.py"%(cfg_name, ip))
        os.system("ssh %s mkdir -p notebook"%ip)


    if options.cherry and options.config:
        cfg_name = 'cherrypy_%s.conf'% name
        os.system("sed 's/JUPYTERIP/%s/' tutorial.conf  > %s"%( ip,cfg_name ))
        os.system("ssh %s mkdir -p /home/vlimant/cherrypy"%ip)
        os.system("scp %s %s:/home/vlimant/cherrypy/cherrypy.conf"%(cfg_name, ip))

        
        ## get the software suite on 
        objects = [ 'cherrypy/run_cherrypy.py',
                    'cherrypy/dbcherry.py',
                    'cherrypy/stop.sh',
                    'cherrypy/start.sh',
                    'cherrypy/dbschema.py',
                    'cherrypy/dbsession.py',
                    'cherrypy/working.py',
                    'notebook/dbsession.py',
                    'notebook/dbschema.py',
                    'notebook/dbtest.ipynb',
                    'database/dbsession.py',
                    'database/dbschema.py',
                    'database/meta.py',
                    ]
        if name == options.master:
            os.system("ssh %s tar zcvf cherry.tgz %s"%(ip, " ".join( objects)))
            os.system("scp %s:cherry.tgz cherry.tgz"%ip)
        else:
            os.system("scp cherry.tgz %s:cherry.tgz"%ip)
            os.system("ssh %s tar zxvf cherry.tgz"%(ip))


    if options.cherry and options.init:
        os.system("ssh %s rm -f /home/vlimant/database/Record.db"%ip)
        os.system("ssh %s python database/meta.py"%ip)
        pass


    if options.cherry and options.run:
        os.system("ssh %s source /home/vlimant/cherrypy/stop.sh"%(ip))
        os.system("ssh %s source /home/vlimant/cherrypy/start.sh %s & "%(ip,ip))

    if options.jupyter and options.run:
        os.system("ssh %s killall jupyter-notebook"%ip)
        os.system("ssh %s jupyter notebook --notebook-dir=/home/vlimant/ &"%(ip))

    if options.cherry and options.kill:
        os.system("ssh %s source /home/vlimant/cherrypy/stop.sh"%(ip))

for name in nodes_name:
    ip = nodes[name]
    if options.cherry and options.init:
        os.system('curl "http://%s:8080/propagate_info?name=%s&ip=%s"'%(ip,name,ip))## itself
        ##IP=`ifconfig | grep eth0 -A1 | grep inet | awk '{ print $2}' | cut -d : -f 2`
        if options.master:
            os.system('curl "http://%s:8080/propagate_info?name=%s&ip=%s"'%(nodes[options.master],name,ip))# and register to the master
