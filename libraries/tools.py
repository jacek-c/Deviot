# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sublime

from ..beginning import __version__


def get_env_paths():
    '''
    All the necessary environment paths are merged to run platformIO
    '''

    from collections import OrderedDict

    # default paths
    if(sublime.platform() == 'windows'):
        default_paths = ["C:\Python27\\", "C:\Python27\Scripts"]
    else:
        default_paths = ["/usr/bin", "/usr/local/bin"]

    system_paths = os.environ.get("PATH", "").split(os.path.pathsep)

    env_paths = []
    env_paths.extend(default_paths)
    env_paths.extend(system_paths)

    env_paths = list(OrderedDict.fromkeys(env_paths))
    env_paths = os.path.pathsep.join(env_paths)

    return env_paths


def save_env_paths(new_path):
    '''
    After install all the necessary dependencies to run the plugin,
    the environment paths are stored in the preferences file
    '''
    from collections import OrderedDict

    env_paths = get_env_paths().split(os.path.pathsep)

    paths = []
    paths.extend(new_path)
    paths.extend(env_paths)

    paths = list(OrderedDict.fromkeys(paths))
    paths = os.path.pathsep.join(paths)

    save_setting('env_path', paths)


def getHeaders():
    """
    headers for urllib request
    """

    user_agent = 'Deviot/%s (Sublime-Text/%s)' % (__version__,
                                                  sublime.version())
    headers = {'User-Agent': user_agent}
    return headers


def extractTar(tar_path, extract_path='.'):
    """
    Extrack tar files in a custom path
    """

    import tarfile
    tar = tarfile.open(tar_path, 'r:gz')
    for item in tar:
        tar.extract(item, extract_path)


def create_command(command):
    """
    Edit the command depending of the O.S of the user
    """
    env_path = get_setting('env_path', False)

    if(not env_path):
        return command

    from . import paths
    bin_dir = paths.getEnvBinDir()

    _os = sublime.platform()

    if(_os is 'osx'):
        exe = 'python'
        options = ['-m', command[0]]
    else:
        exe = command[0]
        options = []

    executable = os.path.join(bin_dir, exe)
    cmd = ['"%s"' % (executable)]
    cmd.extend(options)
    cmd.extend(command[1:])

    return cmd


def run_command(command, cwd=None):
    '''
    Run a command with Popen and return the results or print the errors
    '''
    import subprocess

    command = create_command(command)
    command.append("2>&1")
    command = ' '.join(command)
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, cwd=cwd,
                               universal_newlines=True, shell=True)

    output = process.communicate()
    stdout = output[0]
    return_code = process.returncode

    return (return_code, stdout)


def get_config(key, default=None):
    """
    get a given value in the deviot.ini file or
    return the default value
    """
    from .configobj.configobj import ConfigObj
    from . import paths

    file_config = paths.getConfigFile()
    config = ConfigObj(file_config)

    if(key in config):
        return config[key]
    return default


def save_config(key, value):
    """
    save a value in the deviot.ini file
    """
    from .configobj.configobj import ConfigObj
    from . import paths

    file_config = paths.getConfigFile()
    config = ConfigObj(file_config)

    config[key] = value

    config.write()


def get_setting(key, default=None):
    """
    get setting handled by ST
    """
    import sublime

    settings = sublime.load_settings("Deviot.sublime-settings")

    return settings.get(key, default)


def save_setting(key, value):
    """
    save setting handled by ST
    """
    import sublime

    settings = sublime.load_settings("Deviot.sublime-settings")
    settings.set(key, value)
    sublime.save_settings("Deviot.sublime-settings")
