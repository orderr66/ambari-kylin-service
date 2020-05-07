import os
import base64
from time import sleep
from resource_management import *

class KylinQuery(Script):
    
    def install(self, env):      
        import params
        self.install_packages(env)
        Directory([params.install_dir],
              mode=0755,
              cd_access='a',
              create_parents=True
        )
        Execute('cd ' + params.install_dir + '; wget ' + params.downloadlocation + ' -O kylin.tar.gz  ')
        Execute('cd ' + params.install_dir + '; tar -xvf kylin.tar.gz')
        Execute('cd ' + params.install_dir + '; ln -s apache-kylin-3.0.1-bin-hadoop3 latest')
                

    def configure(self, env):  
        import params
        env.set_params(params)
        kylin_properties = InlineTemplate(params.kylin_properties)   
        File(format("{install_dir}/latest/conf/kylin.properties"), content=kylin_properties)
        
        File(format("{tmp_dir}/kylin_init.sh"),
             content=Template("init.sh.j2"),
             mode=0o700
             )        
        File(format("{tmp_dir}/kylin_env.rc"),
             content=Template("env.rc.j2"),
             mode=0o700
             )              
        Execute(format("bash {tmp_dir}/kylin_init.sh"))
             
    def start(self, env):
        import params
        env.set_params(params)
        self.configure(env)
        Execute(format(". {tmp_dir}/kylin_env.rc;{install_dir}/latest/bin/kylin.sh start"))
        sleep(5)
        Execute("ps -ef | grep java | grep kylin | grep -v grep | awk '{print $2}'>"+format("{install_dir}/latest/pid"))
        Execute(format("rm -rf /var/run/kylin.pid;cp {install_dir}/latest/pid /var/run/kylin.pid"))
        

    def stop(self, env):
        import params
        env.set_params(params)
        self.configure(env)
        Execute(format(". {tmp_dir}/kylin_env.rc;{install_dir}/latest/bin/kylin.sh stop"))


    def restart(self, env):
        self.stop(env)
        self.start(env)

    def status(self, env):
        check_process_status("/var/run/kylin.pid")


if __name__ == "__main__":
    KylinQuery().execute()
