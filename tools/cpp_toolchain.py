"""Developer-only local C++ tooling for contract audits; never imported by the server."""
import functools
import os
import shutil
import signal
import subprocess
import threading
import time
from pathlib import Path
from backend.catalog import ROOT, DATA

OUTPUT_LIMIT = 48 * 1024
_DOCTOR_LOCK = threading.Lock()

def run_process(args, cwd, env=None, timeout=30, stdin_text=None, separate_stderr=False):
    started = time.monotonic()
    options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
    try:
        proc = subprocess.Popen([str(a) for a in args], cwd=cwd, env=env, stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE if separate_stderr else subprocess.STDOUT, **options)
    except OSError as exc:
        return {'code': -1, 'output': str(exc), 'timeout': False, 'truncated': False, 'duration': 0}
    captured = bytearray()
    errors = bytearray()
    overflow = threading.Event()
    def read(stream, target):
        while True:
            chunk = stream.read(1024)
            if not chunk: break
            room = max(0, OUTPUT_LIMIT - len(captured) - len(errors))
            target.extend(chunk[:room])
            if len(chunk) > room: overflow.set()
    reader = threading.Thread(target=read, args=(proc.stdout,captured), daemon=True)
    reader.start()
    error_reader = threading.Thread(target=read,args=(proc.stderr,errors),daemon=True) if separate_stderr else None
    if error_reader:error_reader.start()
    if stdin_text is not None:
        def write_input():
            try:proc.stdin.write(stdin_text.encode('utf-8'));proc.stdin.close()
            except (OSError,ValueError):pass
        threading.Thread(target=write_input,daemon=True).start()
    expired = False
    while proc.poll() is None:
        expired = time.monotonic() - started > timeout
        if expired or overflow.is_set():
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            else:
                os.killpg(proc.pid, signal.SIGKILL)
            proc.kill()
            break
        time.sleep(.025)
    proc.wait(timeout=5)
    reader.join(timeout=2)
    if error_reader:error_reader.join(timeout=2)
    proc.stdout.close()
    if proc.stderr:proc.stderr.close()
    try:
        output = captured.decode('utf-8')
    except UnicodeDecodeError:
        output = captured.decode('oem' if os.name=='nt' else 'utf-8', errors='replace')
    if expired: output += '\nПревышен лимит времени.'
    if overflow.is_set(): output += '\nПревышен лимит вывода.'
    result={'code': proc.returncode if not expired and not overflow.is_set() else -1, 'output': output, 'timeout': expired, 'truncated': overflow.is_set(), 'duration': round(time.monotonic() - started, 3)}
    if separate_stderr:result['stderr']=errors.decode('utf-8',errors='replace')
    return result

@functools.lru_cache(maxsize=1)
def toolchain():
    env = os.environ.copy()
    env['VSLANG'] = '1033'
    explicit = env.get('CXX')
    candidates = [explicit] if explicit else ['g++', 'clang++']
    for candidate in candidates:
        if candidate and (exe := shutil.which(candidate)):
            if Path(exe).name.lower() in ('cl', 'cl.exe'): continue
            env['PATH'] = str(Path(exe).parent) + os.pathsep + env.get('PATH', '')
            return {'exe': exe, 'kind': 'gcc', 'name': Path(exe).name, 'env': env}
    if os.name == 'nt':
        vswhere = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Microsoft Visual Studio/Installer/vswhere.exe'
        if vswhere.exists():
            query = subprocess.run([str(vswhere), '-latest', '-products', '*', '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64', '-property', 'installationPath'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            vcvars = Path(query.stdout.strip()) / 'VC/Auxiliary/Build/vcvars64.bat'
            if vcvars.exists():
                # Only the discovered fixed developer-environment script crosses cmd.exe.
                raw = subprocess.run(f'cmd.exe /d /s /c ""{vcvars}" >nul && set"', capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=20)
                for line in raw.stdout.decode('mbcs', errors='replace').splitlines():
                    if '=' in line:
                        k, v = line.split('=', 1)
                        if k: env[k.upper()] = v
                exe = shutil.which('cl.exe', path=env.get('PATH'))
                env['VSLANG'] = '1033'
                if exe: return {'exe': exe, 'kind': 'msvc', 'name': 'MSVC C++17', 'env': env}
    return {'exe': None, 'kind': None, 'name': 'Компилятор не найден', 'env': env}

def compile_cpp(sources, output, includes=(), sanitize=False, timeout=40):
    tc = toolchain()
    if not tc['exe']: return {'code': -1, 'output': 'Установите GCC/Clang или Visual Studio Build Tools (Desktop C++). Можно задать CXX.', 'timeout': False, 'truncated': False, 'duration': 0}
    if tc['kind'] == 'msvc':
        flags = ['/nologo', '/std:c++17', '/EHsc', '/W4', '/WX', '/permissive-', '/utf-8', '/Zc:__cplusplus', '/wd4996']
        if sanitize: flags += ['/fsanitize=address', '/Zi']
        args = [tc['exe'], *flags, *[f'/I{p}' for p in includes], *sources, f'/Fe:{output}', '/link', '/INCREMENTAL:NO']
    else:
        flags = ['-std=c++17', '-Wall', '-Wextra', '-Wconversion', '-Wpedantic', '-Werror', '-g']
        if sanitize: flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        args = [tc['exe'], *flags, *[f'-I{p}' for p in includes], *sources, '-o', output]
    return run_process(args, Path(output).parent, tc['env'], timeout)

def execute(exe, args=(), timeout=8, stdin_text=None, separate_stderr=False):
    env = toolchain()['env'].copy()
    env['ASAN_OPTIONS'] = 'alloc_dealloc_mismatch=1:halt_on_error=1' + (':detect_leaks=1' if os.name != 'nt' else '')
    env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    return run_process([exe, *args], Path(exe).parent, env, timeout, stdin_text, separate_stderr)

def doctor():
    with _DOCTOR_LOCK:
        return _doctor_cached()

@functools.lru_cache(maxsize=1)
def _doctor_cached():
    folder = DATA / '.build' / 'doctor'
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / 'probe.cpp'
    source.write_text('#include <iostream>\nint main(){std::cout << "cpp17-ready";}\n', encoding='utf-8')
    exe = folder / ('probe.exe' if os.name == 'nt' else 'probe')
    build = compile_cpp([source], exe)
    run = execute(exe, timeout=15) if build['code'] == 0 else None
    ok = bool(run and run['code'] == 0 and run['output'] == 'cpp17-ready')
    san = compile_cpp([source], exe, sanitize=True) if ok else None
    sanrun = execute(exe, timeout=15) if san and san['code'] == 0 else None
    sanitizer = bool(sanrun and sanrun['code'] == 0)
    # Prove that the sanitizer detects a defect, not just that a flag is accepted.
    detection = False
    if sanitizer:
        source.write_text('int main(int argc,char**){int* p=new int[1];p[argc]=3;delete[] p;return 0;}\n', encoding='utf-8')
        b = compile_cpp([source], exe, sanitize=True)
        bad = execute(exe, timeout=15) if b['code'] == 0 else None
        detection = bool(bad and bad['code'] != 0 and 'AddressSanitizer' in bad['output'])
    return {'compiler': toolchain()['name'], 'path': toolchain()['exe'], 'available': ok, 'addressSanitizer': sanitizer and detection, 'undefinedSanitizer': sanitizer and detection and toolchain()['kind'] != 'msvc', 'leakSanitizer': sanitizer and detection and os.name != 'nt', 'details': (build['output'] + str(run)) if not ok else ((san or {}).get('output', '') if not sanitizer else ''), 'platform': os.name}
