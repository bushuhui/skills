#!/usr/bin/env python3
"""Clash Verge 代理控制工具 - 通过 RESTful API 管理代理"""

import argparse
import ipaddress
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

API_BASE = "http://192.168.1.15:9098"


def api_get(path):
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def api_put(path, data):
    url = f"{API_BASE}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status


def api_get_delay(name, url="http://1.1.1.1", timeout=3000):
    encoded = urllib.parse.quote(name, safe="")
    path = f"/proxies/{encoded}/delay?url={urllib.parse.quote(url)}&timeout={timeout}"
    return api_get(path)


def get_proxies():
    return api_get("/proxies")["proxies"]


def cmd_list(args):
    """列出所有代理组及其当前选择"""
    proxies = get_proxies()
    group_types = ("Selector", "URLTest", "Fallback", "LoadBalance")

    groups = {
        name: info
        for name, info in sorted(proxies.items())
        if info.get("type") in group_types
    }

    for name, info in groups.items():
        ptype = info["type"]
        current = info.get("now", "")
        print(f"\n{'='*60}")
        print(f"  {name}  (type={ptype})")
        print(f"  当前: {current}")
        print(f"{'='*60}")

        if not args.verbose:
            continue

        for node_name in info.get("all", []):
            node = proxies.get(node_name, {})
            delay = 0
            alive = "-"
            if node.get("history"):
                last = node["history"][-1]
                delay = last.get("delay", 0)
            if delay > 0:
                alive = f"{delay}ms"
            elif node.get("type") in group_types:
                alive = f"-> {node.get('now', '?')}"
            else:
                alive = "timeout"

            marker = " *" if node_name == current else "  "
            print(f"  {marker} {node_name:40s}  {alive}")


def cmd_nodes(args):
    """列出所有可用节点及延迟"""
    proxies = get_proxies()
    group_types = ("Selector", "URLTest", "Fallback", "LoadBalance")
    skip_types = ("Direct", "Reject", "RejectDrop", "Pass", "Compatible")

    nodes = []
    for name, info in sorted(proxies.items()):
        ptype = info.get("type", "")
        if ptype in group_types or ptype in skip_types:
            continue
        delay = 0
        if info.get("history"):
            delay = info["history"][-1].get("delay", 0)
        nodes.append((name, ptype, delay))

    print(f"{'节点名称':40s}  {'类型':15s}  {'延迟':>8s}")
    print("-" * 68)
    for name, ptype, delay in nodes:
        delay_str = f"{delay}ms" if delay > 0 else "timeout"
        print(f"{name:40s}  {ptype:15s}  {delay_str:>8s}")


def cmd_switch(args):
    """切换代理组的选中节点"""
    group = args.group
    node = args.node
    proxies = get_proxies()

    if group not in proxies:
        print(f"错误: 代理组 '{group}' 不存在")
        print(f"可用代理组: {[n for n, i in proxies.items() if i.get('type') == 'Selector']}")
        return 1

    info = proxies[group]
    if info.get("type") != "Selector":
        print(f"错误: '{group}' 类型为 {info['type']}，只有 Selector 类型支持手动切换")
        return 1

    available = info.get("all", [])
    if node not in available:
        print(f"错误: 节点 '{node}' 不在代理组 '{group}' 中")
        print(f"可用节点:")
        for n in available:
            print(f"  - {n}")
        return 1

    encoded = urllib.parse.quote(group, safe="")
    status = api_put(f"/proxies/{encoded}", {"name": node})
    if status == 204:
        print(f"切换成功: {group} -> {node}")
    else:
        print(f"切换失败: HTTP {status}")
        return 1


def cmd_test(args):
    """测试节点延迟"""
    name = args.node
    proxies = get_proxies()
    if name not in proxies:
        print(f"错误: 节点 '{name}' 不存在")
        return 1

    print(f"正在测试 {name} 的延迟...")
    try:
        result = api_get_delay(name, timeout=args.timeout)
        delay = result.get("delay", 0)
        if delay > 0:
            print(f"  {name}: {delay}ms")
        else:
            print(f"  {name}: timeout")
    except urllib.error.HTTPError as e:
        print(f"  {name}: 测试失败 ({e.code})")


