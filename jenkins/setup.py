#!/usr/bin/env python

import sys, getopt, fnmatch, os, subprocess, platform, string, re

global arch, system

#rootDir = os.getcwd()
#rootDir = "/afs/cern.ch/sw/lcg/app/releases/ROOT-externals/ROOT-test-new"
arch = platform.machine()
system = platform.system()

# --------------------- Setting command lines options 
def main(argv):
   global compiler, build_type, op_sys, external, rootDir
   compiler = ''
   build_type = ''
   op_sys = ''
   external = ''

   opts, args = getopt.getopt(argv,"hc:b:o:v:")
   for opt, arg in opts:
      if opt == '-h':
         print 'setup.py -c <compiler> -b <build_type> -o <operating_system> -v <external>'
         sys.exit()
      elif opt in ("-c"):
         compiler = arg
         print compiler
      elif opt in ("-b"):
         build_type = arg
         print build_type
      elif opt in ("-o"):
         op_sys = arg
         print op_sys
      elif opt in ("-v"):
         external = arg
         print external

   rootDir = "/afs/cern.ch/sw/lcg/app/releases/ROOT-externals/"+external 


# --------------------- Setting default OS 
def default_os():
   if system == 'Darwin' :
      osvers = 'mac' + string.join(platform.mac_ver()[0].split('.')[:2],'')
   elif system == 'Linux' :
      dist = platform.linux_distribution()
      if re.search('SLC', dist[0]):
         osvers = 'slc' + dist[1].split('.')[0]
      elif re.search('CentOS', dist[0]):
         osvers = 'cc' + dist[1].split('.')[0]
      elif re.search('Ubuntu', dist[0]):
         osvers = 'ubuntu' + dist[1].split('.')[0]
      elif re.search('Fedora', dist[0]):
         osvers = 'fedora' + dist[1].split('.')[0]
      else:
         osvers = 'linux' + string.join(platform.linux_distribution()[1].split('.')[:2],'')
   elif system == 'Windows':
      osvers = win + platform.win32_ver()[0]
   else:
      osvers = 'unk-os'

   return osvers;

# --------------------- Setting default compiler 

def default_compiler():

   if os.getenv('COMPILER'):
      compiler_orig = os.getenv('COMPILER')
   else:
      if os.getenv('CC'):
         ccommand = os.getenv('CC')
      elif system == 'Windows':
         ccommand = 'cl'
      elif system == 'Darwin':
         ccommand = 'clang'
      else:
         ccommand = 'gcc'
         if ccommand == 'cl':
            versioninfo = os.popen(ccommand).read()
            patt = re.compile('.*Version ([0-9]+)[.].*')
            mobj = patt.match(versioninfo)
            compiler_orig = 'vc' + str(int(mobj.group(1))-6)
         elif ccommand == 'gcc':
            versioninfo = os.popen(ccommand + ' -dumpversion').read()
            patt = re.compile('([0-9]+)\\.([0-9]+)')
            mobj = patt.match(versioninfo)
            compiler_orig = 'gcc' + mobj.group(1) + mobj.group(2)
         elif ccommand == 'clang':
            versioninfo = os.popen4(ccommand + ' -v')[1].read()
            patt = re.compile('.*version ([0-9]+)[.]([0-9]+)')
            mobj = patt.match(versioninfo)
            compiler_orig = 'clang' + mobj.group(1) + mobj.group(2)
         elif ccommand == 'icc':
            versioninfo = os.popen(ccommand + ' -dumpversion').read()
            patt = re.compile('([0-9]+)')
            mobj = patt.match(versioninfo)
            compiler_orig = 'icc' + mobj.group(1) + mobj.group(2)
         else:
            compiler_orig = 'unk-cmp'
   return compiler_orig;         

# --------------------- Setting default built type 

def default_bt():
   if os.getenv('BUILDTYPE'):
      buildtype = os.getenv('BUILDTYPE')
   else:
      buildtype = 'Release'
      
   if buildtype == 'Release' : bt = 'opt'
   elif buildtype == 'Debug' : bt = 'dbg'
   elif buildtype == 'Optimized' : bt = 'opt'
   else : bt = 'unk'

   return bt;   

