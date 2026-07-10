import { useRef, useState } from "react";
import { FILE_LABEL } from "../constants.js";

export default function UploadArea({ uploadedFiles, onFiles, onRemove }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const openPicker = () => inputRef.current?.click();

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      /\.xlsx?$/i.test(f.name),
    );
    if (files.length) onFiles(files);
  };

  const handleChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length) onFiles(files);
    e.target.value = "";
  };

  return (
    <div
      className={`upload-area${dragOver ? " dragover" : ""}`}
      onClick={openPicker}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      <div className="upload-icon">📂</div>
      <div className="upload-text">엑셀 파일을 드래그하거나 클릭하여 업로드</div>
      <div className="upload-sub">재고리스트 / 출하리스트 / 출고리스트 (.xlsx)</div>
      <div className="upload-files">
        {uploadedFiles.length === 0 && (
          <span style={{ color: "#94a3b8", fontSize: "11px" }}>
            업로드된 파일이 없습니다
          </span>
        )}
        {uploadedFiles.map((f) => (
          <span
            key={f.id}
            className={`upload-chip${f.status === "error" ? " error" : ""}`}
            onClick={(e) => e.stopPropagation()}
          >
            {f.status === "error"
              ? `⚠ ${f.name} (인식 실패)`
              : `✅ ${f.name} → ${FILE_LABEL[f.type]} (${f.count}건)`}
            <span className="chip-remove" onClick={() => onRemove(f.id)}>
              ✕
            </span>
          </span>
        ))}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xls"
        multiple
        style={{ display: "none" }}
        onChange={handleChange}
      />
    </div>
  );
}
