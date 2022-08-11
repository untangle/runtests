#! /usr/bin/python2.7

import glob, os, os.path, shutil, time, traceback, datetime
import stats
import subprocess
import shlex

WWW_DIR = "/var/www/ats"
INCOMING_DIR = os.path.join(WWW_DIR, "incoming")
SLEEP_TIME = 30

def run():

  print "%s: Starting IQD..." % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

  # regenerate stats
  stats.main()

  while True:
    print "%s: Checking for new files in incoming..." % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    found = False
    
    try:
      if os.path.isdir(INCOMING_DIR):
        for tarball in glob.glob(INCOMING_DIR + "/*tar.gz"):
          print "Found new tarball: %s" % str(tarball)
          found = True
          tarballName = os.path.basename(tarball)
          version, timestamp, client = tarballName.split('_')

          majorVersion = version[:6]
          print "%s -> %s, %s, %s, %s" % (tarballName, majorVersion, version, timestamp, client)

          versionDir = os.path.join(WWW_DIR, majorVersion)
          if not os.path.isdir(versionDir):
            os.makedirs(versionDir)

          shutil.move(tarball, versionDir)
          
          cmd = "tar -C '%s' -xvzf '%s'" % (versionDir, os.path.join(versionDir, tarballName))
          print cmd
          process = subprocess.Popen( shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          (stdout, stderr) = process.communicate()
          ret = process.wait()
          print "cmd: " + cmd 
          print "result: " + str(ret) 
          if ret != 0:
            print "tar FAILED"
            print stdout
            print stderr
          # try kill the process if still open.  Might be the source of mem leak.
          try:
            process.kill()
          except OSError:
            # can't kill a dead proc
            pass
          
          if found:
            stats.main()
    except Exception,e:
      print "Exception:"
      traceback.print_exc()

    time.sleep(SLEEP_TIME)
