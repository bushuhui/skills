#!/usr/bin/env python3
"""启动 Chrome remote debugging 模式，后台运行后立即返回，Chrome 退出自动重启。"""

import os
import signal
import subprocess
import sys
import time

DEFAULT_PORT = 9222
DEFAULT_PROFILE = f"{os.path.expanduser('~')}/.config/google-chrome-cdp"
SYSTEM_PROFILE = f"{os.path.expanduser('~')}/.config/google-chrome"

# 连续启动失败超过此次数后停止重试
MAX_CRASH_RETRIES = 5
# Chrome 启动后在此时间内退出视为"崩溃"
CRASH_THRESHOLD = 10  # seconds


def tmp_file(name):
    base = os.environ.get("TMPDIR", "/tmp")
    return f"{base}/{name}"


class ChromeDaemon:
    def __init__(self, port, profile):
        self.port = port
        self.profile = profile
        self.pid_file = tmp_file(f"chrome-debug-{port}.pid")
        self.log_file = tmp_file(f"chrome-debug-{port}.log")

    # --- daemon lifecycle ---

    def write_pid(self):
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

    def remove_pid(self):
        try:
            os.remove(self.pid_file)
        except FileNotFoundError:
            pass

    def stop_existing(self):
        """如果已有同端口守护进程在运行，先停掉。"""
        if not os.path.exists(self.pid_file):
            return
        try:
            with open(self.pid_file) as f:
                old_pid = int(f.read())
            os.kill(old_pid, signal.SIGTERM)
            time.sleep(0.5)
        except (ProcessLookupError, ValueError):
            pass
        self.remove_pid()

    def launch_chrome(self):
        args = [
            os.environ.get("CHROME_BIN", "google-chrome"),
            f"--remote-debugging-port={self.port}",
            "--remote-debugging-address=127.0.0.1",
            "--autoConnect",
            f"--user-data-dir={self.profile}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        with open(self.log_file, "a") as f:
            proc = subprocess.Popen(
                args, stdout=f, stderr=subprocess.STDOUT, start_new_session=True
            )
        return proc

    def run(self):
        print(f"Port: {self.port}")
        print(f"Profile: {self.profile}")
        print(f"Log: {self.log_file}")
        print(f"PID file: {self.pid_file}")

        self.stop_existing()
        self.write_pid()

        def shutdown(signum, frame):
            print("\nShutting down daemon...")
            self.remove_pid()
            sys.exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        launch_count = 0
        crash_count = 0

        while True:
            launch_count += 1
            start_time = time.time()
            proc = self.launch_chrome()
            print(f"[{launch_count}] Chrome started (PID={proc.pid})")

            try:
                proc.wait()
            except KeyboardInterrupt:
                break

            elapsed = time.time() - start_time
            code = proc.returncode

            # 判断是崩溃还是正常关闭
            if elapsed < CRASH_THRESHOLD:
                crash_count += 1
                print(
                    f"Chrome exited with code {code} after {elapsed:.0f}s "
                    f"(crash {crash_count}/{MAX_CRASH_RETRIES})"
                )
                if crash_count >= MAX_CRASH_RETRIES:
                    print("Too many crashes, giving up.")
                    break
                # 指数退避：3s, 6s, 12s, 24s, 48s
                wait = min(3 * (2 ** (crash_count - 1)), 60)
                print(f"Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                # 运行超过阈值视为正常关闭，重置崩溃计数
                crash_count = 0
                print(f"Chrome exited with code {code} after {elapsed:.0f}s")
                print("Restarting in 3s...")
                time.sleep(3)

        self.remove_pid()
        print("Daemon stopped.")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    profile = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PROFILE

    if profile == SYSTEM_PROFILE:
        print(f"ERROR: Chrome remote debugging 不能使用默认 profile: {SYSTEM_PROFILE}")
        print(f"请使用独立目录，例如:")
        print(f"  {sys.argv[0]} {port} $HOME/.config/google-chrome-cdp")
        sys.exit(2)

    os.makedirs(profile, exist_ok=True)
    ChromeDaemon(port, profile).run()
