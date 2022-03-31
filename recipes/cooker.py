#! /usr/bin/env python3
import os
import sys
import json
import datetime
import subprocess
from cprint import *
from threading import Thread, Lock, Event
from multiprocessing.pool import ThreadPool

def llist (dest):
    os.system("ls -l {}".format(dest))
def rmf (dest):
    os.system("rm -f {}".format(dest))
def rmrf (dest):
    os.system("rm -rf {}".format(dest))
def mkdir (dest):
    os.system("mkdir -p {}".format(dest))
def touch (dest):
    os.system("touch {}".format(dest))
def symlink (source, dest):
    os.system("ln -sf {} {}".format(source, dest))
def zip (dest, source):
    os.system("zip -r {} {}".format(dest, source))
def cat_dump (source, dest):
    os.system("cat {} >> {}".format(source, dest))
def file_append (source, content):
    with open(source, "a") as fd:
        fd.write(content+"\n")
def echo (content, dest):
    os.system('echo "{}" >> {}'.format(content, dest))
def git_clone (repo, branch=None, dest=None):
    cmd = "git clone {}".format(repo)
    if branch is not None:
        cmd += " --branch {}".format(branch)
    if dest is not None:
        cmd += " {}".format(dest)
    os.system(cmd)
def git_checkout (dest):
    os.system("git checkout {}".format(dest))
def exists (dest):
    return os.path.exists(dest)
def make (dest=None, target=None):
    cmd = "make"
    if dest is not None:
        cmd += " -C {}".format(dest)
    if target is not None:
        cmd += " {}".format(target)
    cmd = cmd.split(" ")
    subprocess.run(args=cmd)
    #os.system(cmd)
def grep (dest, marker):
    with open(dest,"r") as fd:
        content = fd.read()
    for line in content.split("\n"):
        if marker in line:
            return line

DEFAULT_PRE_CONFIGURE_HOOKS = [{
    "script": "test=$(gcc --version | head -n 1 | cut -d\" \" -f3) \
        && __BR2_EXTERNAL__/scripts/test_gcc.py 8.1.0 $test",
    "output": "/tmp/.gcc_ok",
},]
 