def cmd_test_group(args):
    """测试代理组内所有节点的延迟"""
    group = args.group
    proxies = get_proxies()

    if group not in proxies:
        print(f"错误: 代理组 '{group}' 不存在")
        return 1

    encoded = urllib.parse.quote(group, safe="")
    url = args.url
    timeout = args.timeout
    print(f"正在测试代理组 '{group}' 的所有节点...")

    try:
        path = f"/group/{encoded}/delay?url={urllib.parse.quote(url)}&timeout={timeout}"
        result = api_get(path)
        for node_name, delay in sorted(result.items(), key=lambda x: x[1] if x[1] > 0 else 99999):
            delay_str = f"{delay}ms" if delay > 0 else "timeout"
            print(f"  {node_name:40s}  {delay_str}")
    except urllib.error.HTTPError:
        all_nodes = proxies[group].get("all", [])
        for node_name in all_nodes:
            try:
                result = api_get_delay(node_name, url=url, timeout=timeout)
                delay = result.get("delay", 0)
                delay_str = f"{delay}ms" if delay > 0 else "timeout"
            except urllib.error.HTTPError:
                delay_str = "error"
            print(f"  {node_name:40s}  {delay_str}")


def _parse_country_keywords(country):
    """将国家/地区关键词映射为节点名称中可能出现的标识。"""
    mapping = {
        "us": ["🇺🇸", "美国", "US", "us-", "United States"],
        "cn": ["🇨🇳", "中国", "CN", "cn-", "China", "回国"],
        "jp": ["🇯🇵", "日本", "JP", "jp-", "Japan", "东京", "大阪"],
        "kr": ["🇰🇷", "韩国", "KR", "kr-", "Korea", "首尔"],
        "hk": ["🇭🇰", "香港", "HK", "hk-", "Hong Kong"],
        "tw": ["🇹🇼", "台湾", "TW", "tw-", "Taiwan", "台北"],
        "sg": ["🇸🇬", "新加坡", "SG", "sg-", "Singapore"],
        "uk": ["🇬🇧", "英国", "UK", "uk-", "England", "London"],
        "de": ["🇩🇪", "德国", "DE", "de-", "Germany", "Frankfurt"],
        "ru": ["🇷🇺", "俄罗斯", "RU", "ru-", "Russia", "Moscow"],
    }
    key = country.strip().lower()
    if key in mapping:
        return mapping[key]
    return [country]


def cmd_switch_country(args):
    """按国家/地区自动切换 — 筛选可达节点，选延迟最低的"""
    country = args.country
    keywords = _parse_country_keywords(country)
    group = args.group or "GLOBAL"
    proxies = get_proxies()

    if group not in proxies:
        print(f"错误: 代理组 '{group}' 不存在")
        return 1

    info = proxies[group]
    if info.get("type") != "Selector":
        print(f"错误: '{group}' 类型为 {info['type']}，不支持手动切换")
        return 1

    all_nodes = info.get("all", [])
    candidates = [n for n in all_nodes if any(kw in n for kw in keywords)]
    if not candidates:
        print(f"错误: 代理组 '{group}' 中未找到匹配以下关键词的节点: {keywords}")
        print("可用节点:")
        for n in all_nodes:
            print(f"  - {n}")
        return 1

    print(f"找到 {len(candidates)} 个候选节点，正在测试延迟...")
    reachable = []
    for node_name in candidates:
        try:
            result = api_get_delay(node_name, timeout=3000)
            delay = result.get("delay", 0)
            if delay > 0:
                reachable.append((node_name, delay))
                print(f"  {node_name}: {delay}ms ✓")
            else:
                print(f"  {node_name}: timeout ✗")
        except urllib.error.HTTPError:
            print(f"  {node_name}: 测试失败 ✗")

    if not reachable:
        print(f"错误: 没有可达的 {country} 节点")
        return 1

    reachable.sort(key=lambda x: x[1])
    best_name, best_delay = reachable[0]
    encoded = urllib.parse.quote(group, safe="")
    status = api_put(f"/proxies/{encoded}", {"name": best_name})
    if status == 204:
        print(f"切换成功: {group} -> {best_name} ({best_delay}ms)")
    else:
        print(f"切换失败: HTTP {status}")
        return 1


def cmd_status(args):
    """显示当前代理状态概览"""
    proxies = get_proxies()
    version = api_get("/version")

    print(f"Clash 版本: {version.get('version', '?')}")
    print()

    key_groups = ["SSRDOG", "GLOBAL", "Auto"]
    for gname in key_groups:
        if gname in proxies:
            info = proxies[gname]
            ptype = info.get("type", "?")
            current = info.get("now", "?")
            print(f"  {gname:20s}  type={ptype:10s}  当前={current}")


# --- HTTP API Server ---

def _get_status_data():
    proxies = get_proxies()
    version = api_get("/version")
    groups = {}
    for gname in ["SSRDOG", "GLOBAL", "Auto"]:
        if gname in proxies:
            info = proxies[gname]
            groups[gname] = {"type": info.get("type", "?"), "now": info.get("now", "?")}
    return {"version": version.get("version", "?"), "groups": groups}


