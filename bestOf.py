import re
import subprocess
import sys


def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output


if len(sys.argv) < 2:
    print "Usage: bestOf <count> <command>"
    sys.exit(0)

TIME_RE = re.compile("PERF:\s*(.+)\s+(\\d+) ms")

times = {}

for i in range(int(sys.argv[1])):
    output = check_output(sys.argv[2:])
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

