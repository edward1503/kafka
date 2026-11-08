import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const exam = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(exam);
const solution = path.join(root, 'architecture-solution');
const items = JSON.parse(fs.readFileSync(path.join(exam, 'quiz-data.json'), 'utf8'));
const letters = ['A','B','C','D'];
if (items.length !== 10) throw new Error('Expected 10 questions');
for (const [index,item] of items.entries()) {
  if (item.id !== index+1 || item.options.length !== 4 || !letters.includes(item.answer)) throw new Error('Invalid question');
  if (new Set(item.options).size !== 4) throw new Error('Duplicate choices');
}
function escape(s) {
  const m = {'\\':'\\textbackslash{}','{':'\\{','}':'\\}','&':'\\&','%':'\\%','$':'\\$','#':'\\#','_':'\\_','~':'\\textasciitilde{}','^':'\\textasciicircum{}','–':'--','—':'---'};
  return String(s).replace(/[\\{}&%$#_~^–—]/g,c=>m[c]);
}
function inline(s) {
  return String(s).split('`').map((part,i)=>i%2?'\\texttt{'+escape(part)+'}':escape(part)).join('');
}
const questionText = s => s.split('\n\n').map(inline).join('\\par\\smallskip\n');
function questionWithDiagram(item) {
  if (!item.diagram) return questionText(item.question);
  const [context, prompt] = item.question.split('\n\n');
  return inline(context) + '\n\\par\\smallskip\n\\noindent\\makebox[\\linewidth][c]{\\includegraphics[width=0.96\\linewidth]{' +
    item.diagram + '}}\\par\\smallskip\n' + inline(prompt);
}
function markdownQuestion(item) {
  if (!item.diagram) return item.question;
  const [context, prompt] = item.question.split('\n\n');
  return context + '\n\n![' + item.diagramAlt + '](<' +
    item.diagram + '>)\n\n' + prompt;
}
const questions = items.map(item=>'\\noindent\\begin{minipage}{\\linewidth}\n\\small\n' +
  '\\textbf{Câu ' + item.id + '.} ' + questionWithDiagram(item) + '\n' +
  '\\begin{enumerate}[label=\\textbf{\\Alph*.},leftmargin=2em,itemsep=0pt,topsep=2pt]\n' +
  item.options.map(s=>'\\item '+inline(s)).join('\n') + '\n\\end{enumerate}\n' +
  '\\end{minipage}\\par\\addvspace{0.5em}\n').map((block, index) => index === 6 ? '\\Needspace{16\\baselineskip}\n\\section*{Vận dụng: phân tích tình huống}\n' + block : block).join('\n');
fs.writeFileSync(path.join(exam,'questions.tex'),'% Exam only: four unmarked choices per question.\n'+questions,'utf8');
let solutions = String.raw`\begin{infobox}{Bảng đáp án}
\begin{tabularx}{\linewidth}{@{}*{10}{>{\centering\arraybackslash}X}@{}}
`;
solutions += items.map(x=>'\\textbf{'+x.id+'}').join(' & ')+' \\\\\n\\midrule\n';
solutions += items.map(x=>'\\textbf{'+x.answer+'}').join(' & ')+' \\\\\n\\end{tabularx}\n\\end{infobox}\n';
solutions += '\\section*{Giải thích đáp án}\n';
solutions += items.map(item=>'\\Needspace{7\\baselineskip}\n' +
  '\\noindent\\textbf{Câu '+item.id+'. Đáp án '+item.answer+' --- '+escape(item.topic)+'}\\par\n' +
  '\\noindent\\emph{'+inline(item.options[letters.indexOf(item.answer)])+'}\\par\n' +
  inline(item.explanation)+'\\par\\addvspace{0.8em}\n').join('\n');
fs.writeFileSync(path.join(solution,'solutions.tex'),solutions,'utf8');
const intro = '# Quiz trắc nghiệm: Kiến trúc Apache Kafka\n\n' +
  '**Hình thức:** 10 câu hỏi, mỗi câu có bốn lựa chọn A/B/C/D. Chọn một đáp án đúng nhất cho mỗi câu. Câu 7–10 yêu cầu phân tích tình huống.\n\n' +
  '**Bài đọc nền tảng:** [Kiến trúc Apache Kafka](kafka-architecture.md).\n\n' +
  '**Phạm vi:** mốc tài liệu Kafka 4.1; consumer group là nhóm KafkaConsumer thông thường, không bao gồm share groups.\n\n';
fs.writeFileSync(path.join(root,'kafka-architecture-quiz.md'),intro+items.map(item => (item.id === 7 ? '## Vận dụng: phân tích tình huống\n\n' : '') + '## Câu '+item.id+'\n\n'+markdownQuestion(item)+'\n\n'+item.options.map((s,i)=>letters[i]+'. '+s).join('\n\n')).join('\n\n')+'\n','utf8');
const mdSolutions = '# Solution: Kiến trúc Apache Kafka\n\n' +
  '**Đề trắc nghiệm:** [Quiz ôn tập](kafka-architecture-quiz.md).\n\n' +
  '## Bảng đáp án\n\n| Câu | '+items.map(x=>x.id).join(' | ')+' |\n| --- | '+items.map(()=>'---').join(' | ')+' |\n| Đáp án | '+items.map(x=>x.answer).join(' | ')+' |\n\n' +
  '## Giải thích\n\n'+items.map(item=>'### Câu '+item.id+' - Đáp án '+item.answer+'\n\n**'+item.topic+'.** '+item.options[letters.indexOf(item.answer)]+'\n\n'+item.explanation).join('\n\n')+'\n';
fs.writeFileSync(path.join(root,'kafka-architecture-solution.md'),mdSolutions,'utf8');
console.log('Kafka quiz: 10 questions, 40 choices; separate Markdown and TeX solutions.');