# --------------------- Setting names of the main tree directory 

def directories():
   dir_hash = []

   for dirs in os.listdir(rootDir):
      if os.path.isfile(dirs):
         pass
      else:
         dir_hash.append(dirs)

   return dir_hash;      

# --------------------- Setting paths  

def directory_names():
   str = ":"
   dirlist = []
   binlist = []
   liblist = []
   dir_hash = directories()

   Flag = False
   subFlagbins = False

   for i in dir_hash:

      fullpath = rootDir+"/"+i

#      for dirName, subdirList, fileList in os.walk(i):
      for dirName, subdirList, fileList in os.walk(fullpath):   

         for name in sorted(subdirList):

            if ((name.find(compiler) != -1) and (name.find(build_type) != -1) and (name.find(op_sys) != -1)):
               Flag = True
               #               directory =  rootDir+"/"+os.path.join(dirName, name)
               directory =  os.path.join(dirName, name)

               if "Grid" in directory:
                  Flag = False
               if "MCGenerators" in directory:
                  Flag = False

               if "castor" in directory:
                  directory = directory + '/usr'
               if "alien" in directory:
                  directory = directory + '/api'
               dirlist.append(directory);

#######               
               for subdirName, subsubdirList, fileList2 in os.walk(directory):

                  for name2 in sorted(subsubdirList):

                     if (name2 == "lib" or name2 == "lib64"):
                        subFlaglibs = True
                        libs = directory+"/"+name2
                        if "Grid" in libs:
                           subFlaglibs = False
                        if "MCGenerators" in libs:
                           subFlaglibs = False

                        liblist.append(libs)
                        break
                     elif (name2 == "bin"):
                        subFlagbins = True
                        bins = directory+"/"+name2
                        if "Grid" in bins:
                           subFlaglibs = False
                        if "MCGenerators" in bins:
                           subFlaglibs = False

                        binlist.append(bins)

                     else:
                        subFlaglibs = False
                  if (subFlaglibs):break         
########
               break
            else:
               Flag = False
         if Flag:break

   all_dirs = [str.join(dirlist), str.join(binlist), str.join(liblist)]       

   return all_dirs;

if __name__ == "__main__":



   main(sys.argv[1:])
#   rootDir = "/afs/cern.ch/sw/lcg/app/releases/ROOT-externals/"+external

   if not compiler:
      compiler = default_compiler()
   if not build_type:
      build_type = default_bt()
   if not op_sys:
      op_sys = default_os()

   txt_directory = rootDir+"/"+arch+"-"+op_sys+"-"+compiler+"-"+build_type+".txt"

   if os.path.exists(txt_directory):
      fh = open(txt_directory, "r")
      env_var = fh.readlines()
      fh.close()

      prefix = env_var[0].rstrip('\r\n')
      path = env_var[1].rstrip('\r\n')+":"+os.environ["PATH"]
      ld_libs = env_var[2].rstrip('\r\n')+":"+os.environ["LD_LIBRARY_PATH"] 

      print prefix 
      print path 
      print ld_libs

   else:
      os.environ["CMAKE_PREFIX_PATH_ALL"] = directory_names()[0]
      os.environ["PATH_ALL"] = directory_names()[1]+":"+os.environ["PATH"]
      os.environ["LD_LIBRARY_PATH_ALL"] = directory_names()[2]+":"+os.environ["LD_LIBRARY_PATH"]
      
      prefix = os.environ["CMAKE_PREFIX_PATH_ALL"]
      path = os.environ["PATH_ALL"]
      ld_libs = os.environ["LD_LIBRARY_PATH_ALL"]

      print '%s=%s' % ("export CMAKE_PREFIX_PATH", prefix)
      print '%s=%s' % ("export PATH", path)
      print '%s=%s' % ("export LD_LIBRARY_PATH", ld_libs)


