import { CheckCircle, XCircle } from "lucide-react";
import { DEFECT_CLASSES } from "../data/waferPatterns.js";

export default function PatternBadge({ topClass, topColor, isFail }) {
  const cls = DEFECT_CLASSES.find((c) => c.key === topClass);

  return (
    <div className="flex items-center gap-6 py-2">
      <div className="w-24 h-24 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${topColor}1A` }}>
        {isFail ? <XCircle size={40} style={{ color: topColor }} /> : <CheckCircle size={40} style={{ color: topColor }} />}
      </div>
      <div>
        <span className="inline-block px-3 py-1 rounded-full text-[13px] font-semibold" style={{ backgroundColor: `${topColor}1A`, color: topColor }}>
          {topClass}
        </span>
        <p className="text-gray-500 text-[13px] mt-3 leading-relaxed max-w-sm">{cls?.description}</p>
      </div>
    </div>
  );
}
