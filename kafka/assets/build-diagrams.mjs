import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const bundled = createRequire(import.meta.url);
const sharp = bundled('sharp');
const directory = path.join(path.dirname(fileURLToPath(import.meta.url)), 'images');
const navy = '#173547';
const green = '#087F72';
const orange = '#BC5B21';

function svg(width, height, contents) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="${green}"/></marker><marker id="meta-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="${orange}"/></marker></defs>
  <rect width="100%" height="100%" rx="20" fill="#F4F8FA"/>
  <g font-family="Segoe UI, Arial, sans-serif" fill="${navy}">${contents}</g></svg>`;
}

const architecture = svg(1500, 760, `
  <text x="58" y="64" font-size="34" font-weight="700">Kafka: luồng dữ liệu và vai trò của cluster</text>
  <text x="58" y="104" font-size="22" fill="#526977">Ví dụ: sự kiện đơn hàng được nhiều ứng dụng đọc độc lập.</text>
  <rect x="512" y="150" width="475" height="110" rx="16" fill="#FFF1E6" stroke="${orange}" stroke-width="2"/>
  <text x="750" y="193" font-size="26" font-weight="700" text-anchor="middle">Controller quorum · KRaft</text>
  <text x="750" y="231" font-size="22" text-anchor="middle">Quản lý metadata của cluster</text>
  <path d="M750 260 V325" fill="none" stroke="${orange}" stroke-width="3" stroke-dasharray="9 7" marker-end="url(#meta-arrow)"/>
  <rect x="58" y="366" width="292" height="160" rx="16" fill="white" stroke="${navy}" stroke-width="2"/>
  <text x="204" y="410" font-size="27" font-weight="700" text-anchor="middle">Producer</text>
  <text x="204" y="452" font-size="23" text-anchor="middle">Dịch vụ đơn hàng</text>
  <text x="204" y="491" font-size="22" text-anchor="middle" fill="#526977">Gửi record có key</text>
  <rect x="466" y="327" width="568" height="259" rx="20" fill="#E5F3EF" stroke="${green}" stroke-width="2"/>
  <text x="750" y="373" font-size="28" font-weight="700" text-anchor="middle">Kafka cluster · topic order-events</text>
  ${[504, 678, 852].map((x,i)=>`<rect x="${x}" y="403" width="144" height="114" rx="12" fill="white" stroke="${green}" stroke-width="2"/><text x="${x+72}" y="448" font-size="24" font-weight="600" text-anchor="middle">Broker ${i+1}</text><text x="${x+72}" y="488" font-size="21" text-anchor="middle">Lưu replica</text>`).join('')}
  <text x="750" y="557" font-size="21" text-anchor="middle">Record được lưu trong log của các partition</text>
  <path d="M350 446 H452" fill="none" stroke="${green}" stroke-width="4" marker-end="url(#arrow)"/>
  <text x="402" y="421" font-size="20" text-anchor="middle">Ghi</text>
  <rect x="1150" y="318" width="292" height="139" rx="16" fill="white" stroke="${green}" stroke-width="2"/>
  <text x="1296" y="358" font-size="24" font-weight="700" text-anchor="middle">Consumer group A</text>
  <text x="1296" y="396" font-size="23" text-anchor="middle">Xử lý tồn kho</text>
  <text x="1296" y="432" font-size="20" fill="#526977" text-anchor="middle">Offset riêng của nhóm</text>
  <rect x="1150" y="491" width="292" height="139" rx="16" fill="white" stroke="${green}" stroke-width="2"/>
  <text x="1296" y="531" font-size="24" font-weight="700" text-anchor="middle">Consumer group B</text>
  <text x="1296" y="569" font-size="23" text-anchor="middle">Phân tích doanh thu</text>
  <text x="1296" y="605" font-size="20" fill="#526977" text-anchor="middle">Offset riêng của nhóm</text>
  <path d="M1034 423 H1090 V387 H1137 M1090 423 V560 H1137" fill="none" stroke="${green}" stroke-width="4" marker-end="url(#arrow)"/>
  <path d="M1090 387 H1137" fill="none" stroke="${green}" stroke-width="4" marker-end="url(#arrow)"/>
  <text x="1090" y="367" font-size="20" text-anchor="middle">Đọc</text>
  <path d="M60 684 H126" stroke="${green}" stroke-width="4" marker-end="url(#arrow)"/>
  <text x="143" y="692" font-size="21">Luồng record (consumer chủ động fetch)</text>
  <path d="M760 684 H826" stroke="${orange}" stroke-width="3" stroke-dasharray="9 7" marker-end="url(#meta-arrow)"/>
  <text x="844" y="692" font-size="21">Quản lý metadata</text>
  <text x="58" y="735" font-size="18" fill="#526977">Sơ đồ khái niệm; không mô tả đầy đủ kết nối mạng, số controller hay cấu hình triển khai.</text>
`);

const replicaRows = [
  { name:'P0', leader:0, y:227 },
  { name:'P1', leader:1, y:342 },
  { name:'P2', leader:2, y:457 },
];
const replication = svg(1440, 720, `
  <text x="58" y="65" font-size="34" font-weight="700">Partition và replica: hai cách đếm khác nhau</text>
  <text x="58" y="105" font-size="22" fill="#526977">Một topic có 3 partition; replication factor = 3; minh họa trên 3 broker.</text>
  ${[58,520,982].map((x,i)=>`<rect x="${x}" y="148" width="400" height="433" rx="18" fill="white" stroke="#B9CBD4" stroke-width="2"/><text x="${x+200}" y="195" font-size="28" font-weight="700" text-anchor="middle">Broker ${i+1}</text>`).join('')}
  ${replicaRows.map(row=>[58,520,982].map((x,i)=>`<rect x="${x+22}" y="${row.y}" width="356" height="88" rx="12" fill="${i===row.leader?green:'#EAF0F4'}"/><text x="${x+200}" y="${row.y+37}" font-size="26" font-weight="700" fill="${i===row.leader?'white':navy}" text-anchor="middle">${row.name} · ${i===row.leader?'LEADER':'FOLLOWER'}</text><text x="${x+200}" y="${row.y+69}" font-size="20" fill="${i===row.leader?'white':'#526977'}" text-anchor="middle">${i===row.leader?'Nhận ghi cho partition này':'Sao chép log từ leader của '+row.name}</text>`).join('')).join('')}
  <text x="720" y="628" font-size="27" font-weight="700" text-anchor="middle">3 partition × 3 replica = 9 bản sao, trong đó có 3 leader</text>
  <text x="720" y="672" font-size="22" text-anchor="middle" fill="#526977">Mỗi partition có một leader và hai follower; các replica của nó nằm trên broker khác nhau.</text>
  <text x="58" y="707" font-size="18" fill="#526977">Sơ đồ minh họa; ISR có thể là một tập con của các replica được gán.</text>
`);

await fs.mkdir(directory, {recursive:true});
for (const [name, content] of [['kafka-architecture-overview', architecture], ['kafka-partition-replication', replication]]) {
  await fs.writeFile(path.join(directory, `${name}.svg`), content, 'utf8');
  await sharp(Buffer.from(content)).png().toFile(path.join(directory, `${name}.png`));
  console.log(`${name}: SVG + PNG`);
}
