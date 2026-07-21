const BE = "http://localhost:8000";

export async function uploadWaferImage(file, user_num) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BE}/api/upload?user_num=${user_num}`, {
    method: "POST",
    body: form,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "업로드 실패");
  return data; // { image_id, class_id, class_name, confidence }
}

export async function getAnalysisList(user_num, page = 1, size = 100) {
  const res = await fetch(`${BE}/api/analyses?user_num=${user_num}&page=${page}&size=${size}`);
  if (!res.ok) throw new Error("이력 조회 실패");
  return res.json();
}

export async function getAnalysisDetail(analysis_id, user_num) {
  const res = await fetch(`${BE}/api/analyses/${analysis_id}?user_num=${user_num}`);
  if (!res.ok) throw new Error("상세 조회 실패");
  return res.json();
}

export async function getDashboard(user_num) {
  const res = await fetch(`${BE}/api/analyses/dashboard?user_num=${user_num}`);
  if (!res.ok) throw new Error("대시보드 조회 실패");
  return res.json();
}

export function getImageUrl(image_id) {
  return `${BE}/api/analyses/images/${image_id}`;
}
