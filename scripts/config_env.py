#!/usr/bin/env python
import yaml
import argparse
import os
import subprocess


class VirtualEnv:

    # Load YAML file and map the yaml fields to attributes
    def __init__(self, env_yaml):
        
        self.env = env_yaml
        self.script_dir = "/builder/jjb/integration/"
        self.job_template_yaml="integration-templates.yaml"
        self.job_macros_yaml="integration-macros.yaml"
        if self.env.get("log"):
            self.log = open(self.env["log"], 'w')
        else:
            self.log = None
        
        if not self.env.get("env_var") and not self.env["env_var"].get("WORKSPACE"):
            raise Exception("Environment variables section or WORKSPACE env not set in yaml config")
        else:
            # Prepare workspace and jump into it
            workspace = self.env["env_var"]["WORKSPACE"]
            if os.path.isdir(workspace) and os.path.exists(workspace):
                os.chdir(workspace)
            else:
                os.makedirs(workspace)
                os.chdir(workspace) 

    def load_env_vars(self):
        
        for env_var_name in self.env["env_var"]:
            os.environ[env_var_name] = self.env["env_var"][env_var_name]
        
    def print_env_vars(self):
        for env_var_name in self.env["env_var"]:
            print("%s = %s" %(env_var_name,os.environ[env_var_name]))
    
    def run_macro(self,macro, builder_name):
    
        if type(macro) == dict:
            for script in macro["include-raw"]:
                if os.path.isfile(self.script_dir+script):
                    # Add executable rights
                    os.chmod(self.script_dir + script, 0774)
                    print("############ Executing script %s ################" % script) 
                    if self.log:
                        rc = subprocess.call(self.script_dir + script,shell=True, stdout=self.log, stderr=subprocess.PIPE)
                    else:
                        rc = subprocess.call(self.script_dir + script,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if rc:
                        raise Exception("Something went wrong during the execution of %s script" % script)
                else:
                    raise IOError("File %s not found" % script)
        else:
            # Script hardcoded in the yaml
            # Put text script into a script file
            if not self.env.get("env_var") and not self.env["env_var"].get("SSHPASS"):
                raise Exception("Environment variables section or SSHPASS env not set in yaml config")
            
            script_name = "/tmp/" + builder_name + ".sh"
            with open(script_name, "w+") as script_file:
                macro = macro.replace("ssh-copy-id", "sshpass -e ssh-copy-id")
                script_file.write(macro)
            # Add executable rights
            os.chmod(script_name, 0744)
            print("############ Executing hardcoded script %s ################" % script_name) 
            
            if self.log:
                rc = subprocess.call(script_name, shell=True, stdout=self.log, executable='/bin/bash')
            else:
                rc = subprocess.call(script_name, shell=True, executable='/bin/bash')
            if rc:
                raise Exception("Something went wrong during the execution of the script")
           
    def find_macro(self,builder_name):    
        macros_file = open(self.script_dir+self.job_macros_yaml, "r+").read()
        # Remove ! character from yaml as pyyaml is not able to decode it
        macros_file = macros_file.replace("!include-", "include-")
        # Get all the builders from the yaml
        macro_builders = [x for x in yaml.load(macros_file) if x.get("builder")]
        
        macros_found = [x for x in macro_builders if x["builder"]["name"] == builder_name]
        
        if not macros_found:
            raise Exception("Builder %s not found in macros template %s" % (builder_name, self.job_macros_yaml))
        
        #Builder example:
        #- builder:
        #    name: integration-start-cluster-run-test
        #    builders:
        #        - shell:
        #            !include-raw:
        #                - include-raw-integration-start-cluster-run-test.sh
        for macro in macros_found:
            
            self.run_macro(macro["builder"]["builders"][0]["shell"], builder_name)

            
    def inject_env_vars(self, env_file):
    
        if not self.env.get("env_var") and not self.env["env_var"].get("WORKSPACE"):
            raise Exception("Environment variables section or WORKSPACE env not set in yaml config")
        
        # Env vars file location to inject
        loc = self.env["env_var"]["WORKSPACE"] + "/" + env_file
        if not os.path.exists(loc):
            raise IOError("File %s not found" % loc)
            
        with open(loc, "r") as file:
            for line in file.readlines():
                fields = line.split("=")
                os.environ[fields[0]] = fields[1].rstrip()
            
    
    def execute_bash_scripts(self, builders):
             
        for builder in builders:
            if type(builder) == dict:
                self.inject_env_vars(builder["inject"]["properties-file"])
            else:
                self.find_macro(builder)
            
    def configure_env(self):
        self.load_env_vars()
        # Debugging
        self.print_env_vars()
        jenkins_template = yaml.load(open(self.script_dir+self.job_template_yaml))
  
        job = [x for x in jenkins_template if x["job-template"]["name"] == self.env["job_template"]]
        
        if not job:
            raise Exception("Job template name %s not found in file %s" % (self.env["job_template"],self.job_template_yaml))        
       
        self.execute_bash_scripts(job[0]["job-template"]["builders"])
               
        
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("config_yaml", help="Yaml file with the virtual environment configuration")
parser.add_argument("env_name", help="Name of the virtual environment to be configured")
args = parser.parse_args()
#
#main
#
def main():
    
    virt_env = None
    with open(str(args.config_yaml), 'r') as stream:
        try:
            yaml_file = yaml.load(stream)
            for env in yaml_file:
                if env["name"] == str(args.env_name):
                    virt_env = VirtualEnv(env)
                    break
             
        except yaml.YAMLError as exc:
            print(exc)
    
    if not virt_env:
        raise Exception("Env name argument %s not existing in yaml configuration" % args.env_name)
                   
    virt_env.configure_env()
    
if __name__ == '__main__':
    main()
