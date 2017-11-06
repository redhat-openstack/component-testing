#!/usr/bin/env python

# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from octario.lib import exceptions
from octario.lib import execute
from octario.lib import logger

from octario.lib.component import Component
from octario.lib.tester import Tester
from octario.lib.tester import TesterType

import argparse
import datetime
import logging
import os
import sys

LOG = logger.LOG


class OctarioShell(object):

    def get_base_parser(self):
        parser = argparse.ArgumentParser(prog='octario',
                                         description='OpenStack Component '
                                         'Testing Ansible Roles.',
                                         add_help=False)

        parser.add_argument('-?', '-h', '--help',
                            action='help',
                            help='show this help message and exit')

        parser.add_argument('-v', '--verbose',
                            action='store_true',
                            help='increase output verbosity')

        if 'ANSIBLE_INVENTORY' in os.environ:
            default_inventory = os.environ['ANSIBLE_INVENTORY']
        else:
            default_inventory = os.path.join(os.getcwd(), 'hosts')

        parser.add_argument('-i', '--inventory-file',
                            default=default_inventory,
                            help='specify inventory host path'
                                 ' (default=./hosts)')

        parser.add_argument('-t', '--tester',
                            help='Tester to be ran. Supported testers: '
                            '{}'.format(TesterType.get_supported_testers()))

        parser.add_argument('dir',
                            nargs='?',
                            default=os.getcwd(),
                            help='path to component directory')

        return parser

    def parse_args(self, argv):
        parser = self.get_base_parser()
        args = parser.parse_args(argv)

        if args.verbose:
            LOG.setLevel(level=logging.DEBUG)
            LOG.debug('Octario running in debug mode')

        if not args.tester:
            raise exceptions.CommandError("You must provide tester"
                                          " via --tester option")

        LOG.debug('Chosen component directory: %s' % args.dir)
        LOG.debug('Chosen tester: %s' % args.tester)
        LOG.debug('Chosen inventory: %s' % args.inventory_file)

        return args

    def main(self, argv):
        parser_args = self.parse_args(argv)

        tester = Tester(parser_args.tester)
        component = Component(parser_args.dir)

        ansible_playbook = execute.AnsibleExecutor(tester,
                                                   component,
                                                   parser_args.inventory_file,
                                                   path=parser_args.dir)

        ansible_playbook.run()


def main(args=None):
    start_time = datetime.datetime.now()
    LOG.debug('Started octario: %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))

    try:
        if args is None:
            args = sys.argv[1:]

        OctarioShell().main(args)

    except exceptions.OctarioException as ex:
        LOG.error(ex.message)
        sys.exit(1)
    except Exception:
        raise
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    finally:
        finish_time = datetime.datetime.now()
        LOG.debug('Finished octario: %s' %
                  finish_time.strftime('%Y-%m-%d %H:%M:%S'))
        LOG.debug('Run time: %s [H]:[M]:[S].[ms]' %
                  str(finish_time - start_time))


if __name__ == "__main__":
    main()
