#! /usr/bin/python

import csv, datetime, glob, os, os.path, re
import traceback
import matplotlib
matplotlib.use('agg')
# from matplotlib import rc
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# ## for Palatino and other serif fonts use:
# #rc('font',**{'family':'serif','serif':['Palatino']))
# rc('text', usetex=True)
import matplotlib.pyplot as pp
import matplotlib.dates as md

RES = { 'passed'   : re.compile(r'(\d+) passed'),
        'failed'   : re.compile(r'(\d+) failed'),
        'skipped'   : re.compile(r'(\d+) skipped'),
        'error'    : re.compile(r'(\d+) error'),
        'duration' : re.compile(r'([\d.]+) seconds') }

DIRS = { 'version'  : re.compile(r'/([\d\.]{6})'),
         'revision' : re.compile(r'~?(?:svn|vcs|\.)?([\da-zrT.]+)(main|trunk|release|master)?'),
         'time'     : re.compile(r'_([\d\-]+T[\d:]+)-[0-9]:*'),
         'host'     : re.compile(r'.+_(.+?)/(?:test|wrapper)\.log') }

FORMAT_LINE = '%(time)s, %(version)s, %(revision)s, %(duration)s, %(host)s, %(passed)s, %(failed)s, %(error)s'

FM = matplotlib.font_manager.FontProperties(size = 8)

DIR = '/var/www/ats'
PNG_PATH_TEMPLATE = '%s/%%s/%%s.png' % (DIR,)
HTML_PATH_TEMPLATE = '%s/%%s/index.html' % (DIR,)

BLESSED_HOSTS = ('smoke', 'untangle', 'ats-uvm-nightly', 'ats-uvm-branch')

def extractDictFromRegexes(string, dict, defaultValue = None, cast = lambda x: x):
  h = {}
  for key, regex in dict.items():
    m = regex.search(string)
    if m:
      h[key] = cast(m.groups()[0])
    else:
      if defaultValue is not None:
        h[key] = defaultValue
      else:
        raise Exception("meh: key '%s' with regex '%s' for string '%s'" %
                        (key, regex.pattern, string))
  return h

def harvest(directory):
  dirs = os.listdir(directory)
  dirs.sort()

  l = []
  
  for d in dirs:
    if d == 'incoming' or not os.path.isdir(os.path.join(DIR, d)):
      continue

    for log in glob.glob(os.path.join(DIR, d, '*/*/', 'test.log')):
      print log
      h = extractDictFromRegexes(log, DIRS)
      h['time'] = datetime.datetime.strptime(h['time'], '%Y-%m-%dT%H:%M:%S')
      h['detailsdir'] = log.replace(DIR + '/', '')
      
      content = file(log).read()
      h2 = extractDictFromRegexes(content, RES, defaultValue = 0, cast = lambda x: int(float(x)))
      h.update(h2)
      # print h
      #  print FORMAT_LINE % h

      l.append(h)

    for log in glob.glob(os.path.join(DIR, d, '*/', 'test.log')):
      print log
      h = extractDictFromRegexes(log, DIRS)
      h['time'] = datetime.datetime.strptime(h['time'], '%Y-%m-%dT%H:%M:%S')
      h['detailsdir'] = log.replace(DIR + '/', '')

      content = file(log).read()
      h2 = extractDictFromRegexes(content, RES, defaultValue = 0, cast = lambda x: int(float(x)))
      h.update(h2)
      # print h
      #  print FORMAT_LINE % h

      l.append(h)

  return l

def getUniqueVersions(l):
  return set([h['version'] for h in l])

def getEntriesForVersion(l, version):
  l2 = [ h for h in l if h['version'] == version ]
  l2.sort(key = lambda h: h['time'])
  return l2

def listOfDictToList(d, key):
  return [ h[key] for h in d ]

def getPlotValues(l, version):
  l2 = getEntriesForVersion(l, version)
  return [ listOfDictToList(l2, x) for x in ('time', 'revision', 'passed', 'failed', 'error') ]
    
