#!/usr/bin/env python3
"""
pi-memory 知识库搜索（并行多查询版）

用法:
    python3 scripts/knowledge_search.py "无人机控制"
    python3 scripts/knowledge_search.py --queries "无人机控制" "UAV control" "drone导航"
    python3 scripts/knowledge_search.py --queries "无人机" "UAV" "drone" --limit 100
    python3 scripts/knowledge_search.py "强化学习" --server http://192.168.1.10:9873 --raw
"""

import argparse, json, sys, concurrent.futures
from collections import Counter
from urllib.request import Request, urlopen

DEFAULT_SERVER = "http://agent.adv-ci.com:9873"


def search_one(server: str, query: str, limit: int = 30) -> dict:
    """单次 API 调用"""
    try:
        data = json.dumps({"query": query, "limit": limit}).encode()
        req = Request(f"{server}/api/knowledge/search",
            data=data, headers={"Content-Type": "application/json"})
        resp = urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"success": False, "error": str(e)}


def multi_query_search(queries: list[str], limit: int = 100, server: str = DEFAULT_SERVER) -> dict:
    """并行多查询搜索 → 去重合并 → 按分数排序"""
    per_query_limit = limit * 2 if len(queries) > 1 else limit

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(queries)) as pool:
        futures = {pool.submit(search_one, server, q, per_query_limit): q for q in queries}
        all_results = []
        for f in concurrent.futures.as_completed(futures):
            r = f.result()
            if r.get("success"):
                all_results.extend(r["data"]["results"])

    # 按 chunk ID 去重，保留最高分
    seen = {}
    for item in all_results:
        cid = item["id"]
        if cid not in seen or item["score"] > seen[cid]["score"]:
            seen[cid] = item

    results = sorted(seen.values(), key=lambda x: -x["score"])[:limit]
    return {
        "success": True,
        "data": {"count": len(results), "queries": queries, "results": results}
    }


def format_results(result: dict, verbose: int = 3) -> str:
    """格式化输出结果"""
    if not result.get("success"):
        return f"❌ 搜索失败: {result.get('error', '未知错误')}"

    data = result["data"]
    lines = []
    lines.append(f"📋 查询: {', '.join(data['queries'])}")
    lines.append(f"📊 返回结果: {data['count']} 条")
    lines.append("")

    # 文件分布
    files = Counter(r["filePath"] for r in data["results"])
    lines.append("=== 命中文件分布 ===")
    for path, cnt in sorted(files.items(), key=lambda x: -x[1]):
        name = path.split("/")[-1]
        best = max(r["score"] for r in data["results"] if r["filePath"] == path)
        lines.append(f"  {name:50s} {cnt:3d}  best={best:.3f}")
    lines.append("")

    # 详细结果
    if verbose > 0:
        lines.append("=== 最相关片段 ===")
        for i, r in enumerate(data["results"][:verbose]):
            text_preview = r["text"].strip()[:300].replace("\n", " ")
            lines.append(f"{i+1}. [{r['score']:.3f}] {r['filePath']}")
            lines.append(f"   {text_preview}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="pi-memory 知识库并行搜索")
    parser.add_argument("query", nargs="?", help="搜索关键词（无 --queries 时使用）")
    parser.add_argument("--queries", nargs="+", help="多个搜索关键词（由调用者扩展）")
    parser.add_argument("--limit", type=int, default=100, help="返回结果数量（默认100）")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="服务器地址")
    parser.add_argument("--raw", action="store_true", help="输出原始 JSON")
    parser.add_argument("--verbose", type=int, default=3, help="显示详细结果数量（默认3）")
    args = parser.parse_args()

    if args.queries:
        queries = args.queries
    elif args.query:
        queries = [args.query]
    else:
        parser.error("需要提供搜索关键词")

    result = multi_query_search(queries, args.limit, args.server)

    if args.raw:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_results(result, args.verbose))


if __name__ == "__main__":
    main()
