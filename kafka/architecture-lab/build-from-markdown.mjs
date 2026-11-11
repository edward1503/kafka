// Convert the hands-on Markdown into content.tex for the lab handout.
// Run with Node.js and the marked package: node kafka/architecture-lab/build-from-markdown.mjs
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';

const project = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(project, '../kafka-architecture-hands-on.md');
const require = createRequire(import.meta.url);
const { marked } = await import(pathToFileURL(require.resolve('marked')).href);
const tokens = marked.lexer(fs.readFileSync(source, 'utf8'));

function esc(value) {
  const map = { '\\': '\\textbackslash{}', '{': '\\{', '}': '\\}', '#': '\\#', '$': '\\$', '%': '\\%', '&': '\\&', '_': '\\_', '~': '\\textasciitilde{}', '^': '\\textasciicircum{}', '→': '\\ensuremath{\\rightarrow}', '×': '\\ensuremath{\\times}', '–': '--', '—': '---', '\u00a0': '~' };
  return String(value).replace(/[\\{}#$%&_~^→×–—\u00a0]/g, c => map[c]);
}
function code(value) {
  return '\\texttt{' + Array.from(value, c => c === '_' ? '\\_\\allowbreak{}' : /[./=|-]/.test(c) ? esc(c) + '\\allowbreak{}' : esc(c)).join('') + '}';
}
function inline(list = []) {
  return list.map(t => {
    if (t.type === 'text' || t.type === 'escape') return t.tokens ? inline(t.tokens) : esc(t.text);
    if (t.type === 'strong') return '\\textbf{' + inline(t.tokens) + '}';
    if (t.type === 'em') return '\\emph{' + inline(t.tokens) + '}';
    if (t.type === 'codespan') return code(t.text.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>'));
    if (t.type === 'link') {
      if (/^[A-Z]:\//i.test(t.href)) return inline(t.tokens);
      return '\\href{' + t.href.replace(/%/g, '\\%').replace(/#/g, '\\#') + '}{' + inline(t.tokens) + '}';
    }
    if (t.type === 'br') return '\\\\';
    throw new Error('Unsupported inline token: ' + t.type);
  }).join('');
}
function widths(t) {
  const head = t.header.map(c => c.text).join('|');
  if (head === 'Phần|Nội dung|Thời gian|Mục lý thuyết') return [0.07, 0.48, 0.15, 0.20];
  if (head === 'Mã|Bằng chứng|Phần') return [0.15, 0.65, 0.12];
  if (t.header.length === 2) return [0.40, 0.56];
  throw new Error('No column widths for table: ' + head);
}
function table(t) {
  const cols = widths(t).map(w => 'p{' + w + '\\linewidth}').join('');
  const row = cells => cells.map(c => inline(c.tokens)).join(' & ') + ' \\\\';
  const header = '\\rowcolor{rowLavender}\n' + t.header.map(c => '\\textbf{' + inline(c.tokens) + '}').join(' & ') + ' \\\\\n\\midrule\n';
  return (t.rows.length <= 6 ? '\\Needspace{12\\baselineskip}\n' : '') + '\\begingroup\\small\n\\renewcommand{\\arraystretch}{1.2}\n' +
    '\\begin{longtable}{@{}' + cols + '@{}}\n\\toprule\n' + header +
    '\\endfirsthead\n\\toprule\n' + header + '\\endhead\n' +
    '\\bottomrule\n\\endfoot\n' + t.rows.map(row).join('\n') + '\n\\end{longtable}\n\\endgroup';
}

let started = false, tables = 0, commands = 0, outputs = 0, questions = 0;
const out = ['% Generated from kafka-architecture-hands-on.md by build-from-markdown.mjs. Edit the Markdown, not this file.'];
for (const t of tokens) {
  if (t.type === 'space' || t.type === 'def') continue;
  if (t.type === 'heading') {
    if (t.depth === 1) continue;
    if (!started) { out.push('\\tableofcontents\n\\clearpage'); started = true; }
    if (t.text.startsWith('Tài liệu tham khảo')) {
      out.push('\\section*{Tài liệu tham khảo}\n\\addcontentsline{toc}{section}{Tài liệu tham khảo}');
      continue;
    }
    const heading = t.text.replace(/^\d+(?:\.\d+)*\.\s*/, '');
    const cmd = t.depth === 2 ? 'section' : 'subsection';
    out.push('\\Needspace{' + (t.depth === 2 ? 10 : 7) + '\\baselineskip}\n\\' + cmd + '{' + inline(marked.Lexer.lexInline(heading)) + '}');
    continue;
  }
  if (t.type === 'paragraph') {
    const text = t.text;
    if (!started && /^\*Tạo topic/.test(text)) { out.push('\\begin{center}\\large ' + inline(t.tokens) + '\\end{center}'); continue; }
    if (!started && /^\*\*Mục tiêu:/.test(text)) {
      out.push('\\begin{infobox}{Mục tiêu buổi lab}\n' + inline(t.tokens).replace(/^\\textbf\{Mục tiêu:\}\s*/, '').replace(/^sau /, 'Sau ') + '\n\\end{infobox}');
      continue;
    }
    const q = text.match(/^\*\*(Q\d+)\.\*\*\s*/);
    if (q) {
      questions++;
      const body = structuredClone(t.tokens).slice(1);
      if (body[0]?.type === 'text') body[0].text = body[0].text.replace(/^\s+/, '');
      out.push('\\begin{questionbox}{Câu hỏi ' + q[1] + '.}\n' + inline(body) + '\n\\end{questionbox}');
      continue;
    }
    if (/^\*\*(E\d|Điểm kiểm tra)/.test(text)) { out.push('\\begin{evidencebox}\n' + inline(t.tokens) + '\n\\end{evidencebox}'); continue; }
    if (/^\*\*Cửa sổ [A-D]/.test(text)) { out.push('\\Needspace{6\\baselineskip}\n' + inline(t.tokens) + '\\par\\nopagebreak'); continue; }
    out.push(inline(t.tokens) + '\n');
    continue;
  }
  if (t.type === 'blockquote') {
    out.push('\\begin{notebox}\n' + t.tokens.filter(x => x.type === 'paragraph').map(x => inline(x.tokens)).join('\n\n') + '\n\\end{notebox}');
    continue;
  }
  if (t.type === 'table') { tables++; out.push(table(t)); continue; }
  if (t.type === 'code') {
    if (/[^\x00-\x7F]/.test(t.text)) throw new Error('Non-ASCII character in code block (listings cannot typeset it):\n' + t.text);
    const body = t.text.replace(/\t/g, '  ');
    if (t.lang === 'powershell') { commands++; out.push('\\begin{aivncodebox}[language={}]{PowerShell}\n' + body + '\n\\end{aivncodebox}'); }
    else if (t.lang === 'text') { outputs++; out.push('\\begin{aivnCodeOutput}{Kết quả quan sát (lượt chạy 10/11/2026)}\n' + body + '\n\\end{aivnCodeOutput}'); }
    else throw new Error('Unsupported code language: ' + t.lang);
    continue;
  }
  if (t.type === 'list') {
    const env = t.ordered ? 'enumerate' : 'itemize';
    out.push('\\begin{' + env + '}\n' + t.items.map(item => '\\item ' + item.tokens.filter(x => x.type === 'text' || x.type === 'paragraph').map(x => inline(x.tokens || marked.Lexer.lexInline(x.text))).join(' ')).join('\n') + '\n\\end{' + env + '}');
    continue;
  }
  throw new Error('Unsupported block: ' + t.type);
}
if (tables !== 4 || questions !== 8) throw new Error(`Unexpected tables/questions: ${tables}/${questions}`);
fs.writeFileSync(path.join(project, 'content.tex'), out.join('\n\n') + '\n', 'utf8');
console.log(`Kafka lab: ${tables} tables, ${commands} command blocks, ${outputs} output blocks, ${questions} questions.`);
