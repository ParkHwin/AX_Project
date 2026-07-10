import { TYPE_TAG_CLASS } from "../utils/timeline.js";

export default function TimelineTable({ items, emptyLabel }) {
  if (items.length === 0) {
    return (
      <div style={{ color: "#94a3b8", fontSize: "11px", padding: "6px 0" }}>
        {emptyLabel}
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table className="mini-table timeline-table">
        <tbody>
          <tr>
            <th>날짜</th>
            <th>구분</th>
            <th>프로젝트</th>
            <th>수량</th>
            <th>참조번호</th>
          </tr>
          {items.map((it, i) => (
            <tr key={i}>
              <td>{it.date || "-"}</td>
              <td>
                <span className={`tag ${TYPE_TAG_CLASS[it.type]}`}>{it.type}</span>
              </td>
              <td style={{ fontSize: "10px" }}>{it.prj || "-"}</td>
              <td>
                {it.alert ? (
                  <span className="tag tag-red">0 EA ⚠</span>
                ) : (
                  `${it.qty || 0} ${it.unit}`
                )}
              </td>
              <td style={{ fontSize: "10px" }}>
                {it.ref || <span className="tag tag-amber">미연결</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
