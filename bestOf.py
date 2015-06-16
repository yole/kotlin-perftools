import re
import subprocess
import sys

if len(sys.argv) < 2:
    print "Usage: bestOf <count> <command>"
    sys.exit(0)

TIME_RE = re.compile("PERF:\s*([^0-9]+)(\\d+) ms")

times = {}

for i in range(int(sys.argv[1])):
    output = subprocess.check_output(sys.argv[2:])
    for line in output.split('\n'):
        match = TIME_RE.search(line)
        if match:
            operation = match.group(1)
            time = int(match.group(2))
            prev_time = times.get(operation)
            if not prev_time or time < prev_time:
                times[operation] = time

for op, time in times.items():
    print("##teamcity[buildStatisticValue key='%(op)s' value='%(time)d']" % {'op': op.strip(), 'time': time})

