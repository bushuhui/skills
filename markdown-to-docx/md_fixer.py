#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 格式修复器 — 在转 DOCX 前自动修正非标准 Markdown 格式

修复项：
  1. HTML 表格 → 标准 Markdown 表格
  2. 表格分隔行格式错误（如 ||-|||-| → |---|---|---|）
  3. 图片路径引用检查
  4. 其他非标准格式

用法：
    python md_fixer.py <input.md>
    或作为模块导入：
        from md_fixer import MarkdownFixer
        fixer = MarkdownFixer()
        fixed_content, report = fixer.fix(content)
"""

import re
import os
import sys
from typing import Tuple, List, Dict


class MarkdownFixer:
    """Markdown 格式修复器"""

    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.reports: List[str] = []
        self.fix_count: Dict[str, int] = {}

    def _log(self, msg: str, category: str = "fix"):
        self.reports.append(msg)
        self.fix_count[category] = self.fix_count.get(category, 0) + 1

    def fix(self, content: str) -> Tuple[str, List[str]]:
        """
        修复 Markdown 内容中的非标准格式

        Args:
            content: 原始 Markdown 内容

        Returns:
            (修复后的内容, 修复报告列表)
        """
        self.reports = []
        self.fix_count = {}

        # 1. HTML 表格 → Markdown 表格
        content = self._fix_html_tables(content)

        # 2. 修正非标准表格分隔行
        content = self._fix_table_separators(content)

        # 3. 检查图片引用
        content = self._fix_image_refs(content)

        if not self.reports:
            self.reports.append("✓ Markdown 格式检查通过，无需修复")

        return content, self.reports

    # ============================================================
    # 1. HTML 表格 → 标准 Markdown 表格
    # ============================================================

    def _fix_html_tables(self, content: str) -> str:
        """将 HTML 表格转换为标准 Markdown 表格"""
        # 匹配 HTML 表格
        table_pattern = re.compile(
            r'<table>(.*?)</table>',
            re.DOTALL | re.IGNORECASE
        )

        def convert_table(match):
            table_html = match.group(1)
            rows = []

            # 提取所有 tr
            tr_pattern = re.compile(
                r'<tr[^>]*>(.*?)</tr>',
                re.DOTALL | re.IGNORECASE
            )
            for tr_match in tr_pattern.finditer(table_html):
                tr_content = tr_match.group(1)
                cells = []

                # 提取 td 或 th
                cell_pattern = re.compile(
                    r'<t[dh][^>]*>(.*?)</t[dh]>',
                    re.DOTALL | re.IGNORECASE
                )
                for cell_match in cell_pattern.finditer(tr_content):
                    cell_text = cell_match.group(1)
                    # 清理嵌套 HTML 标签
                    cell_text = re.sub(r'<[^>]+>', '', cell_text)
                    # 清理多余空白
                    cell_text = re.sub(r'\s+', ' ', cell_text).strip()
                    cells.append(cell_text)

                if cells:
                    rows.append(cells)

            if not rows:
                return match.group(0)  # 无法解析，保留原样

            # 计算最大列数
            max_cols = max(len(row) for row in rows)
            # 补齐缺失的列
            for row in rows:
                while len(row) < max_cols:
                    row.append('')

            # 构建 Markdown 表格
            lines = []
            # 表头
            lines.append('| ' + ' | '.join(rows[0]) + ' |')
            # 分隔行
            lines.append('|' + '|'.join(['---'] * max_cols) + '|')
            # 数据行
            for row in rows[1:]:
                lines.append('| ' + ' | '.join(row) + ' |')

            md_table = '\n'.join(lines)
            self._log(f"转换 HTML 表格为 Markdown 表格（{len(rows)} 行，{max_cols} 列）", "html_table")
            return md_table

        return table_pattern.sub(convert_table, content)

    # ============================================================
    # 2. 修正非标准表格分隔行
    # ============================================================

    def _fix_table_separators(self, content: str) -> str:
        """修正表格分隔行为为标准格式（如 |---|---|）"""
        lines = content.split('\n')
        fixed_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # 检查是否是表格行（以 | 开头或包含 |）
            if '|' in line and line.strip().startswith('|'):
                # 找到完整的表格块
                table_start = i
                table_lines = []

                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1

                # 检查并修复分隔行
                if len(table_lines) >= 2:
                    header = table_lines[0]
                    separator = table_lines[1]

                    # 检查分隔行是否标准
                    if not self._is_valid_separator(separator):
                        # 计算列数
                        col_count = header.count('|') - 1
                        if col_count > 0:
                            new_separator = '|' + '|'.join(['---'] * col_count) + '|'
                            self._log(
                                f"修正表格分隔行: '{separator.strip()}' → '{new_separator}'",
                                "table_separator"
                            )
                            table_lines[1] = new_separator

                fixed_lines.extend(table_lines)
            else:
                fixed_lines.append(line)
                i += 1

        return '\n'.join(fixed_lines)

    def _is_valid_separator(self, line: str) -> bool:
        """检查是否是标准的 Markdown 表格分隔行"""
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            return False

        # 标准分隔行：|---|---| 或 | :-: | --- | 等
        # 每个单元格应该包含至少 3 个 - 字符，可以有 :
        cells = line[1:-1].split('|')
        for cell in cells:
            cell = cell.strip()
            if not cell:
                return False
            # 移除可选的 :
            cell = cell.replace(':', '')
            if len(cell) < 3 or not all(c == '-' for c in cell):
                return False

        return True

    # ============================================================
    # 3. 检查图片引用
    # ============================================================

    def _fix_image_refs(self, content: str) -> str:
        """检查图片引用路径，标记可能的问题"""
        # 匹配 Markdown 图片：![alt](path)
        img_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

        for match in img_pattern.finditer(content):
            alt_text = match.group(1)
            img_path = match.group(2)

            # 跳过 URL 图片
            if img_path.startswith(('http://', 'https://', 'data:')):
                continue

            # 检查本地文件是否存在
            if self.file_path:
                base_dir = os.path.dirname(os.path.abspath(self.file_path))
                full_path = os.path.join(base_dir, img_path)

                if not os.path.exists(full_path):
                    self._log(
                        f"⚠ 图片文件不存在: {img_path}（检查路径: {full_path}）",
                        "image_check"
                    )

        return content


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：python md_fixer.py <input.md>")
        print("检查并修复 Markdown 文件中的非标准格式")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"错误：文件不存在：{input_path}")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fixer = MarkdownFixer(input_path)
    fixed_content, reports = fixer.fix(content)

    # 输出报告
    print("=== Markdown 格式检查报告 ===")
    for report in reports:
        print(f"  {report}")

    # 统计
    print(f"\n总计修复 {sum(fixer.fix_count.values())} 处问题")
    for category, count in fixer.fix_count.items():
        print(f"  [{category}]: {count} 处")

    # 如果有修复，保存为 _fixed.md
    if sum(fixer.fix_count.values()) > 0:
        output_path = input_path.replace('.md', '_format_fixed.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"\n已保存修复后的文件: {output_path}")
    else:
        print("\n✓ 格式检查通过，无需修复")


if __name__ == '__main__':
    main()