def graph(version, dates, revisions, passed, failed, error):
  try:
    # remove invalid entries from graph
    i = 0
    while i < len(dates):
      if passed[i] + failed[i] + error[i] == 0:
        del dates[i]
        del passed[i]
        del failed[i]
        del error[i]
      else:
        i=i+1

    percentage = []
    for x, y, z in zip(passed, failed, error):
      if x+y+z > 0:
        percentage.append(100. * x/(x+y+z))
      else:
        percentage.append(0)

  except:
    traceback.print_exc()
    return None
  
  fig = pp.figure()

  ax1 = pp.subplot(111)
  p1 = ax1.bar(dates, passed, align='center', width=0.9, color = 'g')
  p2 = ax1.bar(dates, failed, align='center', width=0.9, color = 'r', bottom = passed)
  p3 = ax1.bar(dates, error, align='center', width=0.9, color = 'b', bottom = [ x+y for x, y in zip(passed, failed)])
  ax1.set_ylabel('Test count')
  ax1.set_xlabel('Date')
  fig.autofmt_xdate()

  ax2 = ax1.twinx()
  l1 = ax2.plot(dates, percentage, '-oy', linewidth=3)
  ax2.set_ylabel('% passed', color = 'y')
  ax2.xaxis.set_major_locator(md.DayLocator(interval = 2))
  ax2.xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d'))
  ax2.xaxis.set_minor_locator(md.HourLocator(interval = 6))
  ax2.autoscale_view()
  ax2.grid(True)
  for tl in ax2.get_yticklabels():
    tl.set_color('y')
  for tl in ax2.get_xticklabels() + ax2.get_xticklines():
    tl.set_visible(False)
  
  pp.title('ATS runs over time (%s)' % (version,)) 
  leg1 = pp.legend((l1[0],), ('% passed',), loc = 4, shadow = True, prop = FM)
  if len(p1) != 0 and len(p2) != 0 and len(p3) != 0:
    try:
      pp.legend((p1[0], p2[0], p3[0]), ('passed', 'failed','error'), loc = 3, shadow = True, prop = FM)
      pp.gca().add_artist(leg1)
    except:
      traceback.print_exc()

  pngPath = PNG_PATH_TEMPLATE % (version, version,)
  pp.savefig(pngPath)
  pp.close(fig)
  
  return pngPath.replace(DIR + '/', '')

def html(l, version, pngPath):
  html = '<meta http-equiv="refresh" content="300"/>\n'
  html += "<IMG SRC='%s'/>\n" % (os.path.basename(pngPath),)
  html += "<BR/><BR/>\n"
  html += "\n"

  entries = getEntriesForVersion(l, version)
  entries.reverse()

  if (len(entries) > 0):
    entry = entries[0]

    passed = entry['passed']
    failed = entry['failed']
    skipped = entry['skipped']
    total = passed + failed
    if total == 0:
      percent = 0.0
    else:
      percent = ( float( passed ) / float( passed + failed ) ) * 100.0

    html += "<font size=\"5\"><b>Latest Results %.1f%%</b></font>" % percent
    html += "<br/><br/>\n"

  html += "Corresponding entries:"
  html += "<UL>"
  
  for h in entries:
    html += "<LI>%s %s:" % (h['host'].ljust(15), h['time'])
    html += "&nbsp;&nbsp;&nbsp;"
    html += "<A HREF='%s'>%s</A>" % (os.path.join('..', h['detailsdir'], '../' ), 'log files')
    html += "&nbsp;&nbsp;&nbsp;"

    passed = h['passed']
    failed = h['failed']
    skipped = h['skipped']

    total = passed + failed
    if total == 0:
      html += "Missing Results."
    else:
      percent = ( float( passed ) / float( passed + failed ) ) * 100.0
      html += "%.1f%% Passed, %i Failed, %i Skipped." % (percent, failed, skipped)

    html += "\n"
  html += "</UL>"

  open(HTML_PATH_TEMPLATE % (version,), 'w').write(html)
  
def main():
  l = harvest(DIR)
  versions = getUniqueVersions(l)
  for version in versions:
    pngPath = graph(version, *getPlotValues(l, version))
    if pngPath:
      html(l, version, pngPath)
    
if __name__ == '__main__':
  main()
