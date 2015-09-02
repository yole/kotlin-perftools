import re
import subprocess
import sys
from optparse import OptionParser


def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]

        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output

TIME_RE = re.compile("PERF:\s*(.+)\s+(\\d+) ms")
TAG_RE = re.compile("^([A-Z]+):")


def run_command(args, useBestInRun):
    print "Running " + " ".join(args)
    command_times = {}
    try:
        output = check_output(args)
    except subprocess.CalledProcessError as e:
        print "Command execution failed:"
        print e.output
        sys.exit(1)

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
            if useBestInRun:
                if not prev_time or time < prev_time:
                    command_times[operation] = time
            else:
                command_times[operation] = time + prev_time
    return command_times


def main():
    parser = OptionParser("Usage: %prog [options] command")
    parser.add_option("-c", dest="count", type="int", default=1)
    parser.add_option("-p", dest="prefix")
    parser.add_option("-b", dest="bestInRun", action="store_true")

    (options, args) = parser.parse_args()

    if not args:
        parser.error("Command must be specified")

    times = {}

    for i in range(int(options.count)):
        command_times = run_command(args, options.bestInRun)
        for op, time in command_times.items():
            prev_time = times.get(op)
            if not prev_time or time < prev_time:
                times[op] = time

    for op, time in times.items():
        statistic_key = options.prefix + " " + op.strip() if options.prefix else op.strip()
        print("##teamcity[buildStatisticValue key='%(key)s' value='%(time)d']" % {'key': statistic_key, 'time': time})

if __name__ == "__main__":
    main()
