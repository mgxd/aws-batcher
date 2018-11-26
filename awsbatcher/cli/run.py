"""Main script to initiate jobs"""

from argparse import ArgumentParser, Action

from awsbatcher import DATALAD_ROOT, PROJECTS_DIR, __version__
from awsbatcher.parser import fetch_data
from awsbatcher.batcher import AWSBatcher

class Str2DictAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        val = dict(val.split('=') for val in values.split(','))
        setattr(namespace, self.dest, val)

def get_parser():
    docstr = "awsbatcher: odp batch jobs made simple"
    parser = ArgumentParser()
    parser.add_argument('--version', action='version', version=__version__)
    # Mandatory arguments
    parser.add_argument('project',
                        choices=PROJECTS_DIR.keys(),
                        help="Datalad project name")
    parser.add_argument('job-queue', help="AWS Batch job queue")
    parser.add_argument('job-def'. help="AWS Batch job definition")
    # Optional job definition overwrites
    jobdef = parser.add_argument_group('job-definitions')
    jobdef.add_argument('--vcpus', type=int, help='Number of vCPUs')
    jobdef.add_argument('--mem-mb', type=int, help='Requested memory (MB)')
    jobdef.add_argument('--envars',
                        action=Str2DictAction,
                        help="One or more environmental variables defined as "
                             "KEY=VALUE and comma-separated")
    jobdef.add_argument('--timeout', type=int, help='Time until timeout (sec)')
    # Optional arguments
    parser.add_argument('--desc', default='awsbatcher', help="Job description")
    parser.add_argument('--maxjobs', type=int, help="Max number of queued jobs")
    parser.add_argument('--dry',
                        action='store_true',
                        default=False,
                        help='Print to console instead of submitting')
    return parser

def main(argv=None):
    parser = get_parser()
    args = parser.parse_args(argv)
    project_url = "%s/%s/%s" % (DATALAD_ROOT,
                                args.project,
                                PROJECTS_DIR[args.project])
    batcher = AWSBatcher(desc=args.desc,
                         dataset=args.project,
                         jobq=args.job_queue,
                         jobdef=args.job-definition,
                         vcpus=args.vcpus,
                         mem_mb=args.mem_mb,
                         envars=args.envars,
                         timeout=args.timeout,
                         maxjobs=args.maxjobs)
    # crawl and aggregate subjects to run
    batch = fetch_data(project_url, batch)
    batch.run(args.dry)

if __name__ == '__main__':
    main()
