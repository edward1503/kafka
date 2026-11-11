// Convert the theory Markdown only. Run with Node.js and the marked package.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';

const project = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(project, '../kafka-architecture.md');
const require = createRequire(import.meta.url);
const { marked } = await import(pathToFileURL(require.resolve('marked')).href);
const tokens = marked.lexer(fs.readFileSync(source, 'utf8'));
const imageSource = path.resolve(project, '../assets/images');
const images = path.join(project, 'images');
fs.mkdirSync(images, { recursive: true });
for (const name of fs.readdirSync(imageSource)) {
  fs.copyFileSync(path.join(imageSource, name), path.join(images, name));
}

function esc(value) {
  const map = { '\\': '\\textbackslash{}', '{': '\\{', '}': '\\}', '#': '\\#', '$': '\\$', '%': '\\%', '&': '\\&', '_': '\\_', '~': '\\textasciitilde{}', '^': '\\textasciicircum{}', '→': '\\ensuremath{\\rightarrow}', '×': '\\ensuremath{\\times}', '–': '--', '—': '---', '\u00a0': '~' };
  return String(value).replace(/[\\{}#$%&_~^→×–—\u00a0]/g, c => map[c]);
}
function code(value) {
  return '\\texttt{' + Array.from(value, c => c === '_' ? '\\_\\allowbreak{}' : /[./=-]/.test(c) ? esc(c) + '\\allowbreak{}' : esc(c)).join('') + '}';
}
function inline(list = []) {
  return list.map(t => {
    if (t.type === 'text' || t.type === 'escape') return t.tokens ? inline(t.tokens) : esc(t.text);
    if (t.type === 'strong') return '\\textbf{' + inline(t.tokens) + '}';
    if (t.type === 'em') return '\\emph{' + inline(t.tokens) + '}';
    if (t.type === 'codespan') return code(t.text);
    if (t.type === 'link') {
      if (!/^https?:\/\//i.test(t.href)) return inline(t.tokens);
      return '\\href{' + t.href.replace(/%/g, '\\%').replace(/#/g, '\\#') + '}{' + inline(t.tokens) + '}';
    }
    if (t.type === 'br') return '\\\\';
    throw new Error('Unsupported inline token: ' + t.type);
  }).join('');
}
let figures = 0, tables = 0, pending = null, started = false, bibliography = false;
const out = ['% Generated from kafka-architecture.md; lab and quiz are separate.\n\\begingroup\\small'];
function table(t) {
  tables++;
  const n = t.header.length;
  let widths = n === 2 ? [0.38,0.58] : n === 3 ? [0.22,0.32,0.40] : [0.26,0.12,0.10,0.44];
  if (t.header[0].text === 'Bước') widths = [0.08,0.58,0.28];
  const cols = widths.map(w => 'p{' + w + '\\linewidth}').join('');
  const row = cells => cells.map(c => inline(c.tokens)).join(' & ') + ' \\\\';
  const header = '\\rowcolor{rowLavender}\n' + t.header.map(c => '\\textbf{' + inline(c.tokens) + '}').join(' & ') + ' \\\\\n\\midrule\n';
  return (t.rows.length <= 4 ? '\\Needspace{10\\baselineskip}\n' : '') + '\\begingroup\\small\n\\renewcommand{\\arraystretch}{1.23}\n' +
    '\\begin{longtable}{@{}' + cols + '@{}}\n\\toprule\n' + header +
    '\\endfirsthead\n\\toprule\n' + header + '\\endhead\n' +
    '\\bottomrule\n\\endfoot\n' + t.rows.map(row).join('\n') + '\n\\end{longtable}\n\\endgroup';
}
for (const [index, t] of tokens.entries()) {
  if (t.type === 'space' || t.type === 'def') continue;
  if (t.type === 'heading') {
    if (t.depth === 1) continue;
    if (pending) throw new Error('Missing figure caption');
    if (!started) { out.push('\\endgroup\n\\clearpage\n\\tableofcontents\n\\clearpage'); started = true; }
    if (t.text.startsWith('Tài liệu tham khảo')) {
      bibliography = true;
      out.push('\\FloatBarrier\n\\clearpage\n\\section*{Tài liệu tham khảo và nguồn hình}\n\\addcontentsline{toc}{section}{Tài liệu tham khảo và nguồn hình}');
    } else {
      const heading = t.text.replace(/^\d+(?:\.\d+)*\.\s*/, '');
      const next = tokens.slice(index + 1).find(x => x.type !== 'space');
      const imageNext = next?.type === 'paragraph' && next.tokens?.length === 1 && next.tokens[0].type === 'image';
      const needed = imageNext ? '0.55\\textheight' : (t.depth === 2 ? '8' : '5') + '\\baselineskip';
      out.push('\\FloatBarrier\n\\Needspace{' + needed + '}\n\\' + (t.depth === 2 ? 'section' : 'subsection') + '{' + esc(heading) + '}');
    }
    continue;
  }
  if (t.type === 'paragraph') {
    if (t.tokens.length === 1 && t.tokens[0].type === 'image') {
      const name = path.basename(t.tokens[0].href);
      if (name === 'kafka-logo-horizontal.png') out.push('\\begin{center}\n\\includegraphics[width=2.6cm]{images/' + name + '}\n\\end{center}');
      else {
        const width = name === 'kafka-partition-log.png' ? '9.8cm' : name === 'kafka-consumer-groups.png' ? '12.5cm' : '\\linewidth';
        pending = '\\includegraphics[width=' + width + ',height=0.48\\textheight,keepaspectratio]{images/' + name + '}';
      }
      continue;
    }
    if (pending && /^\*Hình \d+\./.test(t.text)) {
      const caption = structuredClone(t.tokens[0].tokens);
      caption[0].text = caption[0].text.replace(/^Hình \d+\.\s*/, '');
      out.push('\\begin{figure}[!htbp]\n\\centering\n' + pending + '\n\\begin{figurecardcaptionaivn}\n\\capfig{' + inline(caption) + '}\n\\end{figurecardcaptionaivn}\n\\end{figure}');
      pending = null; figures++; continue;
    }
    if (!started && /^\*Biểu trưng/.test(t.text)) {
      out.push('\\begin{center}\\scriptsize ' + inline(t.tokens) + '\\end{center}'); continue;
    }
    if (!started && /^\*Từ sự kiện/.test(t.text)) {
      out.push('\\begin{center}\\large ' + inline(t.tokens) + '\\end{center}'); continue;
    }
    if (!started && /^\*\*Mục tiêu:/.test(t.text)) {
      out.push('\\begin{infobox}{Mục tiêu bài học}\n' + inline(t.tokens).replace(/^\\textbf\{Mục tiêu:\}\s*/, '').replace(/^sau /,'Sau ') + '\n\\end{infobox}'); continue;
    }
    out.push(inline(t.tokens) + '\n'); continue;
  }
  if (t.type === 'blockquote') {
    out.push('\\begin{notebox}\n' + t.tokens.filter(x=>x.type==='paragraph').map(x=>inline(x.tokens)).join('\n\n') + '\n\\end{notebox}'); continue;
  }
  if (t.type === 'table') { out.push(table(t)); continue; }
  if (t.type === 'code') {
    out.push('\\begin{aivncodebox}[language={}]{Ví dụ dữ liệu sự kiện (JSON)}\n' + t.text + '\n\\end{aivncodebox}'); continue;
  }
  if (t.type === 'list') {
    const env = t.ordered ? 'enumerate' : 'itemize';
    out.push((bibliography ? '\\begingroup\\small\n' : '') + '\\begin{' + env + '}\n' + t.items.map(item=>'\\item ' + item.tokens.filter(x=>x.type==='text'||x.type==='paragraph').map(x=>inline(x.tokens || marked.Lexer.lexInline(x.text))).join(' ')).join('\n') + '\n\\end{' + env + '}' + (bibliography ? '\n\\endgroup' : '')); continue;
  }
  throw new Error('Unsupported block: ' + t.type);
}
if (pending || figures !== 6 || tables !== 8) throw new Error(`Unexpected figures/tables: ${figures}/${tables}`);
// content.tex has been edited by hand (citations, thebibliography, extra subsection) and is now the
// canonical source. Regenerating from Markdown would drop those edits, so refuse unless forced.
const target = path.join(project, 'content.tex');
if (fs.existsSync(target) && fs.readFileSync(target, 'utf8').includes('\\begin{thebibliography}') && !process.argv.includes('--force')) {
  console.error('content.tex contains hand edits (thebibliography). Edit content.tex directly, or pass --force to overwrite it from Markdown.');
  process.exit(1);
}
fs.writeFileSync(target, out.join('\n\n')+'\n', 'utf8');
console.log(`Kafka theory: ${figures} figures, ${tables} tables; image assets copied.`);