def _get_proxies_data():
    proxies = get_proxies()
    group_types = ("Selector", "URLTest", "Fallback", "LoadBalance")
    result = []
    for name, info in sorted(proxies.items()):
        if info.get("type") not in group_types:
            continue
        nodes = []
        current = info.get("now", "")
        for node_name in info.get("all", []):
            node = proxies.get(node_name, {})
            delay = 0
            if node.get("history"):
                delay = node["history"][-1].get("delay", 0)
            nodes.append({"name": node_name, "delay": delay, "selected": node_name == current})
        result.append({"name": name, "type": info["type"], "now": current, "nodes": nodes})
    return result


def _get_nodes_data():
    proxies = get_proxies()
    group_types = ("Selector", "URLTest", "Fallback", "LoadBalance")
    skip_types = ("Direct", "Reject", "RejectDrop", "Pass", "Compatible")
    nodes = []
    for name, info in sorted(proxies.items()):
        ptype = info.get("type", "")
        if ptype in group_types or ptype in skip_types:
            continue
        delay = 0
        if info.get("history"):
            delay = info["history"][-1].get("delay", 0)
        nodes.append({"name": name, "type": ptype, "delay": delay})
    return nodes


def _do_switch(group, node):
    proxies = get_proxies()
    if group not in proxies:
        return {"error": f"代理组 '{group}' 不存在"}, 404
    info = proxies[group]
    if info.get("type") != "Selector":
        return {"error": f"'{group}' 类型为 {info['type']}，不支持手动切换"}, 400
    available = info.get("all", [])
    if node not in available:
        return {"error": f"节点 '{node}' 不在代理组 '{group}' 中", "available": available}, 400
    encoded = urllib.parse.quote(group, safe="")
    status = api_put(f"/proxies/{encoded}", {"name": node})
    if status == 204:
        return {"ok": True, "group": group, "node": node}, 200
    return {"error": f"切换失败: HTTP {status}"}, 502


def _do_test_node(name, timeout=3000):
    proxies = get_proxies()
    if name not in proxies:
        return {"error": f"节点 '{name}' 不存在"}, 404
    try:
        result = api_get_delay(name, timeout=timeout)
        return {"name": name, "delay": result.get("delay", 0)}, 200
    except urllib.error.HTTPError as e:
        return {"name": name, "error": f"测试失败 ({e.code})"}, 502


def _do_test_group(group, url="http://1.1.1.1", timeout=3000):
    proxies = get_proxies()
    if group not in proxies:
        return {"error": f"代理组 '{group}' 不存在"}, 404
    encoded = urllib.parse.quote(group, safe="")
    try:
        path = f"/group/{encoded}/delay?url={urllib.parse.quote(url)}&timeout={timeout}"
        result = api_get(path)
        nodes = [{"name": k, "delay": v} for k, v in sorted(result.items(), key=lambda x: x[1] if x[1] > 0 else 99999)]
        return {"group": group, "nodes": nodes}, 200
    except urllib.error.HTTPError:
        all_nodes = proxies[group].get("all", [])
        nodes = []
        for node_name in all_nodes:
            try:
                r = api_get_delay(node_name, url=url, timeout=timeout)
                nodes.append({"name": node_name, "delay": r.get("delay", 0)})
            except urllib.error.HTTPError:
                nodes.append({"name": node_name, "delay": -1})
        return {"group": group, "nodes": nodes}, 200


class ClashAPIHandler(BaseHTTPRequestHandler):
    allowed_networks = None

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {self.client_address[0]} - {format % args}\n")

    def _check_ip(self):
        if self.allowed_networks is None:
            return True
        client_ip = ipaddress.ip_address(self.client_address[0])
        return any(client_ip in net for net in self.allowed_networks)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, status, msg):
        self._send_json({"error": msg}, status)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if not self._check_ip():
            self._send_error_json(403, "IP not allowed")
            return
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        try:
            if path == "/api/status":
                self._send_json(_get_status_data())
            elif path == "/api/proxies":
                self._send_json(_get_proxies_data())
            elif path == "/api/nodes":
                self._send_json(_get_nodes_data())
            elif path.startswith("/api/test-group/"):
                group = urllib.parse.unquote(path[len("/api/test-group/"):])
                data, status = _do_test_group(group)
                self._send_json(data, status)
            elif path.startswith("/api/test/"):
                node = urllib.parse.unquote(path[len("/api/test/"):])
                data, status = _do_test_node(node)
                self._send_json(data, status)
            else:
                self._send_error_json(404, "Not found")
        except urllib.error.URLError as e:
            self._send_error_json(502, f"Clash API 连接失败: {e}")

    def do_PUT(self):
        if not self._check_ip():
            self._send_error_json(403, "IP not allowed")
            return
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        try:
            if path == "/api/switch":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length)) if length > 0 else {}
                group = body.get("group", "")
                node = body.get("node", "")
                if not group or not node:
                    self._send_error_json(400, "需要 group 和 node 参数")
                    return
                data, status = _do_switch(group, node)
                self._send_json(data, status)
            else:
                self._send_error_json(404, "Not found")
        except urllib.error.URLError as e:
            self._send_error_json(502, f"Clash API 连接失败: {e}")
        except json.JSONDecodeError:
            self._send_error_json(400, "无效的 JSON 请求体")


