import subprocess


def execute_command(string_cmd):
    subprocess.check_output(string_cmd, shell=True)
