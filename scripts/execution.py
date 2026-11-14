"""Bound external work, preserving one POSIX process-group owner across nested commands."""
from contextlib import ExitStack
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

_CONTEXT = '_DECK_STUDIO_EXEC_CONTEXT'


class ExecutionTimeout(RuntimeError):
    pass


def positive_seconds(value):
    try:
        seconds = float(value)
    except (ValueError, TypeError):
        raise ValueError('time limit must be a positive finite number') from None
    if isinstance(value, bool) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('time limit must be a positive finite number')
    return seconds


class Deadline:
    def __init__(self, seconds):
        self.end = time.monotonic() + positive_seconds(seconds)

    def remaining(self, cap=None):
        remaining = self.end - time.monotonic()
        if remaining <= 0:
            raise ExecutionTimeout('total execution budget exhausted; stop and report the incomplete stage')
        return min(remaining, positive_seconds(cap)) if cap is not None else remaining


def _inherited_context():
    directory = os.environ.get(_CONTEXT)
    if not directory or os.name != 'posix':
        return None
    owner = Path(directory)/'owner.json'
    # The launching parent writes its child's group ID immediately after Popen returns.
    until = time.monotonic()+.25
    while not owner.exists() and time.monotonic() < until:
        time.sleep(.005)
    try:
        metadata = json.loads(owner.read_text())
    except (OSError, ValueError):
        raise ExecutionTimeout('execution ownership unavailable; stop the nested stage') from None
    if metadata.get('group') != os.getpgrp():
        raise ExecutionTimeout('execution group changed; stop the nested stage')
    return directory


def _kill_group(group):
    try:
        os.killpg(group,signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_bounded(command, *, timeout, check=False, capture_output=False, **kwargs):
    """Run without shell execution or hidden retries. Timeout raises ExecutionTimeout.

    A nested timeout ends the entire owned POSIX stage, so sibling/descendant converters cannot
    outlive its limit. Windows cleans up direct processes and requires host/job supervision.
    """
    timeout = positive_seconds(timeout)
    if 'shell' in kwargs or 'start_new_session' in kwargs:
        raise ValueError('run_bounded controls shell and process-group settings')
    if capture_output:
        if 'stdout' in kwargs or 'stderr' in kwargs:
            raise ValueError('capture_output conflicts with stdout/stderr')
        kwargs.update(stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    inherited = _inherited_context()
    with ExitStack() as stack:
        directory = inherited or stack.enter_context(tempfile.TemporaryDirectory(prefix='deck-exec-'))
        owned = inherited is None
        env = dict(kwargs.pop('env',os.environ))
        env[_CONTEXT] = directory
        process = subprocess.Popen(command,start_new_session=owned and os.name=='posix',env=env,**kwargs)
        marker = Path(directory)/'timeout.txt'
        message = f'{os.path.basename(str(command[0]))} exceeded {timeout:g}s; stop and report the incomplete stage'
        try:
            if owned and os.name=='posix':
                owner = Path(directory)/'owner.pending'
                owner.write_text(json.dumps({'group':process.pid}))
                owner.replace(Path(directory)/'owner.json')
            try:
                stdout,stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                if not owned and os.name=='posix':
                    marker.write_text(message)
                    _kill_group(os.getpgrp())  # outer owner reports the marker and cleans its workspace
                elif os.name=='posix':
                    _kill_group(process.pid)
                else:
                    process.kill()
                try:
                    process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    pass  # do not wait indefinitely on inherited output pipes
                raise ExecutionTimeout(message) from None
            if marker.exists():
                raise ExecutionTimeout(marker.read_text())
            result = subprocess.CompletedProcess(command,process.returncode,stdout,stderr)
            if check and result.returncode:
                raise subprocess.CalledProcessError(result.returncode,command,stdout,stderr)
            return result
        finally:
            if owned and os.name=='posix':
                _kill_group(process.pid)
            elif process.poll() is None:
                process.kill()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            for stream in (process.stdout,process.stderr,process.stdin):
                if stream:
                    stream.close()