def _parse_allow_ip(value):
    networks = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "/" not in item:
            item = f"{item}/32"
        networks.append(ipaddress.ip_network(item, strict=False))
    return networks


def cmd_serve(args):
    """启动 HTTP API 服务"""
    if args.no_ip_limit:
        ClashAPIHandler.allowed_networks = None
        print("警告: 未设置 IP 白名单，所有 IP 均可访问")
    else:
        ClashAPIHandler.allowed_networks = _parse_allow_ip(args.allow_ip)
        print(f"IP 白名单: {args.allow_ip}")

    server = HTTPServer(("0.0.0.0", args.port), ClashAPIHandler)
    print(f"HTTP API 服务已启动: http://0.0.0.0:{args.port}")
    print(f"转发目标: {API_BASE}")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


def main():
    global API_BASE

    parser = argparse.ArgumentParser(
        description="Clash Verge 代理控制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s status                          # 查看当前状态
  %(prog)s list                            # 列出所有代理组
  %(prog)s list -v                         # 列出代理组及节点详情
  %(prog)s nodes                           # 列出所有节点及延迟
  %(prog)s switch SSRDOG "🇯🇵 Japan丨01"    # 切换 SSRDOG 组到日本01
  %(prog)s test "🇭🇰 Hong Kong丨01"        # 测试单个节点延迟
  %(prog)s test-group SSRDOG               # 测试代理组所有节点延迟
  %(prog)s serve --port 9098               # 启动 HTTP API 服务
  %(prog)s serve --port 9098 --allow-ip 192.168.1.0/24  # 限制访问 IP
""",
    )
    parser.add_argument(
        "--api", default=API_BASE, help=f"Clash API 地址 (默认: {API_BASE})"
    )
    sub = parser.add_subparsers(dest="command")

    p_status = sub.add_parser("status", help="显示当前状态概览")
    p_status.set_defaults(func=cmd_status)

    p_list = sub.add_parser("list", help="列出所有代理组")
    p_list.add_argument("-v", "--verbose", action="store_true", help="显示节点详情")
    p_list.set_defaults(func=cmd_list)

    p_nodes = sub.add_parser("nodes", help="列出所有节点及延迟")
    p_nodes.set_defaults(func=cmd_nodes)

    p_switch = sub.add_parser("switch", help="切换代理")
    p_switch.add_argument("group", help="代理组名称 (如 SSRDOG, GLOBAL)")
    p_switch.add_argument("node", help="目标节点名称")
    p_switch.set_defaults(func=cmd_switch)

    p_test = sub.add_parser("test", help="测试单个节点延迟")
    p_test.add_argument("node", help="节点名称")
    p_test.add_argument("--timeout", type=int, default=3000, help="超时(ms)")
    p_test.set_defaults(func=cmd_test)

    p_tg = sub.add_parser("test-group", help="测试代理组所有节点延迟")
    p_tg.add_argument("group", help="代理组名称")
    p_tg.add_argument("--url", default="http://1.1.1.1", help="测试URL")
    p_tg.add_argument("--timeout", type=int, default=3000, help="超时(ms)")
    p_tg.set_defaults(func=cmd_test_group)

    p_serve = sub.add_parser("serve", help="启动 HTTP API 服务")
    p_serve.add_argument("--port", type=int, default=9098, help="监听端口 (默认: 9098)")
    p_serve.add_argument("--allow-ip", default="192.168.1.0/24,127.0.0.1", help="允许访问的 IP/CIDR，逗号分隔 (默认: 192.168.1.0/24,127.0.0.1)")
    p_serve.add_argument("--no-ip-limit", action="store_true", help="禁用 IP 白名单，允许所有 IP 访问")
    p_serve.set_defaults(func=cmd_serve)

    p_sc = sub.add_parser("switch-country", help="按国家自动切换至可达节点")
    p_sc.add_argument("country", help="国家/地区 (如 us, jp, uk 或自定义)")
    p_sc.add_argument("--group", default="GLOBAL", help="代理组名称 (默认: GLOBAL)")
    p_sc.set_defaults(func=cmd_switch_country)

    args = parser.parse_args()
    if args.api != API_BASE:
        API_BASE = args.api

    if not args.command:
        parser.print_help()
        return

    try:
        result = args.func(args)
        sys.exit(result or 0)
    except urllib.error.URLError as e:
        print(f"连接失败: {e}")
        print(f"请确认 Clash 正在运行且外部控制地址为 {API_BASE}")
        sys.exit(1)


if __name__ == "__main__":
    main()