class Hook :
    def __init__ (self, name, descriptor):
        self.output = None
        self.cmds = []
        self.name = name
        if "output" in descriptor:
            self.output = descriptor["output"]
        for t in descriptor["script"].split(";"):
            t = t.strip(";")
            t = t.strip()
            # special macros 
            t = t.replace("__BR2_EXTERNAL__", os.environ["BR2_EXTERNAL"])
            t = t.replace("__TIMESTAMP__", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.cmds.append(t)
    def has_output (self):
        return self.output is not None
    def run (self):
        do_run = not os.path.exists(self.output) if self.has_output() else False
        if do_run :
            for c in self.cmds:
                retcode = os.system(c)
                if retcode > 0:
                    raise RuntimeError("hook {} failed".format(self.name))
            if self.has_output():
                touch(self.output)
    def clean (self):
        if self.has_output():
            rmf(self.output)

class Board : 
    __BUILD_STAMP__ = datetime.datetime.now()
    def __init__ (self, name, pre_config_hooks=None, post_build_hooks=None, layers=[]):
        self.name = name 
        self.layers = layers
    def board_dir (self):
        return "{}/boards/{}".format(os.environ["BR2_EXTERNAL"], self.name)
    def defconfig (self):
        return self.board_dir() + "/config"
    def arch (self):
        return grep(self.defconfig(), " # cpu").split("=")[0].strip("BR2_")
    def custom_dts (self):
        files = os.listdir(self.board_dir())
        for f in files:
            if f.split(".")[-1] == "dts":
                if not "-layer" in f:
                    if not "-overlay" in f:
                        return f
    def has_custom_dts (self):
        return self.custom_dts() is not None
    def devicetree (self):
        return "{}/{}".format(self.board_dir(), self.custom_dts())
    def mkconfig (self, br_config):
        echo("# {} layer".format(self.name), br_config)
        cat_dump(self.defconfig(), br_config)
        for layer in self.layers:
            cat_dump(self.board_dir() +"/" +layer + "-layer.dts", self.board_dir() + "/" + self.custom_dts())
        # shared but standard attributes
        if self.has_custom_dts():
            file_append(br_config, "BR2_LINUX_KERNEL_CUSTOM_DTS_PATH=\"{}\"".format(self.board_dir() + "/" + self.custom_dts()))
        if exists("{}/uboot-fragments".format(self.board_dir())):
            file_append(br_config, "BR2_TARGET_UBOOT_CONFIG_FRAGMENT_FILES=\"{}\"".format(self.board_dir() + "/uboot-fragments"))
class Image :
    def __init__ (self, name, pre_config_hooks=[], boards=[]):
        self.name = name
        self.pre_config_hooks = pre_config_hooks
        self.boards = []
        for b in boards:
            self.boards.append(b)
    def recipe_dir (self):
        return "{}/recipes/{}".format(os.environ["BR2_EXTERNAL"], self.name)
    def defconfig (self, work_dir):
        return "{}/{}_defconfig".format(self.recipe_dir(), self.name)
    def clean (self, work_dir):
        """ cleans given image """
        for hk in self.pre_configure_hooks:
            hk.clean()
    def cook (self, work_dir):
        """ builds given image """
        for hk in self.pre_config_hooks:
            hk.run()
        for b in self.boards :
            br_dir = work_dir + "/buildroot"
            br_config = br_dir + "/configs/{}_defconfig".format(self.name)
            
            cprint.info("applying {} board layer".format(b.name))
            rmf(br_config)
            b.mkconfig(br_config)
            
            cprint.info("cooking {} recipe".format(self.name))
            if exists("{}/overlay".format(self.recipe_dir())):
                file_append(br_config, 'BR2_ROOTFS_OVERLAY=\"{}\"'.format(self.recipe_dir() +"/overlay"))
            if exists("{}/patches".format(self.recipe_dir())):
                file_append(br_config, 'BR2_GLOBAL_PATCH_DIR=\"{}\"'.format(self.recipe_dir() +"/patches"))
            if exists("{}/linux-fragments".format(self.recipe_dir())):
                file_append(br_config, "BR2_LINUX_KERNEL_CONFIG_FRAGMENT_FILES=\"{}\"".format(self.recipe_dir() + "/linux-fragments"))
            if exists("{}/busybox-fragments".format(self.recipe_dir())):
                file_append(br_config, 'BR2_PACKAGE_BUSYBOX_CONFIG_FRAGMENT_FILES=\"{}\"'.format(self.recipe_dir() +"/busybox-fragments"))
            cat_dump(self.defconfig(work_dir), br_config)
            arch = b.arch()
            make(dest=br_dir, target="{}_defconfig".format(self.name))
            make(dest=br_dir)
        cprint.info("image ready!")
        cprint.info(str(os.listdir(work_dir + "/image")))
 
class Cooker :
    def __init__(self, recipes=[]):
        self.recipes = recipes
    def __len__ (self):
        return len(self.recipes)
    def pop (self):
        self.recipes.pop()
    def push (self, r):
        self.recipes.append(r)
    def cook (self, work_dir, br2_url, br2_tag):
        for r in self.recipes:
            br_dir = work_dir + "/buildroot-{}".format(r.name)
            if not exists(br_dir):
                cprint.warn("Downloading a buildroot")
                git_clone(br2_url, branch=br2_tag, dest=br_dir) 
            # remove residues
            rmf(work_dir + "/image")
            rmf(work_dir + "/buildroot")
            symlink(br_dir, work_dir + "/buildroot")
            symlink(br_dir + "/output/images", work_dir + "/image")
            r.cook(work_dir)
            rmf("image-{}.zip")
            zip("image-{}.zip".format(r.name), work_dir + "/image")
    def clean (self, work_dir):
        # remove residues
        rmf(work_dir + "/image")
        rmf(work_dir + "/buildroot")
        for r in self.recipes:
            r.clean()
            rmf("image-{}.zip".format(r.name))

def cooker (argv):
    cooker = Cooker()
    clean = False
    recipes = []
    dl_dir = "~/br2-downloads"
    _br2_external_ = os.environ["BR2_EXTERNAL"]
    work_dir = _br2_external_
    br2_url = "https://github.com/buildroot/buildroot"
    br2_tag = "2021.08.2"

    for i in range (0, len(argv)):
        if argv[i] == "--list":
            recipes = []
            files = os.listdir(_br2_external_ + "/recipes")
            for f in files:
                if exists(_br2_external_ + "/recipes/{}/recipe".format(f)):
                    recipes.append(f)
            print(recipes)
            return 0

        if argv[i] == "--list-boards":
            boards = []
            files = os.listdir(_br2_external_ + "/boards")
            for f in files:
                if exists(_br2_external_ + "/boards/{}/config".format(f)):
                    boards.append(f)
            print(boards)
            return 0 
        
        if argv[i] == "--br2-revision":
            print("Buildroot revision : {}".format(br2_tag))
            return 0

        if argv[i] == "--br2-url":
            br2_url = argv[i+1]
        if argv[i] == "--br2-tag":
            br2_tag = argv[i+1]

        if argv[i] == "--dl-dir":
            dl_dir = argv[i+1]
        if argv[i] == "--work-dir":
            work_dir = argv[i+1]

        if argv[i] == "--recipe":
            path = argv[i+1]
            if not "/" in path:
                recipe_name = path
                path = _br2_external_ + "/recipes/{}/recipe".format(recipe_name)
            else:
                recipe_name = path.split("/")[-1]

            recipe = open(path, "r")
            recipe = json.loads(recipe.read())
            boards = []
            pre_config_hooks = []
            if "pre_configure_hooks" in recipe:
                hooks = recipe["pre_configure_hooks"][0]
                for k in hooks.keys():
                    pre_config_hooks.append(Hook(k, hooks[k]))
            bds = recipe["boards"][0]
            for board in bds.keys():
                bd = Board(bds[board]["board"], layers=[])
                boards.append(bd)
            recipe = Image(recipe_name, pre_config_hooks=pre_config_hooks, boards=boards)
            cooker.push(recipe)
        
        if argv[i] == "--clean":
            clean = True
    
    if clean:
        cooker.clean(work_dir)
    else:
        # make sure requirements have run
        for hook in DEFAULT_PRE_CONFIGURE_HOOKS:
            hk = Hook(hook["output"], hook)
            hk.run()
        # cook requested recipes
        cooker.cook(work_dir, br2_url, br2_tag)
        
if __name__ == "__main__":
    cooker(sys.argv[1:])
