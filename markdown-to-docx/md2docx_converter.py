#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown to DOCX Converter with LaTeX Formula Support

将 Markdown 文件（含 LaTeX 公式）转换为 Word DOCX 文件
使用 pandoc 将 LaTeX 公式转换为 Word 原生 OMML 格式

用法：
    python md2docx_converter.py <input.md> [output.docx]
"""

import sys
import os
import re
import subprocess
from typing import Tuple, List, Optional


class MarkdownFormulaFixer:
    """Markdown LaTeX 公式修正器"""

    def __init__(self):
        # 常见的 LaTeX 公式错误模式
        self.patterns = [
            # 数字间多余空格：1 . 8 -> 1.8
            (r'\$(.*?)\$' , self._fix_inline_math),
            (r'\$\$(.*?)\$\$' , self._fix_display_math),
        ]

    def _fix_number_spacing(self, text: str) -> str:
        """修正数字间的空格问题"""
        # 匹配数字间有空格的情况，如 "1 . 8" -> "1.8"
        # 匹配模式：数字 + 空格 + 标点/数字 + 空格 + 数字
        result = text

        # 处理小数点周围的空格
        result = re.sub(r'(\d)\s+\.\s+(\d)', r'\1.\2', result)

        # 处理逗号周围的空格（在数字之间）
        result = re.sub(r'(\d)\s+\,\s+(\d)', r'\1,\2', result)

        # 处理百分号前的空格
        result = re.sub(r'(\d)\s+(\%)', r'\1\2', result)

        # 处理下标中的多余空格：_{ x } -> _{x}
        result = re.sub(r'_\s*\{\s*([a-zA-Z0-9]+)\s*\}', r'_{\1}', result)

        # 处理上标中的多余空格
        result = re.sub(r'\^\s*\{\s*([a-zA-Z0-9]+)\s*\}', r'^{\1}', result)

        return result

    def _fix_matrix_environment(self, text: str) -> str:
        """修正矩阵环境"""
        # 将错误的 \lceil 替换为正确的矩阵环境
        if r'\lceil' in text and r'\rceil' in text:
            # 尝试转换为 bmatrix
            text = re.sub(
                r'\\lceil\s*(.*?)\s*\\rceil',
                r'\\begin{bmatrix}\1\\end{bmatrix}',
                text,
                flags=re.DOTALL
            )
        return text

    def _fix_bold_symbols(self, text: str) -> str:
        """修正粗体符号格式"""
        # 统一向量符号表示
        # \boldsymbol { P _ { a } } -> \mathbf{P}_a 或保持 \boldsymbol{P_a}
        text = re.sub(r'\\boldsymbol\s*\{\s*\\?([a-zA-Z])\s*_\s*\{\s*([a-zA-Z0-9]+)\s*\}\s*\}',
                      r'\\mathbf{\1}_{\2}', text)
        return text

    def _fix_inline_math(self, match: re.Match) -> str:
        """修正行内数学公式"""
        content = match.group(1)
        fixed = self._fix_number_spacing(content)
        fixed = self._fix_matrix_environment(fixed)
        fixed = self._fix_bold_symbols(fixed)
        return f'${fixed}$'

    def _fix_display_math(self, match: re.Match) -> str:
        """修正块级数学公式"""
        content = match.group(1)
        fixed = self._fix_number_spacing(content)
        fixed = self._fix_matrix_environment(fixed)
        fixed = self._fix_bold_symbols(fixed)
        return f'$${fixed}$$'

    def fix(self, content: str) -> Tuple[str, List[str]]:
        """
        修正 Markdown 内容中的 LaTeX 公式

        返回：修正后的内容和问题列表
        """
        issues = []

        # 记录原始内容用于比较
        original_lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(original_lines):
            original_line = line

            # 检查是否包含数学公式
            if '$' in line:
                # 应用修正
                line = re.sub(r'\$([^$]+)\$', self._fix_inline_math_helper, line)
                line = re.sub(r'\$\$(.+?)\$\$', self._fix_display_math_helper, line, flags=re.DOTALL)

                if line != original_line:
                    issues.append(f"第{i+1}行：修正了公式格式")

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), issues

    def _fix_inline_math_helper(self, match: re.Match) -> str:
        """行内公式修正辅助函数"""
        content = match.group(1)
        fixed = self._fix_number_spacing(content)
        return f'${fixed}$'

    def _fix_display_math_helper(self, match: re.Match) -> str:
        """块级公式修正辅助函数"""
        content = match.group(1)
        fixed = self._fix_number_spacing(content)
        return f'$${fixed}$$'


class MarkdownToDocxConverter:
    """Markdown to DOCX 转换器"""

    def __init__(self, input_path: str, output_path: Optional[str] = None):
        self.input_path = input_path
        self.output_path = output_path or self._get_default_output_path()
        self.fixer = MarkdownFormulaFixer()

    def _get_default_output_path(self) -> str:
        """获取默认输出路径"""
        base, _ = os.path.splitext(self.input_path)
        # 如果输入是 _cn.md 结尾，输出为 _cn.docx
        if base.endswith('_cn') or base.endswith('_fixed'):
            return base + '.docx'
        return base + '.docx'

    def check_pandoc(self) -> bool:
        """检查 pandoc 是否已安装"""
        try:
            result = subprocess.run(
                ['pandoc', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def fix_formulas(self) -> Tuple[str, List[str]]:
        """读取并修正公式"""
        with open(self.input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed_content, issues = self.fixer.fix(content)
        return fixed_content, issues

    def save_fixed_markdown(self, fixed_content: str, output_path: Optional[str] = None) -> str:
        """保存修正后的 Markdown"""
        output = output_path or self.input_path.replace('.md', '_fixed.md')
        with open(output, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return output

    def convert_to_docx(self, use_fixed: bool = True) -> str:
        """
        转换为 DOCX 格式

        Args:
            use_fixed: 是否先修正公式再转换

        Returns:
            输出的 DOCX 文件路径
        """
        if not self.check_pandoc():
            raise RuntimeError("pandoc 未安装，请先安装：sudo apt install pandoc 或访问 https://pandoc.org")

        # 确定输入文件
        if use_fixed:
            fixed_content, issues = self.fix_formulas()
            if issues:
                print(f"发现并修正了 {len(issues)} 个公式格式问题")
                for issue in issues[:5]:  # 只显示前 5 个
                    print(f"  - {issue}")

            # 保存临时修正文件
            temp_path = self.input_path.replace('.md', '_temp_fixed.md')
            self.save_fixed_markdown(fixed_content, temp_path)
            input_file = temp_path
        else:
            input_file = self.input_path

        # 构建 pandoc 命令
        cmd = [
            'pandoc',
            input_file,
            '-o', self.output_path,
            '--mathml',  # 使用 MathML（Word 支持）
        ]

        print(f"执行转换：{' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise RuntimeError(f"pandoc 转换失败：{result.stderr}")

            # 清理临时文件
            if use_fixed and os.path.exists(temp_path):
                os.remove(temp_path)

            print(f"转换成功：{self.output_path}")
            return self.output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("转换超时，文件可能过大")

    def convert(self, fix_first: bool = True) -> str:
        """
        完整转换流程

        Args:
            fix_first: 是否先修正公式

        Returns:
            输出的 DOCX 文件路径
        """
        if fix_first:
            # 先修正公式
            fixed_content, issues = self.fix_formulas()

            # 保存修正后的 Markdown
            fixed_md_path = self.input_path.replace('.md', '_fixed.md')
            self.save_fixed_markdown(fixed_content, fixed_md_path)
            print(f"已保存修正后的 Markdown: {fixed_md_path}")

            if issues:
                print(f"\n发现并修正了 {len(issues)} 个公式格式问题")

        # 转换为 DOCX
        self.convert_to_docx(use_fixed=fix_first)

        return self.output_path


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：python md2docx_converter.py <input.md> [output.docx]")
        print("\n示例:")
        print("  python md2docx_converter.py paper.md")
        print("  python md2docx_converter.py paper.md output.docx")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_path):
        print(f"错误：文件不存在：{input_path}")
        sys.exit(1)

    converter = MarkdownToDocxConverter(input_path, output_path)

    try:
        result = converter.convert(fix_first=True)
        print(f"\n转换完成：{result}")
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
