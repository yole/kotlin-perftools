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

TIME_RE = re.compile("PERF:\s*(.+)\s+(\\d+) ms")
TAG_RE = re.compile("^([A-Z]+):")


def run_command(args):
    print "Running " + " ".join(args)
    command_times = {}
    output = check_output(args)
    for line in output.split('\n'):
        print line
        match = TIME_RE.search(line)
        if match:
            operation = match.group(1)
            tag_match = TAG_RE.search(operation)
            if tag_match:
                operation = tag_match.group(1)
            time = int(match.group(2))
            prev_time = command_times.get(operation, 0)
            command_times[operation] = time + prev_time
    return command_times

if len(sys.argv) < 2:
    print "Usage: bestOf <count> <command>"
    sys.exit(0)

times = {}

for i in range(int(sys.argv[1])):
    command_times = run_command(sys.argv[2:])
    for op, time in command_times.items():
        prev_time = times.get(op)
        if not prev_time or time < prev_time:
            times[op] = time

for op, time in times.items():
    print("##teamcity[buildStatisticValue key='%(op)s' value='%(time)d']" % {'op': op.strip(), 'time': time})
