// Combines 재고(입고)/출하/출고 rows that match a predicate into one
// chronological list, so a material's or project's full flow can be
// read at a glance instead of three separate tables.
export function buildTimeline(rawData, matchers) {
  const items = [];

  rawData.재고.forEach((r) => {
    if (matchers.재고(r)) {
      items.push({
        date: r["입고일"] || "",
        type: "입고",
        prj: r["프로젝트번호"] || "",
        qty: r["입고수량"] || "",
        unit: r["단위"] || "",
        ref: r["구매요청번호"] || "",
        note: "",
        alert: false,
      });
    }
  });

  rawData.출하.forEach((r) => {
    if (matchers.출하(r)) {
      items.push({
        date: r["출하의뢰일"] || "",
        type: "출하",
        prj: r["프로젝트번호"] || "",
        qty: r["수량"] || "",
        unit: r["단위"] || "",
        ref: r["출하의뢰번호"] || "",
        note: r["비고"] || "",
        alert: false,
      });
    }
  });

  rawData.출고.forEach((r) => {
    if (matchers.출고(r)) {
      items.push({
        date: r["요청일"] || "",
        type: "출고",
        prj: r["프로젝트번호"] || "",
        qty: r["출고수량"] || "",
        unit: r["단위"] || "",
        ref: r["구매요청번호"] || "",
        note: r["비고"] || "",
        alert: r["출고수량"] === "0",
      });
    }
  });

  return items.sort((a, b) => a.date.localeCompare(b.date));
}

export const TYPE_TAG_CLASS = {
  입고: "tag-blue",
  출하: "tag-teal",
  출고: "tag-amber",
};
